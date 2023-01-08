# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    cat_process = fields.Selection([
        ('Bases', 'Bases'),
        ('Confiteria', 'Confiteria'),
        ('Cubiertas', 'Cubiertas'),
        ('Extrusion', 'Extrusion'),
        ('Bañado galleta', 'Bañado galleta'),
        ('Envasado', 'Envasado'),
        ('Encajado', 'Encajado'),
        ('Moldeado', 'Moldeado'),
        ('Firsclass llenado', 'Firsclass llenado'),
        ('Chocotaza', 'Chocotaza'),
        ('Chocolate liquido galleta', 'Chocolate liquido galleta'),
        ('Mezclas', 'Mezclas'),
        ('Heladeria','Heladeria'),
        ('Desarrollo','Desarrollo')],string="Proceso",required=False,readonly=False,copy=False,help="Ingrese el proceso de fabricacion al que pertenece este producto valido para MH")

MrpBom()