#!/home/diamond/venv/billing/bin/python
# -*- coding: utf-8 -*- 
# Скрипт выдает список IP-адресов, разрешенных к доступу в интернет
import os
import sys

sys.path.append("/home/diamond/venv/billing/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'
from users.models import Service, Pipe

arg = sys.argv[1] if len (sys.argv) == 2 else False

f = open('list_ip.txt', 'w')

if arg:
    pipes_script = open('pipes.sh', 'w')
    counter = 10
    for pipe in Pipe.objects.all():
        lines = ''
        lines += 'ipfw pipe %s config bw %sKbit/s mask dst-ip 0x000000ff\n' % (pipe.id*2, pipe.speed_out)
        lines += 'ipfw pipe %s config bw %sKbit/s mask src-ip 0x000000ff\n' % (pipe.id*2+1, pipe.speed_in)
        lines += 'ipfw add %s pipe %s ip from any to table\(%s\) out\n' % (counter, pipe.id*2, pipe.id)
        lines += 'ipfw add %s pipe %s ip from table\(%s\) to any in\n'  % (counter+1, pipe.id*2+1, pipe.id)            
        counter += 2
        for line in lines:
            pipes_script.write(line) 


for srv in Service.objects_active.all().exclude(adm_status='2')|Service.objects.filter(adm_status='1'):
    for iface in srv.ifaces.all():
        if arg:
            pipe_id = srv.plan.speed.id if not srv.speed else srv.speed.id
            line = 'ipfw table %s add %s\n' % (pipe_id,iface.ip.ip)
            pipes_script.write(line) 
        else:
            f.write(iface.ip.ip + '\n')

if arg:
    pipes_script.close()            
    
f.close()