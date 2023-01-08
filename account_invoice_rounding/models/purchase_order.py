# -*- coding: utf-8 -*-
###########################################################
# Author: Xetechs, S.A.
# Support: Luis Aquino -> laquino@xetechs.com
# Website: https://www.xetechs.com
# See LICENSE file for full copyright and licensing details.
###########################################################

from odoo import api, fields, models, tools
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

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

    # @api.depends('product_qty', 'price_unit', 'taxes_id', 'amount_rouding')
    # def _compute_amount(self):
    #     for line in self:
    #         vals = line._prepare_compute_all_values()
    #         taxes = line.taxes_id.compute_all(
    #             vals['price_unit'],
    #             vals['currency_id'],
    #             vals['product_qty'],
    #             vals['product'],
    #             vals['partner'])
    #         line.update({
    #             'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
    #             'price_total': taxes['total_included'] - line.amount_rouding,
    #             'price_subtotal': taxes['total_excluded'] - line.amount_rouding,
    #         })
    
    def _prepare_account_move_line(self, move):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move)
        res.update({
            'amount_rouding': self.amount_rouding or 0.00,
        })
        return res
PurchaseOrderLine()