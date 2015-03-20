# -*- coding: utf-8 -*-
from users.models import Abonent

# Поиск по разным полям абонента

def abonent_filter(data):
    abonent_list = Abonent.objects.filter(contract__icontains=data)|\
        Abonent.objects.filter(title__icontains=data)|\
        Abonent.objects.filter(detail__title__icontains=data)|\
        Abonent.objects.filter(tag__title__icontains=data)|\
        Abonent.objects.filter(service__location__address__icontains=data)|\
        Abonent.objects.filter(contact__first_name__icontains=data)|\
        Abonent.objects.filter(contact__surname__icontains=data)|\
        Abonent.objects.filter(contact__mobile__icontains=data)
    return abonent_list.distinct()      