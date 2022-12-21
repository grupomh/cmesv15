# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from werkzeug import url_encode


class HrExpenseSheetRegisterPaymentWizard(models.TransientModel):
    _inherit = "hr.expense.sheet.register.payment.wizard"


    @api.onchange('currency_id')
    def onchange_currency(self):
        self.amount = self.company_id.currency_id._convert(self.expense_sheet_id.total_amount, self.currency_id, self.company_id, self.payment_date or fields.Date.today())
    
HrExpenseSheetRegisterPaymentWizard()