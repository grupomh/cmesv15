# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = "mrp.production"

        #Relation Fields
    bom_id = fields.Many2one('mrp.bom', 'Bom materials',check_company=True)

    cat_process = fields.Selection(string='Proceso',related='bom_id.cat_process',store=True,readonly=True)

    turn = fields.Selection([
        ('Diurno', 'Diurno'),
        ('Nocturno', 'Nocturno')],string='Turno', required=True, copy=False)

    quality_control_lines = fields.One2many('quality.control.points','production_id',string="-detalles control de calidad",required=False,index=True,readonly=False,copy=False)

    
    

MrpProduction()