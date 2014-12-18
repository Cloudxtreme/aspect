#!/home/diamond/venv/billing/bin/python
# -*- coding: utf-8 -*- 
# Скрипт выдает список IP-адресов, разрешенных к доступу в интернет
import os
import sys

sys.path.append("/home/diamond/venv/billing/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'
from vlans.models import Network, IPAddr

# arg = sys.argv[1] if len (sys.argv) == 2 else False

def dec2ip(ip):
     return '.'.join([str((ip >> 8 * i) & 255) for i in range(3, -1, -1)])
        
def ip2dec(ip):
    return sum([int(q) << i * 8 for i, q in enumerate(reversed(ip.split(".")))])

config = ''
config += 'authoritative;\n'
config += 'default-lease-time 600;\n'
config += 'max-lease-time 7200;\n'
config += '\n'
config += 'subnet 192.168.64.0 netmask 255.255.255.0 {\n'
config += '        range 192.168.64.253 192.168.64.254;\n'
config += '        deny unknown-clients;\n'
config += '}\n'

f = open('dhcpd.conf', 'w')

for net in Network.objects.filter(net_type='UN',in_dhcpd=True):
    mask = dec2ip(4294967295 - pow(2,32-net.mask)+1)
    config += '\n'
    config += 'subnet %s netmask %s {\n' % (net.ip,mask)
    config += '        range %s %s;\n' % (dec2ip(ip2dec(net.ip)+2),dec2ip(ip2dec(net.ip)+pow(2,32-net.mask)-2))
    config += '        default-lease-time 259200;\n'
    config += '        max-lease-time 259200;\n'
    config += '        option routers %s;\n' % dec2ip(ip2dec(net.ip)+1)
    config += '        option ip-forwarding off;\n'
    config += '        option broadcast-address %s;\n' % dec2ip(ip2dec(net.ip)+pow(2,32-net.mask)-1)
    config += '        option subnet-mask %s;\n' % mask
    config += '        option domain-name-servers 194.190.13.246, 194.190.13.158;\n'
    config += '}\n'

    for ipaddr in IPAddr.objects.filter(net__pk=net.pk):
        try:
            if ipaddr.interface.mac:
                ip = ipaddr.ip
                mac = ipaddr.interface.mac
                number = ipaddr.interface.id
            else:
                number = 0    
        except:
            number = 0
        else:
            if number:
                config += '\n'
                config += 'host %s {\n' % (number)
                config += '  hardware ethernet %s;\n' % (mac)
                config += '  ifixed-address %s;\n'  % (ip)
                config += '}\n'

for line in config:
    # print line
    f.write(line)

f.close()