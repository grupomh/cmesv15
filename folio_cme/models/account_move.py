from odoo import api, models, fields
import datetime

class AccountMove(models.Model):
    _inherit = "account.move"
    folio = fields.Char(string="Folio",store=True, index=True, copy=False)

class AccountJournal(models.Model):
    _inherit = "account.journal"
    code_sequence = fields.Char(string="Codigo de Sequencia")