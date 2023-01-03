# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

     
class ResCompany(models.Model):
    _inherit = 'res.company'
    
    commission_based_on_so = fields.Boolean("Comisiones sobre Pedidos de Ventas", default=False)
    commission_based_on_invoice = fields.Boolean("Comisiones sobre Facturas Valdidas", default=False)
    commission_based_on_payment = fields.Boolean("Comisiones sobre Pagos de Facturas", default=False)

ResCompany()

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    commission_based_on_so = fields.Boolean("Comisiones sobre Pedidos de Ventas", related='company_id.commission_based_on_so',readonly=False)
    
    commission_based_on_invoice = fields.Boolean("Comisiones sobre Facturas Valdidas", related='company_id.commission_based_on_invoice',readonly=False)
    
    commission_based_on_payment = fields.Boolean("Comisiones sobre Pagos de Facturas", related='company_id.commission_based_on_payment',readonly=False)
    