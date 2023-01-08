# -*- coding: utf-8 -*-

from odoo import api, fields, models
class StockMove(models.Model):
    _inherit = "stock.move"

    currency_id = fields.Many2one('res.currency', related="sale_line_id.order_id.currency_id")
    price_subtotal = fields.Monetary('Subtotal', related="sale_line_id.price_subtotal")
StockMove()