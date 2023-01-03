from odoo import fields, models, api
class ResPartner(models.Model):
    _inherit = "res.partner"

    type_document = fields.Selection([
        ('CUI', 'Con DPI'),
        ('EXT', 'Con Pasaporte'),
        ('NIT', 'Con NIT')], string="Documento", default="NIT")


    @api.onchange('vat')
    def onchange_nit(self):
        if self.vat:
            nit = self.vat
            if '-' in nit:
                self.vat = nit.replace('-', '')
ResPartner()
