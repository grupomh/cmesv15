# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError



class ResPartner(models.Model):
    _inherit = "res.partner"

    is_retroactive_invoice = fields.Boolean('Aplicar facturacion tardia', required=False, copy=False, default=False)
ResPartner()

class ProductProduct(models.Model):
    _inherit = "product.product"

    cupons_ids = fields.One2many('coupon.program', 'reward_product_id', 'Promociones', ondelete="cascade")
    is_promotion = fields.Boolean('Producto promocionable', compute="_compute_is_promotion", store=False)

    @api.depends('cupons_ids')
    def _compute_is_promotion(self):
        for rec in self:
            is_promotion = False
            if rec.cupons_ids:
                is_promotion = True
            rec.update({
                'is_promotion': is_promotion,
            })


ProductProduct()