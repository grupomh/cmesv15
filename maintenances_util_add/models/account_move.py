# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit= "account.move"

    maintenance_request_id=fields.Many2one('maintenance.request', 'Peticion de mantenimiento',  required=False, copy=False, readonly=False)
    maintenance_equipment_id=fields.Many2one('maintenance.equipment',"Equipo mantenimiento",related='maintenance_request_id.equipment_id', required=False, copy=False, readonly=True)
    
AccountMove()