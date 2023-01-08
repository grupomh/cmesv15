# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrPayslipRun(models.Model):
    _inherit = "hr.payslip.run"

    #def action_send_session_by_email_cron(self):
     #   session_ids = self.env['hr.payslip'].search([('email_sent', '=', False)])
      #  for session in session_ids:
       #     if session.email_sent is False:
        #        session.action_send_session_by_email()
         #       session.email_sent = True