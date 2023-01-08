# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class KardexStock(models.Model):
    _name ="kardex.stock"
    _description = "Kardex movimientos"
    _rec_order="id desc"

    def _default_currency_id(self):
        company_id = self.env.context.get('company_id') or self.env.company.id
        return self.env['res.company'].browse(company_id).currency_id    

    company_id = fields.Many2one('res.company', 'Company', required=False, default=lambda self: self.env.company.id,readonly=True)
    currency_id = fields.Many2one('res.currency', 'Monedas',default= _default_currency_id)


    asiento = fields.Char("Asiento", copy=False)
    fecha = fields.Datetime("Fecha", copy=False)
    tipo_doc = fields.Char("Tipo documento", copy=False)
    no_doc = fields.Char("No. doc", copy=False)
    no_fuente = fields.Char("No. fuente", copy=False)
    ubi_origen = fields.Char("Ubicacion origen", copy=False)
    ubi_dest = fields.Char("Ubicacion destino", copy=False)
    client = fields.Char("Cliente", copy=False)
    category = fields.Char("Categoria", copy=False)
    uom = fields.Char("Unidad", copy=False)
    cost_uni = fields.Float("Costo unitario", copy=False)
    qty_transf = fields.Float("Cant. Transfe", copy=False)
    qty_entrada = fields.Float("Entrada.", copy=False)
    qty_salida = fields.Float("Salida.", copy=False)
    cost_entrada = fields.Monetary("Entrada", copy=False)
    cost_salida = fields.Monetary("Salida", copy=False)
    product = fields.Char("Producto", copy=False)
    month = fields.Integer("Mes", copy=False)

