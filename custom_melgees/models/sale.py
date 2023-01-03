# -*- coding: utf-8 -*-

from odoo import api, fields, models
class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoice_numbers = fields.Char('Facturas', compute="_compute_invoice_numbers", store = True)

    @api.depends('invoice_ids')
    def _compute_invoice_numbers(self):
        invoice_numbers = ""
        for rec in self:
            invoice_numbers = ""
            if rec.invoice_ids:
                for inv in rec.invoice_ids:
                    invoice_numbers += str(inv.name) if inv.name else ""
            rec.update({
                'invoice_numbers': invoice_numbers or "",
            })
SaleOrder()

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_authorize = fields.Boolean('Cambiar precio', compute="_get_authorize")
    user_id = fields.Many2one(
        'res.users', related="order_id.user_id")

    @api.depends('product_id', 'user_id')
    def _get_authorize(self):
        user = self.env.user
        for rec in self:
            flag = user.has_group('custom_melgees.group_update_sale_prices')
            rec.update({
                'is_authorize': flag or False,
            })
SaleOrderLine()