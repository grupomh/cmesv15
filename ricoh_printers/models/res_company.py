# -*- coding: utf-8 -*-


from odoo import fields, models, api
from odoo.exceptions import UserError
from odoo.addons.ricoh_printers import numero_a_texto



class ResCompany(models.Model):
    _inherit = 'res.company'

    ricoh_devices = fields.Boolean('Use Ricoh Devices', required=False, default=False)
    ricoh_type = fields.Selection([
        ('LPD', 'LPD and Port'),
        ('PATH', 'Directory')], string="Conection", default='LPD')
    device_port = fields.Char('Port', default="515")
    device_path = fields.Char("Device Path", required=False)
    ricoh_user = fields.Char('Usuario', required=False)
    ricoh_password = fields.Char('Password', required=False)

ResCompany()