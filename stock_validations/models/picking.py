# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang


class StockPicking(models.Model):
    _inherit = "stock.picking"


    def button_validate(self):
        self.validate_move_price()
        self.validate_sale_move()
        res = super(StockPicking, self).button_validate()
        return res
    
    def validate_move_price(self):
        for pick in self:
            item = 0.00
            if pick.picking_type_id.code == 'incoming':
                if self.env.user.has_group('stock_validations.group_stock_validations'):
                    continue
                #Validation from purchase order
                for move in pick.move_ids_without_package:
                    item += 1
                    if move.purchase_line_id and not move.purchase_line_id.order_id.invoice_ids:
                        if move.purchase_line_id.order_id.partner_id.is_retroactive_invoice:
                            raise UserError(('La Orden de Compra %s,  no tiene facturas creadas') %(move.purchase_line_id.order_id.name))
                    if move.purchase_line_id and not move.purchase_line_id.order_id.date_invoice:
                        if move.purchase_line_id.order_id.partner_id.is_retroactive_invoice:
                            raise UserError(('Las facturas en la po %s,  no tienen fechas asignadas') %(move.purchase_line_id.order_id.name))
                    if move.purchase_line_id and move.purchase_line_id.price_unit == 0.00:
                        raise UserError(('La linea %s (%s),  tiene precio unitario 0.00') %(item, move.product_id.name))
        return True
    
    def validate_sale_move(self):
        for pick in self:
            #item = 0
            if pick.picking_type_id.code == 'outgoing':
                item = 0
                if self.env.user.has_group('stock_validations.group_stock_validations'):
                    continue
                for move in pick.move_ids_without_package:
                    item += 1
                    if not move.sale_line_id:
                        if move.product_id.is_promotion:
                            continue
                        if move.picking_id.sale_id:
                            order_lines_1 = move.picking_id.sale_id.order_line.filtered(lambda r : r.product_id.id == move.product_id.id)
                            if not order_lines_1:
                                raise UserError(('La linea %s  (%s), no esta en la orden de venta %s') %(item, move.product_id.name, move.picking_id.origin))
                            for so_line in order_lines_1:
                                if so_line.product_id.id == move.product_id.id:
                                    if round(move.quantity_done, 2) > (so_line.product_uom_qty - so_line.qty_delivered):
                                        raise UserError(('La linea %s  (%s), tiene cantidades mayores (%s) que en la orden de venta (%s), segun disponble de entregas (%s)') %(item, move.product_id.name, move.quantity_done, so_line.product_uom_qty, (so_line.product_uom_qty - so_line.qty_delivered)))
                                    else:
                                        continue
                                #else:
                                #    raise UserError(('La linea %s  (%s), no esta en la orden de venta %s') %(item, move.product_id.name, move.picking_id.origin))
                        else:
                            raise UserError(('La linea %s  (%s), no esta en la orden de venta %s') %(item, move.product_id.name, move.picking_id.origin))
                    if move.sale_line_id:
                        if round(move.quantity_done,2) > (move.sale_line_id.product_uom_qty - move.sale_line_id.qty_delivered):
                            raise UserError(('La linea %s  (%s), tiene cantidades mayores (%s) que en la orden de venta (%s), segun disponible de entregas (%s)') %(item, move.product_id.name, move.quantity_done, move.sale_line_id.product_uom_qty, (move.sale_line_id.product_uom_qty - move.sale_line_id.qty_delivered)))
                item = 0
                for ml in pick.move_line_ids_without_package:
                    item += 1
                    if not ml.move_id.sale_line_id:
                        if ml.product_id.is_promotion:
                            continue
                        if ml.picking_id.sale_id:
                            #raise UserError("Si hay SO")
                            order_lines_2 = ml.picking_id.sale_id.order_line.filtered(lambda r : r.product_id.id == ml.product_id.id)
                            if not order_lines_2:
                                raise UserError(('La linea %s  (%s), no esta en la orden de venta %s') %(item, ml.product_id.name, ml.picking_id.origin))
                            for so_line in order_lines_2:
                                #raise UserError("Entro al FOR")
                                if so_line.product_id.id == ml.product_id.id:
                                    #raise UserError("Hay producto igual")
                                    if round(ml.qty_done, 2) > (so_line.product_uom_qty - so_line.qty_delivered):
                                        raise UserError(('La linea %s  (%s), tiene cantidades mayores (%s) que en la orden de venta (%s), segun disponible de entregas (%s)') %(item, ml.product_id.name, ml.qty_done, so_line.product_uom_qty, (so_line.product_uom_qty - so_line.qty_delivered)))
                                    else:
                                        continue
                                #else:
                                #    raise UserError(('La linea %s  (%s), no esta en la orden de venta %s') %(item, ml.product_id.name, ml.picking_id.origin))
                        else:
                            raise UserError(('La linea %s  (%s), no esta en la orden de venta %s') %(item, ml.product_id.name, ml.picking_id.origin))
                    if ml.move_id.sale_line_id:
                        if round(ml.qty_done, 2) > (ml.move_id.sale_line_id.product_uom_qty - ml.move_id.sale_line_id.qty_delivered):
                            raise UserError(('La linea %s  (%s), tiene cantidades mayores (%s) que en la orden de venta (%s), segun disponible de entregas (%s)') %(item, ml.product_id.name, ml.qty_done, ml.move_id.sale_line_id.product_uom_qty, (ml.move_id.sale_line_id.product_uom_qty - ml.move_id.sale_line_id.qty_delivered)))
        return True
StockPicking()

class StockMove(models.Model):
    _inherit = "stock.move"

    def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
        self.ensure_one()
        AccountMove = self.env['account.move'].with_context(default_journal_id=journal_id)

        move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
        if move_lines:
            if self.purchase_line_id and self.purchase_line_id.order_id.partner_id.is_retroactive_invoice == True:
                date = self.purchase_line_id.order_id.date_invoice
            else:
                date = self._context.get('force_period_date', fields.Date.context_today(self))
            new_account_move = AccountMove.sudo().create({
                'journal_id': journal_id,
                'line_ids': move_lines,
                'date': date,
                'ref': description,
                'stock_move_id': self.id,
                'stock_valuation_layer_ids': [(6, None, [svl_id])],
                'type': 'entry',
                'branch_id': self.picking_id.branch_id.id,
            })
            new_account_move.post()
StockMove()
