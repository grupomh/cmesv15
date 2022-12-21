# -*- coding: utf-8 -*-

from odoo import api, fields, models
from .numero_a_texto import Numero_a_Texto

from num2words import num2words


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _get_num2words(self, amount):
        return Numero_a_Texto(amount)

    def _format_date(self, date, format):
        day = date.strftime('%d')
        year = date.strftime('%Y')
        months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre',
                  'Noviembre', 'Diciembre']
        month = months[(date.month)-1]
        if format == 'day':
            return day
        elif format == 'month':
            return month
        elif format == 'year':
            return year
