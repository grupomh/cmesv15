# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

class AccountPaymentSeller(models.Model):
    _inherit = "account.payment"

    vendedor_id = fields.Many2one('res.users', string='Vendedor') 



# class MultiInvoicePaymentSeller(models.TransientModel):
#     _inherit = "customer.multi.payments"

#     vendedor_id = fields.Many2one('res.users', string='Vendedor') 

#     def get_new_payment_vals(self,payment):
#         res = super(MultiInvoicePaymentSeller, self).get_new_payment_vals(payment)
#         for rec in self:
#             if rec.vendedor_id:
#                 res.update({'vendedor_id': rec.vendedor_id.id or False})
#         return res


# MultiInvoicePaymentSeller()




# class PaymentRegisterSeller(models.TransientModel):
#     _inherit = 'account.payment.register'

#     vendedor_id = fields.Many2one('res.users', string='Vendedor') 

#     def _prepare_payment_vals(self, invoices):
#         res = super(PaymentRegisterSeller, self)._prepare_payment_vals(invoices)
#         for rec in self:
#             if rec.vendedor_id:
#                 res.update({
#                     'vendedor_id': rec.vendedor_id.id or False,
#                 })
#         return res

# PaymentRegisterSeller()
