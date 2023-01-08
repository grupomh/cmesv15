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

class ResCity(models.Model):
    _inherit = "res.city"

    name = fields.Char('Estado', required=True)
    parent_id = fields.Many2one('res.country.state', 'Estado', required=False)
    company_id = fields.Many2one('res.company', 'Company', required=False, default=lambda self: self.env.company)


ResCity()