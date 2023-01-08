# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError

class MultiInvoicePayment(models.TransientModel):
    _inherit = "customer.multi.payments"

    branch_id = fields.Many2one('res.branch', 'Rama', copy=False, required=False, default=lambda self: self.env.user.branch_id)


    def get_new_payment_vals(self, payment):
        res = super(MultiInvoicePayment, self).get_new_payment_vals(payment)
        for rec in self:
            if rec.branch_id:
                res.update({
                    'branch_id': rec.branch_id.id or False,
                })
        return res

MultiInvoicePayment()