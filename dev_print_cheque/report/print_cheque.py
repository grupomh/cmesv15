# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

from odoo import models, fields, api
from num2words import num2words
from .numero_a_texto import Numero_a_Texto
import datetime
import locale


class print_check(models.AbstractModel): 
    _name = 'report.dev_print_cheque.report_print_cheque'

    def get_date(self, date, obj):
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8') # Configuration for language Spanish
        date_str = str(date)
        date_split = date_str.split('-')
        date_split = [int(number) for number in date_split]
        date_to_datetime = datetime.datetime(date_split[0], date_split[1], date_split[2])
        date_format = "%d %B %Y" if obj.date_formate == 'dd_mm' else "%B %d %Y"
        if date:
            date = date_to_datetime.strftime(date_format)
            return date
        return ''

    def get_partner_name(self,obj,p_text):
        return obj.partner_id


    def amount_word(self, obj):
        # amt_word = obj.currency_id.with_context(lang=obj.partner_id.lang or 'es_ES').amount_to_text(obj.amount)
        amt_word =Numero_a_Texto(obj.amount)
        lst = amt_word.split(' ')
        lst_len = len(lst)
        first_line = ''
        second_line = ''
        for l in range(0, lst_len):
            if lst[l] != 'euro':
                if obj.cheque_formate_id.word_in_f_line >= l:
                    if first_line:
                        first_line = first_line + ' ' + lst[l]
                    else:
                        first_line = lst[l]
                else:
                    if second_line:
                        second_line = second_line + ' ' + lst[l]
                    else:
                        second_line = lst[l]

        if obj.cheque_formate_id.is_star_word:
            first_line = '***' + first_line
            if second_line:
                second_line += '***'
            else:
                first_line=first_line+'***'
        first_line = first_line.replace(",", "")
        second_line = second_line.replace(",", "")

        return [first_line, second_line]

    def _get_report_values(self, docids, data=None):
        docs = self.env['account.payment'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'account.payment',
            'docs': docs,
#            'data': data,
            'get_date': self.get_date,
            'get_partner_name':self.get_partner_name,
            'amount_word':self.amount_word,
        }


class print_cheque_wizard(models.AbstractModel):
    _name = 'report.dev_print_cheque.cheque_report'

    def get_date(self, date):
        date = date.split('-')
        return date

    def amount_word(self, obj):
        # amt_word = obj.currency_id.with_context(lang=obj.partner_id.lang or 'es_ES').amount_to_text(obj.amount)
        amt_word =Numero_a_Texto(obj.amount)
        lst = amt_word.split(' ')
        lst_len = len(lst)
        first_line = ''
        second_line = ''
        for l in range(0, lst_len):
            if lst[l] != 'euro':
                if obj.cheque_formate_id.word_in_f_line >= l:
                    if first_line:
                        first_line = first_line + ' ' + lst[l]
                    else:
                        first_line = lst[l]
                else:
                    if second_line:
                        second_line = second_line + ' ' + lst[l]
                    else:
                        second_line = lst[l]

        if obj.cheque_formate_id.is_star_word:
            first_line = '***' + first_line
            if second_line:
                second_line += '***'
            else:
                first_line=first_line+'***'

        first_line = first_line.replace(",", "")
        second_line = second_line.replace(",", "")

        return [first_line, second_line]

    def get_report_values(self, docids, data=None):
        docs = self.env['cheque.wizard'].browse(data['form'])
        return {
            'doc_ids': docs.ids,
            'doc_model': 'cheque.wizard',
            'docs': docs,
            'get_date': self.get_date,
            'amount_word':self.amount_word,
        }
            
    
        



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
