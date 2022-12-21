# -*- coding: utf-8 -*-

import time
from odoo import fields, models
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

import logging

_logger = logging.getLogger( __name__ )

class WizardFolioGeneralLedger(models.TransientModel):
    _name = 'wizard.folio.general.ledger'
    _description = 'wizard.folio.general.ledger'

    folio = fields.Integer(string='Folio', required=False, default=1)
    ledger_type = fields.Selection([
        ('op-1', 'Libro Mayor Resumido'),
        ('op-2', 'Libro Mayor Detallado')], string="Tipo de Mayor", default="op-1")

    def get_folio(self):
        context = self.env.context
        account_general_ledger = self.env['account.general.ledger']
        options = context.get('default_options', False)
        values = self.get_values(options=options)
        data = {
            'company': self.env.company.name,
            'title': 'LIBRO DIARIO MAYOR' if self.ledger_type == 'op-2' else 'LIBRO MAYOR',
            'date_from': datetime.strptime(options.get('date', False)['date_from'], "%Y-%m-%d").strftime('%d/%m/%Y'),
            'date_to': datetime.strptime(options.get('date', False)['date_to'], "%Y-%m-%d").strftime('%d/%m/%Y'),
            'lines': values,
            }
        return self.env.ref("l10n_gt_financial_reports.cme_general_ledger_report").report_action(self, data=data)
    
    def get_values(self, options=None):
        args = []
        res = []
        values = []
        if options:
            date_from = options.get('date', False)['date_from']
            args.append(('date', '>=', date_from))
            date_to = options.get('date', False)['date_to']
            args.append(('date', '<=', date_to))
            journal_ids = False
            account_groups = self.env['account.group'].search([('parent_id', '!=', False)], order="code_prefix asc")
            if options.get('journals'):
                journal_ids = [j.get('id') for j in options.get('journals') if j.get('selected')]
                if journal_ids:
                    args.append(('journal_id', 'in', journal_ids))
            for ac_group in account_groups:
                account_obj = account_pl_obj = account_gl_obj = self.env['account.account']
                child_groups = self.env['account.group'].search([('parent_id', 'child_of', ac_group.id)])
                for acc in child_groups:
                    if acc and acc.child_account_ids:
                        account_gl_obj += acc.child_account_ids.filtered(lambda acc: acc.internal_group not in ('income', 'expense'))
                        account_pl_obj += acc.child_account_ids.filtered(lambda acc: acc.internal_group in ('income', 'expense'))
                initial_gl_balance = initial_pl_balance = False
                account_moves_gl_lines = account_moves_pl_lines = False
                #Cuentas de Balance General
                if account_gl_obj:
                    domain_dict = {'_from': date_from, '_to': date_to, 'journals': journal_ids, 'accounts': account_gl_obj.ids}
                    initial_gl_balance = self.get_initial_balance(domain_dict=domain_dict)
                    account_moves_gl_lines = self.get_account_moves(domain_dict=domain_dict)
                #Cuentas de Resultados
                if account_pl_obj:
                    domain_dict = {'_from': date_from, '_to': date_to, 'journals': journal_ids, 'accounts': account_pl_obj.ids}
                    initial_pl_balance = self.get_initial_pl_balance(domain_dict=domain_dict)
                    _logger.info('****************************initial_pl_balance()****************************')
                    _logger.info(initial_pl_balance)
                    account_moves_pl_lines = self.get_account_moves(domain_dict=domain_dict)
                #Amounts for account group
                i_balance = debit = credit = 0.00
                if initial_gl_balance:
                    i_balance += sum([x.get('balance', 0.00) for x in initial_gl_balance])
                if initial_pl_balance:
                    i_balance += sum([x.get('balance', 0.00) for x in initial_pl_balance])
                if account_moves_gl_lines:
                    debit += sum([x.get('debit', 0.00) for x in account_moves_gl_lines])
                    credit += sum([x.get('credit', 0.00) for x in account_moves_gl_lines])
                if account_moves_pl_lines:
                    debit += sum([x.get('debit', 0.00) for x in account_moves_pl_lines])
                    credit += sum([x.get('credit', 0.00) for x in account_moves_pl_lines])
                f_balance = ((i_balance + debit) - credit)
                account_details = []
                if self.ledger_type == 'op-2' and ac_group.show_details == True:
                    if account_moves_gl_lines:
                        account_details += self.get_account_details(aml_lines=account_moves_gl_lines, initial_balance=i_balance)
                    if account_moves_pl_lines:
                        account_details += self.get_account_details(aml_lines=account_moves_pl_lines, initial_balance=i_balance)
                aml = {
                    'group_code': ac_group.code_prefix,
                    'group_name': ac_group.name,
                    'initial_balance': i_balance or 0.00,
                    'debit': debit or 0.00,
                    'credit': credit or 0.00,
                    'balance' : f_balance or 0.00,
                    'details': account_details,
                }
                values.append(aml)
        return values
    
    def get_account_details(self, aml_lines=None, initial_balance=0.00):
        res = []
        if aml_lines:
            res = []
            if initial_balance >= 0.00:
                item = {
                    'date': False,
                    'description': 'Saldo Inicial',
                    'initial_balance': initial_balance or 0.00,
                    'debit': 0.00,
                    'credit': 0.00,
                    'balance': initial_balance or 0.00,
                }
                res.append(item)
            balance = initial_balance or 0.00
            for aml in aml_lines:
                debit = aml.get('debit', 0.00)
                credit = aml.get('credit', 0.00)
                balance += (debit - credit)
                item = {
                    'date': datetime.strptime(str(aml.get('day', False)), '%Y-%m-%d').strftime('%d/%m/%Y'),
                    'description': 'Movimiento del Dia',
                    'initial_balance': 0.00,
                    'debit': debit or 0.00,
                    'credit': credit or 0.00,
                    'balance': balance or 0.00,
                }
                res.append(item)
        return res 

    def get_initial_pl_balance(self, domain_dict=None):
        query_result = False
        if domain_dict:
            _logger.info('****************************domain_dict()****************************')
            _logger.info(domain_dict)
            
            date_from = domain_dict.get('_from', False)
            date_init = datetime.strptime(str(date_from), '%Y-%m-%d').strftime('%Y-01-01')
            date_to = domain_dict.get('_to', False)
            journals = domain_dict.get('journals', False)
            accounts = domain_dict.get('accounts', False)
            args_domain = []
            query = "SELECT sum(aml.balance) as balance FROM account_move_line aml inner join account_move am on am.id = aml.move_id"
            if date_from:
                query += " WHERE am.state not in ('draft', 'cancel') and aml.date >= %s and aml.date < %s"
                args_domain.append(date_init)
                args_domain.append(date_from)
            if journals:
                query += " AND aml.journal_id in %s"
                args_domain.append(tuple(journals))
            if accounts:
                query += " AND aml.account_id in %s"
                args_domain.append(tuple(accounts))
            query += " GROUP BY aml.account_id;"
            #query = query_select + query_where + query_group
            if query:
                _logger.info('****************************query()****************************')
                _logger.info(query)
                self.env.cr.execute(query, tuple(args_domain))
                query_result = self.env.cr.dictfetchall()
                _logger.info('****************************query_result()****************************')
                _logger.info(query_result)
                _logger.info('****************************args_domain()****************************')
                _logger.info(args_domain)
        return query_result

    def get_initial_balance(self, domain_dict=None):
        query_result = False
        if domain_dict:
            _logger.info('****************************domain_dict()****************************')
            _logger.info(domain_dict)
            date_from = domain_dict.get('_from', False)
            date_to = domain_dict.get('_to', False)
            journals = domain_dict.get('journals', False)
            accounts = domain_dict.get('accounts', False)
            args_domain = []
            query = "SELECT sum(aml.balance) as balance FROM account_move_line aml inner join account_move am on am.id = aml.move_id"
            if date_from:
                query += " WHERE am.state not in ('draft', 'cancel') and aml.date < %s "
                args_domain.append(date_from)
            if journals:
                query += " AND aml.journal_id in %s"
                args_domain.append(tuple(journals))
            if accounts:
                query += " AND aml.account_id in %s"
                args_domain.append(tuple(accounts))
            query += " GROUP BY aml.account_id;"
            #query = query_select + query_where + query_group
            if query:
                self.env.cr.execute(query, tuple(args_domain))
                query_result = self.env.cr.dictfetchall()
        return query_result
    
    def get_account_moves(self, domain_dict=None):
        query_result = False
        if domain_dict:
            _logger.info('****************************domain_dict()****************************')
            _logger.info(domain_dict)
            date_from = domain_dict.get('_from', False)
            date_to = domain_dict.get('_to', False)
            journals = domain_dict.get('journals', False)
            accounts = domain_dict.get('accounts', False)
            args_domain = []
            query = "SELECT DATE_TRUNC('day', aml.date)::date as day, sum(aml.debit) as debit, sum(aml.credit) as credit FROM account_move_line aml inner join account_move am on am.id = aml.move_id"
            if date_from:
                query += " WHERE am.state not in ('draft', 'cancel') and aml.date >= %s"
                args_domain.append(date_from)
            if date_to:
                query += " AND aml.date <= %s"
                args_domain.append(date_to)
            if journals:
                query += " AND aml.journal_id in %s"
                args_domain.append(tuple(journals))
            if accounts:
                query += " AND aml.account_id in %s"
                args_domain.append(tuple(accounts))
            query += " GROUP BY DATE_TRUNC('day', aml.date) ORDER BY DATE_TRUNC('day', aml.date);"
            #query = query_select + query_where + query_group
            if query:
                self.env.cr.execute(query, tuple(args_domain))
                query_result = self.env.cr.dictfetchall()
        return query_result


