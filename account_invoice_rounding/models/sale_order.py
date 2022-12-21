# -*- coding: utf-8 -*-
###########################################################
# Author: Xetechs, S.A.
# Support: Luis Aquino -> laquino@xetechs.com
# Website: https://www.xetechs.com
# See LICENSE file for full copyright and licensing details.
###########################################################

from odoo import api, fields, models, tools
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    amount_rouding = fields.Float('Redondeo', digits='Product Price', required=False, default=0.00)
    apply_rouding = fields.Boolean('Aplicar redondeo', compute="_compute_apply_rouding")

    @api.depends('product_id')
    def _compute_apply_rouding(self):
        user = self.env.user
        for rec in self:
            flag = user.has_group('account_invoice_rounding.group_apply_rouding')
            rec.update({
                'apply_rouding': flag or False,
            })

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'amount_rouding')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'] - line.amount_rouding,
                'price_subtotal': taxes['total_excluded'] - line.amount_rouding,
            })

    def _prepare_invoice_line(self):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        res.update({
            'amount_rouding': self.amount_rouding,
        })
        return res
SaleOrderLine()