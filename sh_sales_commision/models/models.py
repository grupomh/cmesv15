# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models,fields,api

class Partner(models.Model):
    _inherit = 'res.partner'

    affiliated = fields.Boolean("Afiliado")

Partner()

class SaleCommission(models.Model):
    _name = 'sale.commission'
    
    name = fields.Char("Descripción")
    user_ids = fields.Many2many('res.users',string="Vendedor")
    type = fields.Selection([
        ('standard','Estandard'),
        ('product','Producto y/o Categoria de Producto')], string="Tipo de Comision")
    
    standard_commission_per = fields.Float("% Comision Estandard")
    affiliated_commission_per = fields.Float("% Comision Socio")
    non_affiliated_commission_per = fields.Float("% Comision Socio no Afiliados")
    
    product_commission_lines = fields.One2many('product.commission.line','commission_id',string="Detalle Comisiones")
    
class CommissionLine(models.Model):
    _name = 'product.commission.line'
    
    
    commission_id = fields.Many2one('sale.commission',string="Comision")
    based_on = fields.Selection([('product','Producto'),('categories','Categoria de Producto')], string="Base", default="product")
    with_commission = fields.Selection([('fix','Precio Fijo'), ('margin','Margen'), ('exception','Estandard')], string="Comisiones con", default="exception")
    
    product_id = fields.Many2one('product.product',string="Producto")
    category_id=fields.Many2one('product.category',string="Categoria de Producto")
    
    target_price = fields.Float("Monto Objetivo")
    above_price_commission = fields.Float("% Comision sobre Precio")
    
    target_margin = fields.Float("% Mergen Objetivo")
    above_margin_commission = fields.Float("% Comision sobre Margen")
    below_margin_commission = fields.Float("% Comision debajo Margen")
    
    exception_commission = fields.Float("% Comision")
    
    
    
   
    