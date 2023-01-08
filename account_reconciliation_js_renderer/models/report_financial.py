from odoo import models, api, _, _lt, fields
from odoo.tools.misc import format_date
from datetime import timedelta

from collections import defaultdict

class ReportPartnerLedger(models.AbstractModel):
    _inherit = "account.partner.ledger"

    @api.model
    def _get_report_line_move_line(self, options, partner, aml, cumulated_init_balance, cumulated_balance):
        if aml['payment_id']:
            caret_type = 'account.payment'
        elif aml['move_type'] in ('in_refund', 'in_invoice', 'in_receipt'):
            caret_type = 'account.invoice.in'
        elif aml['move_type'] in ('out_refund', 'out_invoice', 'out_receipt'):
            caret_type = 'account.invoice.out'
        else:
            caret_type = 'account.move'

        date_maturity = aml['date_maturity'] and format_date(self.env, fields.Date.from_string(aml['date_maturity']))
        fel_text = ' |'
        if aml['move_name']:
            move = self.env['account.move'].search([('name', '=', aml['move_name'])])
            if len(move):
                if move[0].fel_no:
                    fel_text += ' FEL NO: ' + move[0].fel_no + ' | '
                if move[0].fel_serie:
                    fel_text += ' FEL SERIE: ' + move[0].fel_serie
        columns = [
            {'name': aml['journal_code']},
            {'name': aml['account_code']},
            {'name': self._format_aml_name(aml['name'], aml['ref'], aml['move_name']) + fel_text} ,
            {'name': date_maturity or '', 'class': 'date'},
            {'name': aml['full_rec_name'] or ''},
            {'name': self.format_value(cumulated_init_balance), 'class': 'number'},
            {'name': self.format_value(aml['debit'], blank_if_zero=True), 'class': 'number'},
            {'name': self.format_value(aml['credit'], blank_if_zero=True), 'class': 'number'},
        ]
        if self.user_has_groups('base.group_multi_currency'):
            if aml['currency_id']:
                currency = self.env['res.currency'].browse(aml['currency_id'])
                formatted_amount = self.format_value(aml['amount_currency'], currency=currency, blank_if_zero=True)
                columns.append({'name': formatted_amount, 'class': 'number'})
            else:
                columns.append({'name': ''})
        columns.append({'name': self.format_value(cumulated_balance), 'class': 'number'})
        a = columns
        return {
            'id': aml['id'],
            'parent_id': 'partner_%s' % (partner.id if partner else 0),
            'name': format_date(self.env, aml['date']),
            'class': 'date' + aml.get('class', ''),
            'columns': columns,
            'caret_options': caret_type,
            'level': 4,
        }

ReportPartnerLedger()