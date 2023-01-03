# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
class StockQuant(models.Model):
    _inherit = "stock.quant"

    description=fields.Html(string="Descripcion",copy=False, related='product_id.description')

    @api.model
    def action_view_quants_r(self):
        self = self.with_context(search_default_internal_loc=1)
        if self.user_has_groups('stock.group_production_lot,stock.group_stock_multi_locations'):
            # fixme: erase the following condition when it'll be possible to create a new record
            # from a empty grouped editable list without go through the form view.
            if self.search_count([
                ('company_id', '=', self.env.company.id),
                ('location_id.usage', 'in', ['internal', 'transit']),

            ]):
                self = self.with_context(
                    search_default_productgroup=1,
                    search_default_locationgroup=1
                )
        if not self.user_has_groups('stock.group_stock_multi_locations'):
            company_user = self.env.company
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_user.id)], limit=1)
            if warehouse:
                self = self.with_context(default_location_id=warehouse.lot_stock_id.id)

        # If user have rights to write on quant, we set quants in inventory mode.
        if self.user_has_groups('stock.group_stock_manager'):
            self = self.with_context(inventory_mode=True)
        return self._get_quants_action(extend=True)

StockQuant()