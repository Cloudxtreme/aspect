# -*- coding: utf-8 -*-
from django import template
from pays.models import PromisedPays

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
    
@register.filter    
def get_color(value):
    dict = {'A': 'success', 'S' : 'warning', 'N' : 'danger', 'D' : 'info' }
    return dict.get(value)

@register.filter    
def get_hidden(value):
    dict = {'D': 'display:none'}
    return dict.get(value, '')

@register.filter    
def get_day(value):
    dict = {1: 'Понедельник', 2 : 'Вторник', 3 : 'Среда', 4 : 'Четверг', 5 : 'Пятница', 6 : 'Суббота', 7 : 'Воскресенье' }
    return dict.get(value)


# @register.filter
# def get_promised(abonent_id):
# 	return PromisedPays.objects.filter(abonent__pk=abonent_id, pay_onaccount = True).count()