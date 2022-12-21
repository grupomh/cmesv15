# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
from collections import defaultdict
from itertools import groupby

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError
from odoo.tools import date_utils, float_round, float_is_zero


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def button_reproceso(self):
        self.ensure_one()
        product_ids = self.env['product.product'].search([('type', '=', 'product'), ('active', '=', True)])
        return {
            'name': _('Reproceso'),
            'view_mode': 'form',
            'res_model': 'stock.scrap',
            'view_id': self.env.ref('stock.stock_scrap_form_view2').id,
            'type': 'ir.actions.act_window',
            'context': {'default_production_id': self.id,
                        'product_ids': (self.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel')) | self.move_finished_ids.filtered(lambda x: x.state == 'done')).mapped('product_id').ids,
                        'default_is_reprocess': True,
                        'default_company_id': self.company_id.id
                        },
            'target': 'new',
        }
MrpProduction()
