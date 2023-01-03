# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class MaintenanceEquipment(models.Model):
    _inherit= "maintenance.equipment"

    def _default_currency_id(self):
        company_id = self.env.context.get('company_id') or self.env.company.id
        return self.env['res.company'].browse(company_id).currency_id

    bom_lines= fields.One2many ('maintenances.bom', 'equip_maintenance_id', string="Repuestos a utilizar", required=False,index=True,readonly=False, copy=False)

    
    sub_total_mount = fields.Monetary(string='SubTotal', store=True, readonly=True, compute='_amount_all')
    total_mount = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all', tracking=1)
    currency_id = fields.Many2one('res.currency', 'Moneda',default= _default_currency_id)
    company_id = fields.Many2one('res.company', 'Company', required=False, default=lambda self: self.env.company.id,readonly=True)
    invoice_ids = fields.One2many('account.move', 'maintenance_equipment_id', 'Invoices')
    move_lines_ids = fields.One2many('stock.move.line','maintenance_equipment_id2','Move lines components')
    mrp_workforce_ids= fields.One2many('mrp.workforce', 'maintenance_equipment_id', 'Workforces')

    @api.depends('bom_lines')  # Calculo de los totales de abono y factura.
    def _amount_all(self):
        for order in self:
            sub_total_mount = 0.0
            for line in order.bom_lines:
                sub_total_mount += line.cost_qty
            order.update({
                'sub_total_mount': sub_total_mount,
                'total_mount': sub_total_mount,
            })


    count_account_maintenance = fields.Integer(string='Call of account count', compute='_compute_account_count')
    amount_account_maitenance = fields.Monetary(string="Amount Invoiced", compute="_compute_account_count")

    
    @api.depends('invoice_ids.amount_untaxed_signed')
    def _compute_account_count(self):
        for rec in self:
            rec.update({
                'count_account_maintenance': len(rec.invoice_ids.ids),
                #'amount_account_maitenance': abs(sum([x.amount_untaxed_signed for x in rec.invoice_ids.filtered(lambda x: x.invoice_payment_state == 'paid')])),
                'amount_account_maitenance': abs(sum([x.amount_untaxed_signed for x in rec.invoice_ids])), #SIN FILTRO DE STADOS PAGADOS
            })

    def account_move_mainte_action_open(self):
        return{
            'type':'ir.actions.act_window',
            'name':'Facturas de mantenimiento',
            'res_model':'account.move',
            'domain':[('maintenance_equipment_id','=',self.id)],
            'view_mode':'tree',
            'target':'current',
        }

#---------------------------------------------------------------------------------------------------------------------------------------

    amount_repuest_maitenance = fields.Monetary(string="Amount move lines", compute="_compute_move_lines_count")

    
    @api.depends('move_lines_ids.cost_qty')
    def _compute_move_lines_count(self):
        for rec in self:
            rec.update({
                'amount_repuest_maitenance': abs(sum([x.cost_qty for x in rec.move_lines_ids.filtered(lambda x: x.state == 'done')])),
            })

    def lines_move_mainte_action_open(self):
        return{
            'type':'ir.actions.act_window',
            'name':'Consumo de mantenimiento',
            'res_model':'stock.move.line',
            'domain':[('maintenance_equipment_id2','=',self.id)],
            'view_mode':'tree',
            'target':'current',
        }

#--------------------------------------------------------------------------------------------------------------------------------------
    amount_mrp_wokrforce = fields.Monetary(string="Amount workforce lines", compute="_compute_workforce_count")

    
    @api.depends('mrp_workforce_ids.cost_report')
    def _compute_workforce_count(self):
        for rec in self:
            rec.update({
                'amount_mrp_wokrforce': abs(sum([x.cost_report for x in rec.mrp_workforce_ids])),
            })

    def lines_workforce_action_open(self):
        return{
            'type':'ir.actions.act_window',
            'name':'Mano de obra mantenimiento',
            'res_model':'mrp.workforce',
            'domain':[('maintenance_equipment_id','=',self.id)],
            'view_mode':'tree',
            'target':'current',
        }


MaintenanceEquipment()