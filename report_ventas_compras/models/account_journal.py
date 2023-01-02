from odoo import api, fields, models

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    importacion = fields.Boolean(default=False, string="Importaciones?")