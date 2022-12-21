# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger( __name__ )

class AccountMove(models.AbstractModel):
    _inherit = "account.move"

    internal_sequence_number = fields.Integer('# Correlativo', compute="_compute_sequence_number")

    @api.depends('name')
    def _compute_sequence_number(self):
        for rec in self:
            number = []
            internal_sequence = 0
            if rec.name and '/' in rec.name:
                number = rec.name.split('/')
                if number and len(number) > 2:
                    internal_sequence = number[2]
            rec.update({
                'internal_sequence_number': internal_sequence,
            })
    
    def get_reconcile_lines(self):
        aml_obj_ids = self.env['account.move.line']
        for rec in self:
            if rec.line_ids:
                aml_ids = rec.line_ids._reconciled_lines()
                _logger.info(aml_ids)
                aml_obj_ids = self.env['account.move.line'].browse(aml_ids)
                _logger.info(aml_obj_ids)
        return aml_obj_ids
AccountMove()

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def get_reconcile_lines(self):
        aml_obj_ids = self.env['account.move.line']
        for rec in self:
            #if rec.line_ids:
            aml_ids = rec._reconciled_lines()
            _logger.info(aml_ids)
            aml_obj_ids += self.env['account.move.line'].browse(aml_ids)
            _logger.info(aml_obj_ids)
        return aml_obj_ids

AccountMoveLine()