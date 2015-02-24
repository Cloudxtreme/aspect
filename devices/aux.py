# -*- coding: utf-8 -*-
import re, subprocess,shlex,netsnmp, math
from django.conf import settings

def dec2ip(ip):
     return '.'.join([str((ip >> 8 * i) & 255) for i in range(3, -1, -1)])

def ip2dec(ip):
    return sum([int(q) << i * 8 for i, q in enumerate(reversed(ip.split(".")))])

def run_snmp(oid,ip,community=settings.SNMP_COMMUNITY):
    result = netsnmp.snmpget(netsnmp.Varbind(oid), Version = 1, DestHost = ip, Community=community)[0]
    return result if result else netsnmp.snmpget(netsnmp.Varbind(oid), Version = 1, DestHost = ip, Community=settings.SNMP_SNR_COMMUNITY)[0]

# Depricated --> Нужно убирать и переписывать под netsnmp
def run_command(line):
    args = shlex.split(line)
    proc = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    proc.wait()
    return proc.stdout.read(), proc.stderr.read()
# <--

def azimuth_distance(start,end):
    #pi - число pi, rad - радиус сферы (Земли)
    rad = 6372795

    llat1,llong1 = start.split(',')
    llat2,llong2 = end.split(',')

    #координаты двух точек
    # llat1 = 77.1539
    # llong1 = -120.398

    # llat2 = 77.1804
    # llong2 = 129.55

    #в радианах
    lat1 = float(llat1)*math.pi/180.
    lat2 = float(llat2)*math.pi/180.
    long1 = float(llong1)*math.pi/180.
    long2 = float(llong2)*math.pi/180.

    #косинусы и синусы широт и разницы долгот
    cl1 = math.cos(lat1)
    cl2 = math.cos(lat2)
    sl1 = math.sin(lat1)
    sl2 = math.sin(lat2)
    delta = long2 - long1
    cdelta = math.cos(delta)
    sdelta = math.sin(delta)

    #вычисления длины большого круга
    y = math.sqrt(math.pow(cl2*sdelta,2)+math.pow(cl1*sl2-sl1*cl2*cdelta,2))
    x = sl1*sl2+cl1*cl2*cdelta
    ad = math.atan2(y,x)
    dist = ad*rad

    #вычисление начального азимута
    x = (cl1*sl2) - (sl1*cl2*cdelta)
    y = sdelta*cl2
    z = math.degrees(math.atan(-y/x))

    if (x < 0):
        z = z+180.

    z2 = (z+180.) % 360. - 180.
    z2 = - math.radians(z2)
    anglerad2 = z2 - ((2*math.pi)*math.floor((z2/(2*math.pi))) )
    angledeg = (anglerad2*180.)/math.pi

    # print 'Distance >> %.0f' % dist, ' [meters]'
    # print 'Initial bearing >> ', angledeg, '[degrees]'
    return angledeg,dist

# Опеределяем тип устройства
def get_dev_os(ip):
    oid = 'iso.3.6.1.2.1.1.1.0'
    return run_snmp(oid,ip)

# Опеределяем имя устройства
def get_dev_name(ip):
    oid = 'iso.3.6.1.2.1.1.5.0'
    return run_snmp(oid,ip)

# Опеределяем MAC устройства
def get_ubnt_macaddr(ip):
    line = """snmpwalk -v1 -c %s %s 1.2.840.10036.2.1.1.1""" % (settings.SNMP_COMMUNITY,ip)
    mac_str = 'iso.2.840.10036.2.1.1.1.\d = STRING: "(.*)"'
    result,err = run_command(line)
    mac = re.findall(mac_str,result)
    return mac[0].replace(':','') if mac else ''

# Определяем вольтаж на пинговалке
def get_snr_voltage(ip):
    oid = 'iso.3.6.1.4.1.40418.2.2.4.2.0'
    voltage = run_snmp(oid,ip,settings.SNMP_SNR_COMMUNITY)
    # print voltage
    return float(voltage)/100 if voltage else 0    
    
# Определяем наличие внешнего питания
def get_snr_supply(ip):
    oid = 'iso.3.6.1.4.1.40418.2.2.3.6.0'
    supply = run_snmp(oid,ip,settings.SNMP_SNR_COMMUNITY)    
    return True if supply == '2' else False

# Опеределяем модель устройства
def get_ubnt_model(ip):
    line = """snmpwalk -v1 -c %s %s 1.2.840.10036.3.1.2.1""" % (settings.SNMP_COMMUNITY,ip)
    vendor_str = 'iso.2.840.10036.3.1.2.1.2.\d = STRING: "(.*)"'
    model_str = 'iso.2.840.10036.3.1.2.1.3.\d = STRING: "(.*)"'
    result,err = run_command(line)
    vendor = re.findall(vendor_str,result)
    model = re.findall(model_str,result)
    return model[0] if model else ''

# Получаем MAC Access Point'a
def get_ubnt_apmac(ip):
    line = """snmpwalk -v1 -c %s %s 1.3.6.1.4.1.14988.1.1.1.1.1.6""" % (settings.SNMP_COMMUNITY,ip)
    oid_template = 'iso.3.6.1.4.1.14988.1.1.1.1.1.6.\d = Hex-STRING: (\w{2} \w{2} \w{2} \w{2} \w{2} \w{2})'
    result,err = run_command(line)
    mac = re.findall(oid_template,result)    
    return mac[0].replace(' ','') if mac else ''

# Получаем MAC'и подключенных клиентов
def get_ubnt_clients(ip):
    line = """snmpwalk -v1 -c %s %s 1.3.6.1.4.1.14988.1.1.1""" % (settings.SNMP_COMMUNITY,ip)
    oid_template = 'iso.3.6.1.4.1.14988.1.1.1.2.1.3.(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})'
    result,err = run_command(line)
    macs = []
    for mac in re.findall(oid_template,result):
        macs.append(''.join(map(lambda x: hex(int(x)).split('x')[1].rjust(2,'0'), mac.split('.'))))

    return macs

# Получаем конфиг клиента
def get_ubnt_cfg(ip):
    line = """sshpass -p 'yfxfkj' rsh 
             -o ConnectTimeout=3 
             -o StrictHostKeyChecking=no 
             -o UserKnownHostsFile=/dev/null 
             hflbcn@%s 
             'cat /tmp/system.cfg'""" % ip
    config,err = run_command(line)
    return config, True if err.find('Connection timed out') ==-1 else False

# Определяем AP или Station
def get_ubnt_ap(config):
    ap_str = 'radio.1.mode=master'
    return bool(re.findall(ap_str,config))

# Определяем частоту антенны
def get_ubnt_freq(config):
    frq_list = 'wireless.1.scan_list.channels=(\d{4})(,\d{4})*'
    frq_str = 'radio.1.freq=(\d{4})'
    if not re.findall(frq_str,config) and re.findall(frq_list,config):
        freqs = [x.strip(',') for x in re.findall(frq_list,config)[0] if x]
    else:
        freqs = re.findall(frq_str,config)
    return freqs

# Определяем полосу
def get_ubnt_width(config):
    d = {('0','2',False):'10',
        ('0','1', True):'40',
        ('30','1',False):'30',
        ('25','1',False):'25',
        ('3','4',False):'3',
        ('0','4',False):'5',
        ('2','2',False):'8',
        ('0','1',False):'20',
    }
    clksel_str = 'radio.1.clksel=(\d?)'
    chanbw_str = 'radio.1.chanbw=(\d{1,2})'
    clksel = re.findall(clksel_str,config)[0]
    chanbw = re.findall(chanbw_str,config)[0]
    width = d[chanbw,clksel,bool(re.findall('radio.1.ieee_mode=11naht40',config))]
    return width
