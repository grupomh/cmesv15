# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    date_invoice = fields.Date('Fecha de factura', compute="_compute_invoice_date", store=False)

    @api.depends('invoice_ids')
    def _compute_invoice_date(self):
        date = False
        for po in self:
            if po.invoice_ids:
                invoices = po.invoice_ids.filtered(lambda inv: inv.state not in ('draft', 'cancel') and inv.invoice_date)
                date = invoices[0].invoice_date if invoices else False
            po.update({
                'date_invoice': date,
            })

PurchaseOrder()