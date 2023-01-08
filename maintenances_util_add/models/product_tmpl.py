# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    templates_id = fields.Many2one('product.template', string='Product',related='product_id.product_tmpl_id')

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    purchase_lines_ids = fields.One2many('purchase.order.line','templates_id','purchase lines')

    sum_average_purchase = fields.Float(string="Costo unitario compras", compute="_compute_purchase_lines_aver")

    @api.depends('purchase_lines_ids.price_unit')
    def _compute_purchase_lines_aver(self):
        for rec in self:
            if len(rec.purchase_lines_ids.filtered(lambda x: x.state == 'purchase')) >= 1:
                rec.update({
                    'sum_average_purchase': abs(sum([x.price_unit for x in rec.purchase_lines_ids.filtered(lambda x: x.state == 'purchase')]) / len(rec.purchase_lines_ids.filtered(lambda x: x.state == 'purchase'))),
                })
            else:
                rec.update({'sum_average_purchase': 0.00 })
