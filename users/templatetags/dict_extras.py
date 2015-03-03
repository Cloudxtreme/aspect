# -*- coding: utf-8 -*-
from django import template
from pays.models import PromisedPays
import notice.smsru as smsru
import re

register = template.Library()

@register.filter
def div( value, arg ):
    '''
    Divides the value; argument is the divisor.
    Returns empty string on any error.
    '''
    try:
        value = float( value )
        arg = float( arg )
        if arg: return value / arg
    except: pass
    return ''

@register.filter
def sms_status(value):
    return smsru.SEND_STATUS.get(int(value), "Unknown status")

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
    
@register.filter    
def freq_list(value):
    result = ''
    for item in re.findall('\d{4}',value):
        result += '%s Mhz' % item
    return result

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

@register.filter    
def get_shift_by_mask(value):
    result = value - 17 if value < 25 else value - 25
    return result

@register.filter    
def pow_2(value):
    return pow(2,32-value)-2

@register.filter
def get_colored_balance(value):
    if value.__class__.__name__ == 'Payment':
        return u'success'
    else:
        return u'danger'

@register.filter
def get_sign(value):
    if value.__class__.__name__ == 'Payment':
        return u'+ %0.2f' % value.summ
    else:
        return u'- %0.2f' % value.summ
        
# @register.filter
# def get_promised(abonent_id):
# 	return PromisedPays.objects.filter(abonent__pk=abonent_id, pay_onaccount = True).count()