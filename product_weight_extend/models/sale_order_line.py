from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    weight = fields.Float(compute='weight_total', readonly=True, string="Peso Total")

    def weight_total(self):
        for data in self:
            data.weight = data.product_id.weight * data.product_uom_qty


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _margin_percentage(self):
        for data in self:
            if data.margin > 0 and data.amount_total > 0:
                data.margin_percentage = (data.margin / data.amount_total) * 100
            else:
                data.margin_percentage = 0

    margin_percentage = fields.Float(compute='_margin_percentage', string="Porcentaje margen")