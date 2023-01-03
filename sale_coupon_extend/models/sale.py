# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_moves_reward(self):
        moves = self.env['stock.move']
        for record in self:
            picking_id = record.picking_ids[-1]
            for line in record.order_line.filtered(lambda r: r.is_reward_line):
                product_name = line.product_id.name.split( ' - ' )[1]
                product_id = self.env['product.product'].search(
                        ['&', ("sale_ok","=",True), ('name', '=', product_name)], limit=1)
                if not product_id:
                    raise ValidationError( _('Error. ') )
                move_id = moves.create( {
                                'name': line.product_id.name,
                                'product_id': product_id.id,
                                'product_uom': product_id.uom_id.id,
                                'product_uom_qty': line.product_uom_qty,
                                'company_id': record.company_id.id, 
                                'picking_id': picking_id.id, 
                                'picking_type_id': picking_id.picking_type_id.id, 
                                'location_id': picking_id.location_id.id, 
                                'location_dest_id': picking_id.location_dest_id.id
                                } )
                move_id._action_assign()
            picking_id.action_confirm()
            picking_id.action_assign()
        return

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        try:
            self._create_moves_reward()
        except:
            return res
        return

    