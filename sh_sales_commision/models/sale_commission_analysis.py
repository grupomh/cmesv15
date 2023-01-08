# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models,fields,api

class SaleCommissionAnalysis(models.Model):
    _name = 'sale.commission.analysis'
    
    name = fields.Char("Descripcion")
    date = fields.Date("Fecha")
    sales_person_id = fields.Many2one("res.users",string="Vendedor")
    invoice_ref = fields.Char("Factura")
    order_ref = fields.Char("Pedido de Venta")
    type = fields.Selection([('standard','Estandard'),('partner','Socio Afiliado'),
                             ('product','Producto/Categoria de Producto/Margen'),
                             ('discount','Descuento')],string="Typo de Comisiones")
    
    commission_name = fields.Many2one('sale.commission',string="Comision")
    product_id = fields.Many2one('product.product',string="Producto")
    category_id=fields.Many2one('product.category',string="Categoria de Producto")
    sub_category_id=fields.Many2one('product.category',string="Subcategoria de Producto")
    partner_id = fields.Many2one('res.partner',string="Socio")
    partner_type = fields.Char("Tipo de Socio")
    amount=fields.Float("Monto Comision")
    order_id = fields.Many2one('sale.order',string="Pedido de Venta")
    move_id = fields.Many2one('account.move',string="Factura")
    is_invoice = fields.Boolean("Is Invoice")
        