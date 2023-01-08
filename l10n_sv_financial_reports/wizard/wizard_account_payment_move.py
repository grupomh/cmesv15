# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class WizardAccountPaymentMove(models.TransientModel):
    _name = 'wizard.account.payment.move'
    _description = 'Wizard Account Payment Move Report'

    payment_ids = fields.Many2many('account.payment', 'rel_wizard_payment', 'wizard_id', 'payment_id', string="Pagos")
    group_by_document = fields.Boolean('Agrupar por Boleta', default=True)

    def group_by_docs(self, move_lines=None):
        grouped_result = {}
        if move_lines:
            grouped_result = {}
            for aml in move_lines.filtered(lambda x: x.move_id.state not in ('draft', 'cancel')).sorted(key=lambda x: x.debit):
                if aml.payment_id.boleta not in grouped_result:
                    grouped_result[aml.payment_id.boleta] = []
                grouped_result[aml.payment_id.boleta].append(aml)
        return grouped_result
    
    def group_by_account(self, move_lines=None):
        grouped_result = {}
        if move_lines:
            grouped_result = {}
            for aml in move_lines:
                if aml.account_id not in grouped_result:
                    grouped_result[aml.account_id] = []
                grouped_result[aml.account_id].append(aml)
        return grouped_result
    
    def get_aml(self, move_lines=[]):
        aml_obj = self.env['account.move.line']
        if move_lines:
            aml_obj = self.env['account.move.line']
            for aml in move_lines:
                aml_obj += aml
        return aml_obj

    def action_generate_report(self):
        self.ensure_one()
        values = self.generate_values()
        #raise UserError(('%s') %(values))
        datas = {
            'values': values,
            'company_name': self.env.company.name,
        }
        return self.env.ref('l10n_sv_financial_reports.action_report_account_payment_move').report_action(self, data=datas)
    
    def generate_values(self):
        account_move_lines = self.env['account.move.line']
        aml_grouped = []
        res = []
        moves = []
        items = {}
        for rec in self:
            for pay in rec.payment_ids.sorted(key=lambda l: l.payment_date):
                if pay.state in ('draft', 'cancelled'):
                    raise UserError(('No se puede procesar pagos en borrador o cancelado'))
                if pay.move_line_ids:
                    account_move_lines += pay.move_line_ids
            subitems = {}
            items = {}
            counter = 0
            if account_move_lines:
                aml_grouped = rec.group_by_docs(move_lines=account_move_lines)
                for doc, aml in aml_grouped.items():
                    #items = {}
                    res = []
                    aml_account_grouped = rec.group_by_account(move_lines=aml)
                    aml_ids = rec.get_aml(move_lines=aml)
                    move_ids = aml_ids.move_id.filtered(lambda x: x.state not in ('draft', 'cancel'))
                    _logger.info('**********************move_ids**********************')
                    _logger.info(move_ids)
                    counter += 1
                    items = {
                        'document': doc,
                        'date': aml[0].date,
                        'count': counter,
                        'journal': aml[0].move_id.journal_id.name,
                        'branch': aml[0].move_id.branch_id.name,
                        'notes': ",".join("{}".format(i.name) for i in move_ids),
                        'lines': False,
                    }
                    for account, aml_lines in aml_account_grouped.items():
                        aml_reconciled = rec.get_aml(move_lines=aml_lines)
                        _logger.info('**********************aml_reconciled**********************')
                        _logger.info(aml_reconciled)
                        debit = sum([x.debit for x in aml_lines])
                        credit = sum([x.credit for x in aml_lines])
                        subitems = {
                            'account_group_code': account.ledger_group_id.code_prefix,
                            'account_group': account.ledger_group_id.name,
                            'account_code': account.code,
                            'account': account.name,
                            'partial': 0.00,
                            'debit': debit or 0.00,
                            'credit': credit or 0.00,
                            'aml_reconciled': rec.get_aml_reconcile_lines(aml=aml_reconciled.filtered(lambda x: x.account_id.id == account.id).get_reconcile_lines(), debit=debit, credit=credit),
                        }
                        res.append(subitems)
                    if res:
                        items.update({
                            'lines': res,
                        })
                        moves.append(items)
        return moves
    
    def get_aml_reconcile_lines(self, aml=None, debit=None, credit=None):
        res = []
        if aml:
            if debit > 0.00:
                for l in aml.filtered(lambda x: x.debit > 0.00):
                    item = {
                        'account_code': l.account_id.code,
                        'account': (("Pago de factura: %s ") %((l.ref if l.ref else ''))),
                        'partial': l.debit or 0.00,
                    }
                    res.append(item)
            if credit > 0.00:
                for l in aml.filtered(lambda x: x.credit > 0.00):
                    item = {
                        'account_code': l.account_id.code,
                        'account': (("Pago de factura: %s ") %(l.ref if l.ref else '')),
                        'partial': l.credit or 0.00,
                    }
                    res.append(item)
        return res

                    
WizardAccountPaymentMove()