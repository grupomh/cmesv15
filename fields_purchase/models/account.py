# -*- coding: utf-8 -*-
from odoo import api,fields, models, _

class Account(models.Model):
    _inherit="account.move"

    narration1=fields.Html("Texto", required=False, readonly=True,copy=False,related='purchase_id.notes')



    
Account()