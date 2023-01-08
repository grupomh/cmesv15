# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def  validate_limit_credit(self):
        today = fields.Date.context_today(self)
        for record in self:
            company = record.env.company
            if record.partner_id.apply_credit_limit == False:
                continue
            if company.apply_credit_limit == False:
                continue
            if self.env.user.has_group('partner_credit_limit.group_access_credit_limit'):
                continue
            if record.partner_id.total_overdue:
                due_invoices = {}
                move_line = record.partner_id.unreconciled_aml_ids.filtered(lambda r: today > r.date_maturity if r.date_maturity else today > r.date and r.company_id == record.env.company)
                for line in move_line:
                    due_invoices.setdefault(line)
                raise UserError(_('This Partner has overdue invoices: \n' + ' \n '.join( ['No: %s, date: %s'%(i.move_id.name, i.move_id.invoice_date) for i in due_invoices] )))
            else:
                limit = record.partner_id.credit_limit
                amount = sum([aml.amount_residual for aml in record.partner_id.unreconciled_aml_ids.filtered(lambda r: not r.blocked and r.company_id == record.env.company)])
                if record.amount_total > limit or amount > limit:
                    raise UserError(_('This Partner has exceeded its assigned credit limit'))


    #def action_confirm(self):
    #    res = super(SaleOrder, self).action_confirm()
    #    self.validate_limit_credit()
    #    return res
    
    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        self.validate_limit_credit()
        return res
    
        
