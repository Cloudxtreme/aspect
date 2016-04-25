#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import requests, os
import codecs
import datetime
import syslog
from xml.dom.minidom import *
from Queue import Queue
from threading import Thread

DUMP_FILE = 'dump.xml'
RESULT_FILE = 'report.txt'
BLOCK_SITE = 'http://194.190.13.158/block/'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_DUMP = os.path.join(BASE_DIR, DUMP_FILE)
result_list = []
urls = []
unreachable = []
blocked = []
header = ''

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Проверка URL с помощью requests
def url_check_req(url):
    try:
        response = requests.head(url, verify=False,timeout=5)
    # except requests.exceptions.ConnectionError:
    except:
        # print url
        result = None
    else:
        if response.status_code == 404:
            result = None
        else:
            result = response.headers.get('location', default=url)

    return result

# Проверка URL с помощью urllib2
def url_check_lib(url):
    ret = urllib2.urlopen(url)
    return ret.url

# Очередь на проверку
def get_state(queue):
    for url in iter(queue.get, None):
        result_url = url_check_req(url)
        if result_url is None:
            unreachable.append(url)
            print bcolors.WARNING + u"[Недоступен] " + bcolors.ENDC + url
        elif BLOCK_SITE not in result_url:
            pair = (url,result_url)
            result_list.append(pair)
            print bcolors.FAIL + u"[Доступен] " + bcolors.ENDC + url
            # print pair
        else:
            blocked.append(url)
            print bcolors.OKGREEN + u"[Заблокирован] " + bcolors.ENDC + url
        # print "Заблокированных: %s, Доступных: %s, недоступных: %s, всего: %s" % (len(blocked),len(result_list),len(unreachable), len(urls))
            
        # if result_url not in [BLOCK_SITE,None]:
            # pair = (url,result_url)
            # result_list.append(pair)
            # print len(result_list)
            # print pair

# Многопоточный менеджер
def mt_url_check(url_set):
    queue = Queue()
    threads = [Thread(target=get_state, args=(queue,)) for _ in range(20)]
    for t in threads:
        t.daemon = True
        t.start()
    
    # Place work in queue
    for url in url_set: queue.put(url)
    # Put sentinel to signal the end
    for _ in threads: queue.put(None)
    # Wait for completion
    for t in threads: t.join()
    # return result_list

def print_and_return(line):
    print line
    return line

# Получаем из дампа список запрещенных URL
header += print_and_return(u"Загружаем файл %s\n" % PATH_DUMP)

xml = parse(PATH_DUMP)

url_nodes = xml.getElementsByTagName('url')
for node in url_nodes:
    url = node.childNodes[0].nodeValue
    urls.append(url)

header += print_and_return(u"Прочитано %s записей\n" % (len(urls)))

start = datetime.datetime.now()

header += print_and_return(u"Начало проверки в %s\n" % start)

mt_url_check(urls)
finish = datetime.datetime.now()

header += print_and_return(u"Проверка закончена за %s\n" % (finish-start))
header += print_and_return(u"Доступно %s сайтов\n" % (len(result_list)))
header += print_and_return(u"Заблокировано %s сайтов\n" % (len(blocked)))
header += print_and_return(u"Недоступно %s сайтов\n" % (len(unreachable)))

syslog.syslog(syslog.LOG_INFO, header)

print u"Запись результатов в %s" % RESULT_FILE

alert_file = codecs.open(RESULT_FILE, encoding='utf-8', mode='w')

for line in header:
    alert_file.write(line)

alert_file.write('===========================================\n')

for item in result_list:
    alert_file.write(item[0])
    alert_file.write(" => ")
    alert_file.write(item[1])
    alert_file.write("\n")
alert_file.close()