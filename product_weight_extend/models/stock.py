from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move'

    weight = fields.Float(compute='weight_total', readonly=True, string="Peso Total")

    def weight_total(self):
        for data in self:
            data.weight = data.product_id.weight * data.product_uom_qty
