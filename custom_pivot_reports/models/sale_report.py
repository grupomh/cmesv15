# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    default_code = fields.Char('Referencia interna', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', 'Almacén', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['default_code'] = ", t.default_code"
        fields['warehouse_id'] = ', s.warehouse_id'

        groupby += ', t.default_code'

        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
