from odoo import models, fields, api

class Account_Move(models.Model):
    _inherit = 'account.move'
    invoice_suplier_resolution = fields.Char(string = 'Factura Proveedor')
    invoice_customer = fields.Char(string = '# de Factura')
