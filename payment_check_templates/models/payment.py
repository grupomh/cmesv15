# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import Warning

class AccountPayment(models.Model):
    _inherit = "account.payment"

    check_type = fields.Selection([
        ('no_negociable', '*NO NEGOCIABLE'),
        ('negociable', '*NEGOCIABLE*'),
    ], string="Tipo de cheque", default='negociable')
    
AccountPayment()