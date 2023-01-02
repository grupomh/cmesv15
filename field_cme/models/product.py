# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_repr
from odoo.exceptions import ValidationError
from collections import defaultdict



class ProductProduct(models.Model):
    _inherit = 'product.product'


    def write(self, vals):
        if self.env.context.get('import_file') and not self.env.context.get('import_standard_price'):
            if 'standard_price' in vals:
                for product in self:
                    counterpart_account_id = product.property_account_expense_id.id or product.categ_id.property_account_expense_categ_id.id
                    #product.with_context(import_standard_price=True)._change_standard_price(vals['standard_price'], counterpart_account_id)
        res = super(ProductProduct, self).write(vals)
        return res

ProductProduct()