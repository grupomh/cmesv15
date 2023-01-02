from odoo import api, models, fields
from datetime import date
import datetime
class AccountMove(models.Model):
    _inherit = 'account.move'
    
    dias_vencidos = fields.Char(
        string='Antiguedad',
        compute =  'compute_date'
    )
    #payment_date = fields.Date('Fecha de Pago', store=False, compute="_compute_payment_date")
    #payment_days = fields.Integer('Dias del Pago', store=False, compute="_compute_payment_date")
    invoice_payment_state=fields.Selection('pagos',related='payment_state')

    # @api.depends('invoice_payment_state')
    # def _compute_payment_date(self):
    #     for rec in self:
    #         payment_date = False
    #         payment_days = False
    #         if rec.invoice_payment_state == 'paid':
    #             payment_id = self.env['account.payment'].search([('invoice_ids', 'in', [rec.id])], order="payment_date desc", limit=1)
    #             if payment_id:
    #                 payment_date = payment_id.payment_date
    #                 payment_days = (rec.invoice_date - payment_id.payment_date)
    #         rec.update({
    #              'payment_date': payment_date,
    #              'payment_days': abs(payment_days.days) if payment_days else 0,
    #          })



    @api.depends('state','invoice_payment_state')
    def compute_date(self):
        for invoice in self:
            if (invoice.invoice_date and invoice.invoice_payment_state != 'paid') and invoice.state == 'posted':
                date_now = datetime.datetime.now()
                date_invoice_odoo = str(invoice.invoice_date)
                date_invoice_odoo = date_invoice_odoo.split('-')
                int_date_list = [int(i) for i in date_invoice_odoo]
                date_odoo = datetime.datetime(int_date_list[0],int_date_list[1],int_date_list[2],0,0)
                date_finally  = str((date_now - date_odoo).days)
                invoice.update({'dias_vencidos': date_finally})
            else:
                invoice.update({'dias_vencidos': '0'})
