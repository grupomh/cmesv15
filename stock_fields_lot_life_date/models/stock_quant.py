# -*- coding: utf-8 -*

from odoo import api, fields, models, _

class StockQuant(models.Model):
    _inherit = "stock.quant"

    life_date =fields.Datetime('Fecha de caducidad', readonly=True,copy=False, related="lot_id.expiration_date")

StockQuant()