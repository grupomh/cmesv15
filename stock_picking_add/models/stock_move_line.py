# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class StockMoveLine(models.Model):
    _inherit= "stock.move.line"

    price_envio=fields.Float('precio unitario', related='move_id.sale_line_id.price_unit')
    price_env_sub=fields.Float(compute='_compute_amount_price_env')

    @api.depends('price_envio','qty_done')
    def _compute_amount_price_env(self):
        for line in self:
            line.price_env_sub = line.price_envio * line.qty_done if line.price_envio else 0.0
        

    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot/Serial Number',
        domain="[('quant_ids.location_id', '=', location_id),('company_id', '=', company_id),'&',('product_id', '=', product_id),('product_qty', '>', 0.01)]", check_company=True)