from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move.line'

    weight = fields.Float(compute='weight_total', readonly=True, string="Peso Total")

    def weight_total(self):
        for data in self:
            data.weight = data.product_id.weight * data.quantity