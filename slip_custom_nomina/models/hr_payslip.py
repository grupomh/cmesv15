# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrPayslip(models.Model):
    _inherit = "hr.payslip"


    send_mail_boleta=fields.Boolean('Boleta enviada', copy=False, readonly=True, default=False, help="Si el campo esta lleno, el correo electronico fue enviado")

    def action_send_payslip(self):   
        for rec in self:
            ctx = {}
            email_list = rec.employee_id.work_email
            if email_list:
                ctx['email_to'] = email_list
                ctx['email_from'] = self.env.user.partner_id.email
                ctx['send_email'] = True
                ctx['attendee'] = rec.employee_id.name
                template = self.env.ref('slip_custom_nomina.email_template_payslip')
                template.with_context(ctx).send_mail(self.id, force_send=True, raise_exception=False)
                rec.update({
                    'send_mail_boleta' : True,
                }) 
            else:
                rec.update({
                    'send_mail_boleta' : False,
                })
