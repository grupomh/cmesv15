# -*- coding: utf-8 -*-
###########################################################
# Author: Xetechs, S.A.
# Support: Luis Aquino -> laquino@xetechs.com
# Website: https://www.xetechs.com
# See LICENSE file for full copyright and licensing details.
###########################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from collections import defaultdict

class ProductCategory(models.Model):
    _inherit = "product.category"

    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.company)
ProductCategory()