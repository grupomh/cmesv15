from odoo import api, fields, models, _
from odoo.exceptions import UserError
from itertools import groupby

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    branch_id = fields.Many2one('res.branch', string="Branch")
