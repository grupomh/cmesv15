# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger( __name__ )

class AccountAccount(models.AbstractModel):
    _inherit = "account.account"

    ledger_group_id = fields.Many2one('account.group', 'Grupo de Mayor', required=False, copy=False, tracking=False)

AccountAccount()