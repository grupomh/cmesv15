# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    apply_credit_limit = fields.Boolean(string="¿Aplicar Limite de Credito?", default=False, help="Seleccionar si en esta compañia se aplicara limite de credito")
ResCompany()