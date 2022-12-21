# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _default_currency_id(self):
        company_id = self.env.context.get('company_id') or self.env.company.id
        return self.env['res.company'].browse(company_id).currency_id


    product_tmpl_id = fields.Many2one('product.template', 'Product Template', related='product_id.product_tmpl_id')
    cost_component = fields.Float('Costo unitario',readonly=True, related='product_tmpl_id.sum_average_purchase', store=True)
    company_id = fields.Many2one('res.company', 'Company', required=False, default=lambda self: self.env.company.id,readonly=True)
    currency_id = fields.Many2one('res.currency', 'Moneda',default= _default_currency_id)
    maintenance_equipment_id2 = fields.Many2one('maintenance.equipment','Equipo mantenimiento',related='picking_id.maintenance_equipment_id',readonly=True)
    maintenance_request_id2=fields.Many2one('maintenance.request', 'Peticion de mantenimiento', related='picking_id.maintenance_request_id', readonly=True)
    cost_qty = fields.Monetary('Costo total componente', readonly=True, copy=False,required=False, compute="_total_qty_cost")

    @api.model #ESTA FUNCION ES PARA PODER HACER SUMA DENTRO DE AGRUPACIONES O FILTROS
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(StockMoveLine, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        if 'cost_qty' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_invoice_due = 0.0
                    for record in lines:
                        total_invoice_due += record.cost_qty
                    line['cost_qty'] = total_invoice_due
        return res

    @api.depends('qty_done')
    def _total_qty_cost(self):
        for record  in self:
            record['cost_qty']=record.qty_done * record.cost_component

StockMoveLine()