# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"
    _description = "Add maintenance"
    _rec_name = 'pre_cod'

    def _default_currency_id(self):
        company_id = self.env.context.get('company_id') or self.env.company.id
        return self.env['res.company'].browse(company_id).currency_id

    type_ope_picking = fields.Many2one(
        'stock.picking.type', string="Tipo de operacion", copy=False)
    count_consu_repuest = fields.Integer(
        string='Consumo de repuestos count', compute='_compute_consu_repuest_count')
    picking_ids = fields.One2many(
        'stock.picking', 'maintenance_request_id', 'Picking')
    maintenance_type = fields.Selection(
        selection_add=[('predictive', 'Predictivo')])
    prev_cosul = fields.Selection([
        ('mayor', 'Mayor'),
        ('menor', 'Menor'), ], 'Tipo preventivo', copy=False)
    cod_type_maint = fields.Char(
        string='codigo tipo', copy=False, compute="select_type_cod_mainte_", readonly=True)
    cod_complete = fields.Char(
        string="Codigo completo", compute='_conca_cod_complete')
    pre_cod = fields.Char('auto generado', copy=False,
                          default=lambda self: _('New'), readonly=True)

    company_id = fields.Many2one('res.company', 'Company', required=False,
                                 default=lambda self: self.env.company.id, readonly=True)
    currency_id = fields.Many2one(
        'res.currency', 'Moneda', default=_default_currency_id, readonly=True)
    invoice_ids = fields.One2many(
        'account.move', 'maintenance_request_id', 'Invoices')
    move_lines_ids = fields.One2many(
        'stock.move.line', 'maintenance_request_id2', 'Move lines')
    mrp_workforce_ids = fields.One2many(
        'mrp.workforce', 'maintenance_request_id', 'Workforce lines')
    sum_total = fields.Monetary('Total', copy=False, compute="sum_total_cost_")


# ----------------------------------Button Pedidos de repuestos cuando ya eta creado-------------------------------------------------------------------------


    @api.depends('picking_ids.picking_type_id')
    def _compute_consu_repuest_count(self):
        for rec in self:
            rec.update({
                'count_consu_repuest': len(rec.picking_ids.ids),
            })

    def maintenance_consu_repuest_action_open_(self):
        self.ensure_one()
        action = {
            'name': _('Consumos de repuesto'),
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'context': {'default_maintenance_equipment_id': self.equipment_id.id,
                        'default_maintenance_request_id': self.id,
                        'default_company_id': self.company_id.id
                        },
            # 'target': 'new',
            'domain': [('maintenance_request_id', '=', self.id)],
        }
        if self.count_consu_repuest == 1:
            repues_consu = self.env['stock.picking'].search(
                [('maintenance_request_id', '=', self.id)])
            action['view_mode'] = 'form'
            action['res_id'] = repues_consu.id
        return action

# ---------------------------------------------------------------------------------------------------------------------------------------------

    @api.depends("maintenance_type")  # logica
    def select_type_cod_mainte_(self):
        for rec in self:
            if rec.maintenance_type == 'preventive':
                rec.cod_type_maint = "PV"
            elif rec.maintenance_type == 'predictive':
                rec.cod_type_maint = "PD"
            else:
                rec.cod_type_maint = "CT"

    def button_consu_repuest_action(self):
        self.ensure_one()
        return {
            'name': _('New Consumo de repuestos'),
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'context': {
                'default_company_id': self.company_id.id,
                'default_maintenance_equipment_id': self.equipment_id.id,
                'default_partner_id': self.user_id.partner_id.id,
                'default_picking_type_id': self.type_ope_picking.id,
                'default_maintenance_request_id': self.id,
            },
            'domain': [('maintenance_equipment_id', '=', self.id)],
        }

    @api.model  # INCREMENTAL QUE LE DA UN CODIGO A LA PETICION DE MANTENIMIENTO
    def create(self, vals):
        if vals.get('pre_cod', _('New')) == _('New'):
            vals['pre_cod'] = self.env['ir.sequence'].next_by_code(
                'maintenance.request') or _('New')
        res = super(MaintenanceRequest, self).create(vals)
        return res

    @api.onchange("equipment_id")
    def _conca_cod_complete(self):
        for rec in self:
            rec.cod_complete = rec.cod_type_maint + " - " + rec.pre_cod

    @api.depends("sum_total")  # logica
    def sum_total_cost_(self):
        for rec in self:
            rec.sum_total = rec.amount_account_maitenance + \
                rec.amount_repuest_maitenance + rec.amount_mrp_wokrforce

# -------------------------------------------------------------------------------------------------------------------------------------------------
    amount_account_maitenance = fields.Monetary(
        string="Amount Invoiced", compute="_compute_account_count")

    @api.depends('invoice_ids.amount_untaxed_signed')
    def _compute_account_count(self):
        for rec in self:
            rec.update({
                # SIN FILTRO DE STADOS PAGADOS
                'amount_account_maitenance': abs(sum([x.amount_untaxed_signed for x in rec.invoice_ids])),
            })

    def account_move_mainte_action_open(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facturas de mantenimiento',
            'res_model': 'account.move',
            'domain': [('maintenance_request_id', '=', self.id)],
            'view_mode': 'tree',
            'target': 'current',
        }

# ------------------------------------------------------------------------------------------------------------------------------------------------
    amount_repuest_maitenance = fields.Monetary(
        string="Amount move lines", compute="_compute_move_lines_count")

    @api.depends('move_lines_ids.cost_qty')
    def _compute_move_lines_count(self):
        for rec in self:
            rec.update({
                'amount_repuest_maitenance': abs(sum([x.cost_qty for x in rec.move_lines_ids.filtered(lambda x: x.state == 'done')])),
            })

    def lines_move_mainte_action_open(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Consumo de mantenimiento',
            'res_model': 'stock.move.line',
            'domain': [('maintenance_request_id2', '=', self.id)],
            'view_mode': 'tree',
            'target': 'current',
        }

    # -----------------------------------------------------------------------------------------------------------------------------------------------
    amount_mrp_wokrforce = fields.Monetary(
        string="Amount workforce lines", compute="_compute_workforce_count")

    @api.depends('mrp_workforce_ids.cost_report')
    def _compute_workforce_count(self):
        for rec in self:
            rec.update({
                'amount_mrp_wokrforce': abs(sum([x.cost_report for x in rec.mrp_workforce_ids])),
            })

    def lines_workforce_action_open(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Mano de obra mantenimiento',
            'res_model': 'mrp.workforce',
            'domain': [('maintenance_request_id', '=', self.id)],
            'view_mode': 'tree',
            'target': 'current',
        }

    # -----------------------------------------------------------------------------------------------------------------------------------------------------
    @api.model  # ESTA FUNCION ES PARA PODER HACER SUMA DENTRO DE AGRUPACIONES O FILTROS
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(MaintenanceRequest, self).read_group(
            domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        if 'amount_account_maitenance' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_account_due = 0.0
                    total_repuest_due = 0.0
                    for record in lines:
                        total_account_due += record.amount_account_maitenance
                        total_repuest_due += record.amount_repuest_maitenance
                    line['amount_account_maitenance'] = total_account_due
                    line['amount_repuest_maitenance'] = total_repuest_due
        return res
