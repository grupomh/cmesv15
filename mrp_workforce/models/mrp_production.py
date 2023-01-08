# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = "mrp.production"

        #Relation Fields

    mrp_workforce = fields.One2many('mrp.workforce','production_id',string="Mano de obra",required=False,index=True,readonly=False,copy=False)


    hours_mrp_wokrforce = fields.Float(string="Horas reportadas", compute="_compute_workforce_count")

    
    @api.depends('mrp_workforce.hours_report')
    def _compute_workforce_count(self):
        for rec in self:
            rec.update({
                'hours_mrp_wokrforce': abs(sum([x.hours_report for x in rec.mrp_workforce])),
            })

MrpProduction()