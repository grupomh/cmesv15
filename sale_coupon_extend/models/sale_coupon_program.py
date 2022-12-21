# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleCouponProgram(models.Model):
    _inherit = 'coupon.program'

    rule_max_quantity = fields.Integer(string="Maximum Quantity", default=1,
        help="Maximum required product quantity to get the reward")

    def _filter_programs_on_products(self, order):
        order_lines = order.order_line.filtered(lambda line: line.product_id) - order._get_reward_lines()
        products = order_lines.mapped('product_id')
        products_qties = dict.fromkeys(products, 0)
        for line in order_lines:
            products_qties[line.product_id] += line.product_uom_qty
        valid_programs = self.filtered(lambda program: not program.rule_products_domain)
        for program in self - valid_programs:
            valid_products = program._get_valid_products(products)
            ordered_rule_products_qty = sum(products_qties[product] for product in valid_products)
            # Avoid program if 1 ordered foo on a program '1 foo, 1 free foo'
            if program.promo_applicability == 'on_current_order' and \
               program._is_valid_product(program.reward_product_id) and program.reward_type == 'product':
                ordered_rule_products_qty -= program.reward_product_quantity
            if ordered_rule_products_qty >= program.rule_min_quantity and ordered_rule_products_qty <= program.rule_max_quantity:
                valid_programs |= program
        return valid_programs

    def _check_promo_code(self, order, coupon_code):
        message = {}
        applicable_programs = order._get_applicable_programs()
        if self.maximum_use_number != 0 and self.order_count >= self.maximum_use_number:
            message = {'error': _('Promo code %s has been expired.') % (coupon_code)}
        elif not self._filter_on_mimimum_amount(order):
            message = {'error': _('A minimum of %s %s should be purchased to get the reward') % (
            self.rule_minimum_amount, self.currency_id.name)}
        elif self.promo_code and self.promo_code == order.promo_code:
            message = {'error': _('The promo code is already applied on this order')}
        elif not self.promo_code and self in order.no_code_promo_program_ids:
            message = {'error': _('The promotional offer is already applied on this order')}
        elif not self.active:
            message = {'error': _('Promo code is invalid')}
        elif self.rule_date_from and self.rule_date_from > order.date_order or self.rule_date_to and order.date_order > self.rule_date_to:
            message = {'error': _('Promo code is expired')}
        elif order.promo_code and self.promo_code_usage == 'code_needed':
            message = {'error': _('Promotionals codes are not cumulative.')}
        elif self._is_global_discount_program() and order._is_global_discount_already_applied():
            message = {'error': _('Global discounts are not cumulative.')}
        elif self.promo_applicability == 'on_current_order' and self.reward_type == 'product':
            if not order._is_reward_in_order_lines(self):
                message = {'error': _('The reward products should be in the sales order lines to apply the discount.')}

        elif not self._is_valid_partner(order.partner_id):
            message = {'error': _("The customer doesn't have access to this reward.")}
        elif not self._filter_programs_on_products(order):
            message = {'error': _(
                "You don't have the required product quantities on your sales order. If the reward is same product quantity, please make sure that all the products are recorded on the sales order (Example: You need to have 3 T-shirts on your sales order if the promotion is 'Buy 2, Get 1 Free'.")}
        else:
            if self not in applicable_programs and self.promo_applicability == 'on_current_order':
                message = {'error': _('At least one of the required conditions is not met to get the reward!')}
        return message






class SaleOrder(models.Model):
    _inherit = "sale.order"
    def _is_reward_in_order_lines(self, program):
        if self.order_line.filtered(lambda line: line.product_id == program.reward_product_id and line.product_uom_qty > 0) and program.conjunta:
            for line in self.order_line:
                if line.product_id == program.reward_product_id:
                    if line.product_uom_qty < program.reward_product_quantity:
                        line.product_uom_qty = program.reward_product_quantity
            return True
        elif self.order_line.filtered(lambda line: line.product_id == program.reward_product_id and line.product_uom_qty >= program.reward_product_quantity):
            return True
        elif program.conjunta:
            self.env['sale.order.line'].create({
                'order_id': self.id,
                'name': program.reward_product_id.name,
                'invoice_status': 'no',
                'price_unit': program.reward_product_id.product_tmpl_id.list_price,
                'product_id': program.reward_product_id.id,
                'product_uom_qty': program.reward_product_quantity
            })
            return True
        else:
            return False


    def _get_reward_values_product(self, program):
        price_unit = self.order_line.filtered(lambda line: program.reward_product_id == line.product_id)[0].price_reduce

        order_lines = (self.order_line - self._get_reward_lines()).filtered(
            lambda x: program._is_valid_product(x.product_id))
        max_product_qty = sum(order_lines.mapped('product_uom_qty')) or 1
        # Remove needed quantity from reward quantity if same reward and rule product
        if program._is_valid_product(program.reward_product_id):
            # number of times the program should be applied
            program_in_order = max_product_qty // (program.rule_min_quantity + program.reward_product_quantity)
            # multipled by the reward qty
            reward_product_qty = program.reward_product_quantity * program_in_order
            # do not give more free reward than products
            if len(program.reward_product_id) > 1:
                program.reward_product_id = program.reward_product_id[0]


            reward_product_qty = min(reward_product_qty, self.order_line.filtered(
                lambda x: x.product_id == program.reward_product_id).product_uom_qty)
            if program.rule_minimum_amount:
                order_total = sum(order_lines.mapped('price_total')) - (
                            program.reward_product_quantity * program.reward_product_id.lst_price)
                reward_product_qty = min(reward_product_qty, order_total // program.rule_minimum_amount)
        else:
            reward_product_qty = min(max_product_qty, self.order_line.filtered(
                lambda x: x.product_id == program.reward_product_id).product_uom_qty)

        reward_qty = min(int(int(max_product_qty / program.rule_min_quantity) * program.reward_product_quantity),
                         reward_product_qty)
        # Take the default taxes on the reward product, mapped with the fiscal position
        taxes = program.reward_product_id.taxes_id
        if self.fiscal_position_id:
            taxes = self.fiscal_position_id.map_tax(taxes)
        return {
            'product_id': program.discount_line_product_id.id,
            'price_unit': - price_unit,
            'product_uom_qty': reward_qty,
            'is_reward_line': True,
            'name': _("Free Product") + " - " + program.reward_product_id.name,
            'product_uom': program.reward_product_id.uom_id.id,
            'tax_id': [(4, tax.id, False) for tax in taxes],
        }