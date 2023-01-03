# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class StockPicking(models.Model):
    _inherit= "stock.picking"

    def _default_currency_id(self):
        company_id = self.env.context.get('company_id') or self.env.company.id
        return self.env['res.company'].browse(company_id).currency_id    

    currency_id = fields.Many2one('res.currency', 'Monedas',default= _default_currency_id)
    sale_order_prod_id = fields.Many2one('sale.order','Presupuesto',store=True, required=False, tracking=1)
    sale_order_prod_name_id = fields.Many2one('res.partner','Cliente',related='sale_order_prod_id.partner_id', readonly=True)  
    total_mountss = fields.Monetary(compute='_amount_all_prices')
    
    @api.depends('move_line_ids_without_package.price_env_sub') # Calculo de total de factura en envio
    def _amount_all_prices(self):
        for order in self:
            sub_total_mount_abo = 0.0
            for line in order.move_line_ids_without_package:
                sub_total_mount_abo += line.price_env_sub
            order.update({
                'total_mountss' : sub_total_mount_abo,
            })