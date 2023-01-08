# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    product_reprocess_id = fields.Many2one(
        'product.product', 'Producto Reproceso', domain="[('type', 'in', ['product', 'consu']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        required=False, states={'done': [('readonly', True)]}, check_company=True)
    product_reprocess_uom_id = fields.Many2one(
        'uom.uom', 'UOM Reproceso',
        required=False, states={'done': [('readonly', True)]}, domain="[('category_id', '=', product_uom_category_id)]")
    product_reprocess_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    reprocess_location_id = fields.Many2one('stock.location', 'Scrap Location', domain="[('usage', '=', 'internal'), ('company_id', 'in', [company_id, False])]", required=False, states={'done': [('readonly', True)]}, check_company=True)
    reprocess_qty = fields.Float('Cantidad reprocesada', default=1.0, required=False, states={'done': [('readonly', True)]})
    is_reprocess = fields.Boolean('Reproceso', default=False)

    @api.onchange('product_reprocess_id')
    def onchange_product_reprocess(self):
        if self.product_reprocess_id:
            self.product_reprocess_uom_id = self.product_reprocess_id.uom_id.id

    def do_scrap(self):
        res = super(StockScrap, self).do_scrap()
        for scrap in self:
            if scrap.is_reprocess == True:
                move = self.env['stock.move'].create(scrap._prepare_move_values_reprocessing())
                move._action_done()
        return res

    def _prepare_move_values_reprocessing(self):
        self.ensure_one()
        location_id = self.reprocess_location_id.id
        if self.picking_id and self.picking_id.picking_type_code == 'incoming':
            location_id = self.picking_id.location_dest_id.id
        return {
            'name': self.name,
            'created_production_id': self.production_id.id,
            'production_id': self.production_id.id,
            'picking_type_id': self.production_id.picking_type_id.id,
            'origin': self.production_id.name or self.origin,
            'company_id': self.company_id.id,
            'product_id': self.product_reprocess_id.id,
            'product_uom': self.product_reprocess_uom_id.id,
            'state': 'draft',
            'product_uom_qty': self.reprocess_qty,
            'location_id': self.scrap_location_id.id,
            'scrapped': False,
            'location_dest_id': location_id,
            'price_unit': self.product_id.standard_price,
            'group_id': self.production_id.procurement_group_id.id,
            'move_line_ids': [(0, 0, {'product_id': self.product_reprocess_id.id,
                                           'product_uom_id': self.product_reprocess_uom_id.id, 
                                           'qty_done': self.reprocess_qty,
                                           'production_id': self.production_id.id,
                                           'location_id': self.scrap_location_id.id,
                                           'location_dest_id': location_id,
                                           'package_id': self.package_id.id, 
                                           'owner_id': self.owner_id.id,
                                           'lot_id': self.lot_id.id, })],
#             'restrict_partner_id': self.owner_id.id,
            'picking_id': self.picking_id.id
        }

StockScrap()