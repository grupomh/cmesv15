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

class ResPartner(models.Model):
    _inherit = "res.partner"
    
    city_id = fields.Many2one('res.city', 'Municipio', required=False)

ResPartner()