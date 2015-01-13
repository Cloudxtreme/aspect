#!/home/diamond/venv/billing/bin/python
# -*- coding: utf-8 -*-
import sys, os, re
sys.path.append("/home/diamond/venv/dev/aspekt")
os.environ['DJANGO_SETTINGS_MODULE'] = 'aspekt.settings'
import MySQLdb
from users.models import Abonent
from contacts.models import Contact

def importcontacts1cdb():
  db = MySQLdb.connect(host="10.255.0.10", user="d.sitnikov", 
                         passwd="Aa12345", db="radius")
  db.set_character_set("cp1251")
  cursor = db.cursor()
  sql = """SELECT SubscriberID, Address,Contacts,ContactPerson FROM Subscribers WHERE SubscriberID LIKE '50______' AND tarif > 1;"""
  cursor.execute(sql)
  data = cursor.fetchall()
  cList = []
  for rec in data:
    uid, addr, cnt, prs = rec
    try:
      abonent = Abonent.objects.get(contract=uid)
    except:
      pass
    else:
      r_email = re.compile(r'(\b[\w.]+@+[\w.]+.+[\w.]\b)')
      emails = r_email.findall(cnt)

      if emails:
        email = emails[0]
      else:
        email = ''

      if prs == '':
        person = abonent.title
      else:
        person = prs.decode('cp1251')

      if addr:
        address = addr.decode('cp1251')

      cList += [Contact(
                        abonent=abonent,
                        surname=person,
                        address=address,
                        phone=cnt.decode('cp1251'),
                        email=email,
                  )]
      # print '(%s| %s | %s | %s)' % (uid, addr.decode('cp1251'), contact.decode('cp1251'), person.decode('cp1251'))  
  Contact.objects.bulk_create(cList)
  # print cList
  db.close()

importcontacts1cdb()