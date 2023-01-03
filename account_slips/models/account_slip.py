# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import Warning


class AccountSlip(models.Model):
    _name = "account.slip"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Account Slips For Credit Sales / Purchase."

    name = fields.Char("Reference No", copy=False, Help="Reference Number For Account Slip")
    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.company, help="Related Company")
    partner_id = fields.Many2one("res.partner", "Partner", required=True, track_visibility='onchange', help="Related Partner.")
    issue_date = fields.Date("Issue Date", required=True, default=datetime.now().date(), track_visibility='onchange', help="Issue Date For Account Slip")
    due_date = fields.Date("Due Date", track_visibility='onchange', required=True, help="Due Date For Account Slip.")
    invoice_ids = fields.Many2many('account.move', 'invoice_slip_rel', 'slip_id', 'invoice_id', string="Invoices")
    pay_day = fields.Date("Date To Pay", copy=False, track_visibility='onchange', help="Date On Which Payment Will Be Done.")
    date_of_payment = fields.Date("Date Of Payment Done", copy=False, help="Date On Which Amount Is Paid For Slip.")
    slip_total_amount = fields.Monetary("Monto Total", compute="_compute_slip_amount", store=True,
                                     copy=False,help="Total Amount For Slip.")
    slip_paid_amount = fields.Monetary("Monto Pagado", compute="_compute_slip_amount", store=True,
                                    copy=False,                                    help="Paid Amount For Slip.")
    slip_outstanding_amount = fields.Monetary("Monto Pendiente", compute="_compute_slip_amount", store=True,
                                           copy=False,help="Outstanding Amount For Slip.")
    state = fields.Selection([('draft', 'Borrador'),
                              ('open', 'Abierto'),
                              ('paid', 'Pagado'),
                              ('cancel', 'Anulado')], string="State", copy=False, default="draft",
                             track_visibility='onchange', help="State Of Account Slips.")
    account_slip_type = fields.Selection([('collection_slip', 'Collection Slip'),
                                          ('payment_slip', 'Payment Slip')], string="Type",
                                         help="Type Of Account Slips.")
    currency_id = fields.Many2one("res.currency", string="Currency", copy=False,
                                  help="Currency For This Slip.")
    user_id = fields.Many2one("res.users", string="Responsible", track_visibility='onchange', default=lambda self: self.env.user, help="Person Responsible For Slip.")
    notes = fields.Text('Notas')

    #@api.onchange("due_date")
    #def onchange_due_date(self):
    #    if self.due_date:
    #        due_date_weekday = self.due_date.weekday()
    #        payment_weekday = self.company_id.day_of_payment or 0
    #        days_to_add = (payment_weekday - due_date_weekday) if payment_weekday >= due_date_weekday else (7 + (payment_weekday - due_date_weekday))
    #        self.pay_day = self.due_date + timedelta(days=days_to_add)

    @api.model
    def create(self, vals):
        #if vals.get('account_slip_type') == 'payment_slip':
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('account.slip') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('account.slip') or _('New')
        return super(AccountSlip, self).create(vals)

    def action_validate(self):
        for account_slip in self:
            if not account_slip.pay_day:
                raise Warning(_("You Have Not Set Date to Pay Yet. Set Date For Payment."))
            if not account_slip.invoice_ids:
                raise Warning(_("You Must Set Invoices To Validate Slip.."))
            account_slip.write({"state": "open"})
        return True

    def action_cancel(self):
        return self.write({"state": "cancel"})

    @api.depends("invoice_ids", "invoice_ids.amount_residual")
    def _compute_slip_amount(self):
        for account_slip in self:
            slip_amount = 0.0
            outstanding_amount = 0.0
            for invoice in account_slip.invoice_ids:
                slip_amount += invoice.amount_total or 0.0
                outstanding_amount += invoice.amount_residual or 0.0
            account_slip.slip_total_amount = slip_amount
            account_slip.slip_paid_amount = slip_amount - outstanding_amount
            account_slip.slip_outstanding_amount = outstanding_amount
            account_slip.currency_id = account_slip.invoice_ids and account_slip.invoice_ids[0].currency_id.id or False

            if account_slip.state == 'open' and outstanding_amount == 0.0:
                account_slip.write({'state': 'paid', 'date_of_payment': datetime.now().today()})

AccountSlip()

class SlipDays(models.Model):
    _name = "slip.days"

    name = fields.Char('Dia', required=True)
SlipDays()

class SlipHours(models.Model):
    _name = "slip.hours"

    name = fields.Char('Hora', required=True)
SlipHours()