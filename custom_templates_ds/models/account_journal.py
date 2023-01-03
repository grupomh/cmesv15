# -*- coding: utf-8 -*-


from odoo import fields, models, api
from odoo.exceptions import UserError, Warning



class AccountJournal(models.Model):
    _inherit = 'account.journal'

    numero_resolucion = fields.Char('Numero CAI', required=False)
    vencimiento_resolucion = fields.Date('Fecha de Vencimiento', required=False)
    rango_documentos = fields.Char('Rango de numeracion', default=False)
AccountJournal()