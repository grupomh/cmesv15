# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import fields, models, api
from datetime import datetime

        
class sale_order(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection([
            ('draft', 'Draft Quotation'),
            ('sent', 'Quotation Sent'),
            ('sale', 'Sale Order'),
            ('to approve', 'To Approve'),
            ('cancel', 'Cancelled'),
            ('done', 'Locked'),
            ], string='Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True)


    
    def action_confirm(self):
        so_double_validation_amount=self.env['ir.config_parameter'].sudo().get_param('sale_approve.so_double_validation_amount')
        so_order_approval = self.env['ir.config_parameter'].sudo().get_param('sale_approve.so_order_approval')
        self.validate_limit_credit()    
        self.action_send_aprobe()
        
        if so_order_approval == "True"  and self.amount_total > float(so_double_validation_amount) :
            self.write({'state': 'to approve'})
            return


        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'date_order': fields.Datetime.now()
        })
        self._action_confirm()        
        if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
            self.action_done()        
        return True


    
    def button_toapprove(self):
        self.action_send_aprobe_two()
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'date_order': fields.Datetime.now()
        })
        self._action_confirm()
        if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
            self.action_done()        
        return True



    
    def button_unlock(self):
        self.write({'state': 'sale'})


    
    def _track_subtype_approve(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'to approve':
            return 'sale.mt_order_toapprove'
        if 'state' in init_values and self.state == 'sale':
            return 'sale.mt_order_confirmed'
        elif 'state' in init_values and self.state == 'sent':
            return 'sale.mt_order_sent'
        return super(SaleOrder, self)._track_subtype(init_values)


    def action_send_aprobe(self):   #Accion para enviar correo cuando se confirma
        for rec in self:
            ctx = {}
            email_list = rec.partner_id.user_id.employee_id.parent_id.work_email
            if email_list:
                ctx['email_to'] = email_list
                ctx['send_email'] = True
                template = self.env.ref('sale_approve.email_send_approve')
                template.with_context(ctx).send_mail(self.id, force_send=True, raise_exception=False)

    def action_send_aprobe_two(self):   #Accion para enviar correo cuando se aprueba
        for rec in self:
            ctx = {}
            email_list = rec.partner_id.user_id.employee_id.parent_id.work_email
            if email_list:
                ctx['email_to'] = email_list
                ctx['send_email'] = True
                template = self.env.ref('sale_approve.email_send_approve_two')
                template.with_context(ctx).send_mail(self.id, force_send=True, raise_exception=False)


class SaleConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'


    so_order_approval = fields.Boolean(string= 'SO Approval')
    so_double_validation_amount = fields.Monetary( string="Double validation amount *", currency_field='company_currency_id', default=5000)     
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True,
        help='Utility field to express amount currency')



    def get_values(self):


        res = super(SaleConfiguration, self).get_values()
        

        res.update(
            so_order_approval = self.env['ir.config_parameter'].sudo().get_param('sale_approve.so_order_approval'),
            so_double_validation_amount=float(self.env['ir.config_parameter'].sudo().get_param('sale_approve.so_double_validation_amount'))
        )
        return res

    def set_values(self):
        super(SaleConfiguration, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('sale_approve.so_order_approval', self.so_order_approval)
        self.env['ir.config_parameter'].sudo().set_param('sale_approve.so_double_validation_amount', self.so_double_validation_amount)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id', 'product_uom_qty', 'qty_delivered', 'state', 'product_uom')
    def _compute_qty_to_deliver(self):
        """Compute the visibility of the inventory widget."""
        for line in self:
            line.qty_to_deliver = line.product_uom_qty - line.qty_delivered
            if line.state in ['draft', 'to approve'] and line.product_type == 'product' and line.product_uom and line.qty_to_deliver > 0:
                line.display_qty_widget = True
            else:
                line.display_qty_widget = False

SaleOrderLine()

   



