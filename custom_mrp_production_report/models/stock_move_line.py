# -*- coding: utf-8 -*-

from email.policy import default
from odoo import api, fields, models, _

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    print_check= fields.Boolean('Imprimir', copy=False, required=False, default=False)
    control_check = fields.Boolean('Recibido', copy=False, required=False)

    #def set_access_for_check(self):
        #self.view_check = self.env['res.users'].has_group('custom_mrp_production_report.group_check_tandas_manager')

    #view_check = fields.Boolean(compute='set_access_for_check', copy=False, required=False)
    
