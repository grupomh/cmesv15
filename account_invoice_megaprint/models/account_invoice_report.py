from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _no_fe_taxes(self):
        for data in self:
            if data.tax_ids and data.move_id.journal_id.is_factura_especial:
                for tax in data.tax_ids:
                    if not tax.active_fel and tax.amount == 12:
                        data.no_fe_taxes = round(data.price_subtotal * 12/100,2)
            else:
                data.no_fe_taxes = 0
    no_fe_taxes = fields.Float(compute="_no_fe_taxes")

