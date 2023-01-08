from odoo import models, fields, api
class Res_partner(models.Model):
    _inherit = 'res.partner'
    dui = fields.Char('DUI')
    nrc = fields.Char('NRC')