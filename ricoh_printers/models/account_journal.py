# -*- coding: utf-8 -*-


from odoo import fields, models, api
from odoo.exceptions import UserError



class AccountJournal(models.Model):
    _inherit = 'account.journal'

    active_ricoh = fields.Boolean('Activar RICOH', requiered=False, default=False)
    ricoh_type = fields.Selection([
        ('FCF', 'Factura'),
        ('FCFE', 'Factura Exenta'),
        ('FEX', 'Factura Exporatacion'),
        ('NDC', 'Nota de Credito'),
        ('CCF', 'Credito Fiscal'),
        ('CCFNS', 'Credito Fiscal No Sujeta'),
        ('CDR', 'Constancia de Retencion'),
        ('FSE', 'Factura Sujeto Excluido')], string="Tipo documento", default="FCF")
    resolution_number = fields.Char('Resolucion', required=False)
    is_exento = fields.Boolean('Documento Exento', required=False, default=False)
    serie = fields.Char('Serie', required=False)
AccountJournal()