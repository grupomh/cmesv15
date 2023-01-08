# -*- encoding: UTF-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2015-Today Laxicon Solution.
#    (<http://laxicon.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_is_zero
from collections import namedtuple


class StockRule(models.Model):
    _inherit = 'stock.rule'

    action = fields.Selection(selection_add=[('split_procurement', 'Choose between MTS and MTO')])
    mts_rule_id = fields.Many2one('stock.rule', string="MTS Rule")
    mto_rule_id = fields.Many2one('stock.rule', string="MTO Rule")

    @api.constrains('action', 'mts_rule_id', 'mto_rule_id')
    def _check_mts_mto_rule(self):
        for rule in self:
            if rule.action == 'split_procurement':
                if not rule.mts_rule_id or not rule.mto_rule_id:
                    msg = _('No MTS or MTO rule configured on procurement rule: %s!') % (rule.name, )
                    raise ValidationError(msg)
                if (rule.mts_rule_id.location_src_id.id !=
                        rule.mto_rule_id.location_src_id.id):
                    msg = _('Inconsistency between the source locations of '
                            'the mts and mto rules linked to the procurement '
                            'rule: %s! It should be the same.') % (rule.name,)
                    raise ValidationError(msg)

    def get_mto_qty_to_order(self, product, product_qty, product_uom, values):
        self.ensure_one()
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        src_location_id = self.mts_rule_id.location_src_id.id
        product_location = product.with_context(location=src_location_id)
        virtual_available = product_location.virtual_available
        qty_available = product.uom_id._compute_quantity(virtual_available, product_uom)
        if float_compare(qty_available, 0.0, precision_digits=precision) > 0:
            if float_compare(qty_available, product_qty, precision_digits=precision) >= 0:
                return 0.0
            else:
                return product_qty - qty_available
        return product_qty

    @api.model
    def _run_split_procurement(self, procurements):
        Procurement_mts = namedtuple('Procurement_mts', ['product_id', 'product_qty', 'product_uom', 'location_id', 'name', 'origin', 'company_id', 'values'])
        Procurement_needed = namedtuple('Procurement_needed', ['product_id', 'product_qty', 'product_uom', 'location_id', 'name', 'origin', 'company_id', 'values'])
        for procurement in procurements:
            product_id = procurement[0][0]
            product_qty = procurement[0][1]
            product_uom = procurement[0][2]
            location_id = procurement[0][3]
            name = procurement[0][4]
            origin = procurement[0][5]
            company_id = procurement[0][6]
            values = procurement[0][7]

            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            needed_qty = procurement[1].get_mto_qty_to_order(product_id, product_qty, product_uom, values)
            if float_is_zero(needed_qty, precision_digits=precision):
                getattr(procurement[1].mts_rule_id, '_run_%s' % procurement[1].mts_rule_id.action)(([procurement]))
            elif float_compare(needed_qty, product_qty, precision_digits=precision) == 0.0:
                getattr(procurement[1].mto_rule_id, '_run_%s' % procurement[1].mto_rule_id.action)(([procurement]))
            else:
                mts_qty = product_qty - needed_qty
                print ("mts_qty", mts_qty)
                print ("product_qty", product_qty)
                print ("needed_qty", needed_qty)
                # original
                # Procurement_mts = Procurement_mts(product_id, mts_qty, product_uom, location_id, name, origin, company_id, values)
                Procurement_mts = Procurement_mts(product_id, needed_qty, product_uom, location_id, name, origin, company_id, values)
                pro_mts = procurement[1]
                final_mts = tuple([Procurement_mts, pro_mts])
                getattr(procurement[1].mts_rule_id, '_run_%s' % procurement[1].mts_rule_id.action)([final_mts])
                # for need qty

                # original
                # Procurement_needed = Procurement_needed(product_id, needed_qty, product_uom, location_id, name, origin, company_id, values)
                Procurement_needed = Procurement_needed(product_id, mts_qty, product_uom, location_id, name, origin, company_id, values)
                pro_need_qty = procurement[1].mto_rule_id
                final_need_qty = tuple([Procurement_needed, pro_need_qty])
                getattr(procurement[1].mto_rule_id, '_run_%s' % procurement[1].mto_rule_id.action)([final_need_qty])
        return True
