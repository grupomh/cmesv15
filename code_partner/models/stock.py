# -*- coding: utf-8 -*-

from odoo import api, fields, models

ROUTE_LIST = [
        ('01' ,'01'),
        ('02' ,'02'),
        ('03' ,'03'),
        ('04' ,'04'),
        ('05' ,'05'),
        ('06' ,'06'),
        ('07' ,'07'),
        ('08' ,'08'),
        ('09', '09'),
        ('10', '10')
    ]

class StockMove(models.Model):
    _inherit = 'stock.move'

    route = fields.Selection(ROUTE_LIST, string="Route", related="partner_id.route", store=True)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    route = fields.Selection(ROUTE_LIST, string="Route", related="partner_id.route", store=True)