import re, subprocess,shlex
# from devices.models import Config

def dec2ip(ip):
     return '.'.join([str((ip >> 8 * i) & 255) for i in range(3, -1, -1)])

def ip2dec(ip):
    return sum([int(q) << i * 8 for i, q in enumerate(reversed(ip.split(".")))])

# def calcnet(net, mask):
#     mask1 = mask + 1
#     net1 = dec2ip(ip2dec(net)+pow(2,31-mask))
#     if mask >= 29:
#         return (net,mask1),(net1,mask1)
#     return ((net,mask1),(net1,mask1), calcnet(net,mask1),calcnet(net1,mask1))

def get_ubnt_cfg(ip):
    line = """sshpass -p 'yfxfkj' rsh 
             -o ConnectTimeout=3 
             -o StrictHostKeyChecking=no 
             -o UserKnownHostsFile=/dev/null 
             hflbcn@%s 
             'cat /tmp/system.cfg'""" % ip
    args = shlex.split(line)
    proc = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    proc.wait()
    config = proc.stdout.read()
    err = proc.stderr.read()
    result = True if err.find('Connection timed out') ==-1 else False
    return config, result

def get_freq_ubnt(config):
    frq_list = 'wireless.1.scan_list.channels=(\d{4})(,\d{4})*'
    frq_str = 'radio.1.freq=(\d{4})'
    if not re.findall(frq_str,config) and re.findall(frq_list,config):
        freqs = [x.strip(',') for x in re.findall(frq_list,config)[0] if x]
    else:
        freqs = re.findall(frq_str,config)
    return freqs

def get_width_ubnt(config):
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
