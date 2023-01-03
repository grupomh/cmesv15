# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    invisible = fields.Boolean('Ocultar transacciones', default=False)
    type=fields.Selection('type ', related='move_type')
AccountInvoice()