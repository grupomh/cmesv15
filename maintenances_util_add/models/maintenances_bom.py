# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class MaintenancesBom(models.Model):
    _name ="maintenances.bom"
    _description = "utilidades agregadas a mantenimiento"
    _rec_order="id desc"
    _rec_name="product_id"
    _check_company_auto =True

    def _default_currency_id(self):
        company_id = self.env.context.get('company_id') or self.env.company.id
        return self.env['res.company'].browse(company_id).currency_id

    def _get_default_product_uom_id(self):
        return self.env['uom.uom'].search([], limit=1, order='id').id
    
    


    product_id = fields.Many2one('product.product', 'Component', required=True, copy=False)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', related='product_id.product_tmpl_id')
    details = fields.Html('Detalles', readonly=True, related='product_tmpl_id.description')
    cost_component = fields.Float('Costo unitario',readonly=True, related='product_tmpl_id.standard_price')
    company_id = fields.Many2one('res.company', 'Company', required=False, default=lambda self: self.env.company.id,readonly=True)
    equip_maintenance_id = fields.Many2one('maintenance.equipment', 'Parent equipement BoM', ondelete='cascade', required=True) #--------------------AQUI
    product_qty = fields.Float('Quantity', default=1.0,digits='Product Unit of Measure', required=True)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure',
        required=True,
        help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control",related='product_id.uom_id',domain="[('category_id', '=', product_uom_category_id)]" )#domain="[('category_id', '=', product_uom_category_id)]"
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    sequence = fields.Integer(
        'Sequence', default=1,
        help="Gives the sequence order when displaying.")

    maintenance_menor=fields.Boolean('Menor', copy=False, required=False)
    maintenance_mayor=fields.Boolean('Mayor', copy=False, required=False)
    maintenance_ct=fields.Boolean('Correctivo', copy=False, required=False)


    currency_id = fields.Many2one('res.currency', 'Moneda',default= _default_currency_id)
    cost_qty = fields.Monetary('Costo total componente', readonly=True, copy=False,required=False, compute="_total_qty_cost")

    @api.depends('product_qty')
    def _total_qty_cost(self):
        for record  in self:
            record['cost_qty']=record.product_qty * record.cost_component


MaintenancesBom()




