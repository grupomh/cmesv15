
from odoo import models, fields, api
class Account_move(models.Model):
    _inherit = 'account.move'

    invoice_print_status = fields.Char(string="Estado de Impresión",compute='status_invoice', store=True)

    @api.depends('count_print')
    def status_invoice(self):
        for record in self:
            if record.count_print >= 1:
                record.update({'invoice_print_status': 'Impresa'})
            else:
                record.update({'invoice_print_status': 'No Impresa'})