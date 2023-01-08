# -*- coding: utf-8 -*-

from email.policy import default
from odoo import api, fields, models, _

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    qty_total_dif=fields.Float('Cantidad faltante', copy=False, readonly=True, compute='_dif_qty_produced')


    finished_move_line_ids2 = fields.One2many(
        'stock.move.line', compute='_compute_lines2', inverse='_inverse_lines', string="Finished Product"
        )

    @api.depends('move_finished_ids.move_line_ids')
    def _compute_lines2(self):
        for production in self:
            production.finished_move_line_ids2 = production.move_finished_ids.mapped('move_line_ids')
    

    @api.depends("qty_produced") #logica
    def _dif_qty_produced(self):
        for rec in self:
            rec.qty_total_dif = rec.product_qty - rec.qty_produced

   