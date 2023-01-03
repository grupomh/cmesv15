from odoo import models, fields, api
class Res_partner(models.Model):
    _inherit = 'res.partner'
    giro = fields.Char('Giro')