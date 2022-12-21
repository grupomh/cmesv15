from odoo import api, fields, models

class AccountMoveFE(models.Model):
    _inherit = 'account.move'

    def _amount_total_fe_lines(self):
        for data in self:
            data.amount_total_fe_lines = 0
            for lines in data.invoice_line_ids:
                data.amount_total_fe_lines += lines.fe_total_line_amount

    amount_total_fe_lines = fields.Monetary(compute="_amount_total_fe_lines")