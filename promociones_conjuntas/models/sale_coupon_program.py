from odoo import api, fields, models

class SaleCouponProgram(models.Model):
    _inherit = "coupon.program"

    conjunta = fields.Boolean(string='Es conjunta?', default=False)

    def _filter_not_ordered_reward_programs(self, order):
        programs = self.env['sale.coupon.program']
        for program in self:
            if program.reward_type == 'product' and program.conjunta:
                programs = program
            elif program.reward_type == 'product' and \
                    not order.order_line.filtered(lambda line: line.product_id == program.reward_product_id):
                continue
            elif program.reward_type == 'discount' and program.discount_apply_on == 'specific_products' and \
                    not order.order_line.filtered(
                        lambda line: line.product_id in program.discount_specific_product_ids):
                continue
            programs |= program
        return programs


class SaleOrder(models.Model):
    _inherit = "sale.order"


