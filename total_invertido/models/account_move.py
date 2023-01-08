
from odoo import models, fields, api
class Account_move(models.Model):

    _inherit = 'account.move'

    total_inverso = fields.Monetary(string="Total Inverso",compute='compute_total_inverso')

    @api.depends('amount_total','state')
    def compute_total_inverso(self):
        for invoice in self:
            cero = 0.00
            if invoice.state == 'cancel':
                invoice.update({'total_inverso': cero})
            else:
                invoice.update({'total_inverso': invoice.amount_total})