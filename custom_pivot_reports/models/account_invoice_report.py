# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api

from functools import lru_cache

class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    warehouse_id = fields.Many2one('stock.warehouse', string='Almacén', readonly=True)
    default_code = fields.Char('Referencia interna', readonly=True)

    @api.model
    def _from(self):
        query_from = super(AccountInvoiceReport, self)._from()
        return query_from + '''
                   LEFT JOIN sale_order so ON move.invoice_origin = so.name
        '''

    @api.model
    def _select(self):
        query_select = super(AccountInvoiceReport, self)._select()
        if query_select:
            query_select += '''
                    , so.warehouse_id, template.default_code
            '''
        else:
            query_select = ''
        return query_select

    @api.model
    def _group_by(self):
        query_group_by = super(AccountInvoiceReport, self)._group_by()
        return query_group_by + '''
                    , so.warehouse_id, template.default_code
            '''

