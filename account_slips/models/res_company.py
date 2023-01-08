# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = "res.company"

    account_slip_note = fields.Html("Notes", help="Account Slip Report Notes.")
    days_ids = fields.Many2many('slip.days', 'company_days_rel', 'company_id', 'day_id', string="Dias de pago")
    hours_ids = fields.Many2many('slip.hours', 'company_hours_rel', 'company_id', 'hour_id', string="Horas de pago")
    day_of_payment = fields.Selection([("0", "Monday"),
                                       ("1", "Tuesday"),
                                       ("2", "Wednesday"),
                                       ("3", "Thursday"),
                                       ("4", "Friday"),
                                       ("5", "Saturday"),
                                       ("6", "Sunday")],
                                      string="Day Of Payment", default='0',
                                      help="On This Day Payment Should Be Done After Due Date of Payment Slips."
                                      )
ResCompany()