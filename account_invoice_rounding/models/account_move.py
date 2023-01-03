# -*- coding: utf-8 -*-
###########################################################
# Author: Xetechs, S.A.
# Support: Luis Aquino -> laquino@xetechs.com
# Website: https://www.xetechs.com
# See LICENSE file for full copyright and licensing details.
###########################################################

from odoo import api, fields, models, tools
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

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
    def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None, partner=None, taxes=None, move_type=None):
        res = super(AccountMoveLine, self)._get_price_total_and_subtotal(price_unit, quantity, discount, currency, product, partner, taxes, move_type)
        if res:
            res['price_total'] -= self.amount_rouding
            res['price_subtotal'] -= self.amount_rouding
        return res
    
    
    @api.onchange('amount_rouding')
    def _onchange_rounding(self):
        self.price_total -= self.amount_rouding
        self.price_subtotal -= self.amount_rouding
    
    
AccountMoveLine()