from odoo import api, fields, models
from odoo.exceptions import ValidationError

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    pago_selection = [
        ('cheque_propio', 'Cheque propio'),
        ('cheque_ajeno', 'Cheque ajeno'),        
        ('transferencias', 'Transferencias'),
        ('efectivo', 'Efectivo'),
        ('nota_cargo', 'Nota de Cargo'),
        ('cheques', 'Cheques'),
    ]
    forma_pago = fields.Selection(pago_selection, 'Formas de pago')
    boleta = fields.Char('Boleta', default="0")

    type_bank = fields.Selection([
        ('agromercantil', 'Banco Agromercantil de Guatemala'),
        ('banco_bi', 'Banco Industrial'),
        ('banco_G&T', 'Banco G&T Continental'),
        ('banrural', 'Banco de Desarrollo Rural'),
        ('bac', 'Bando de America Central'),
        ('proamerica', 'Banco Proamerica'),
        ('ficohsa', 'Banco Ficohsa Guatemala'),
        ('vivibanco', 'Vivibanco'),
        ('banco_internacional', 'Banco Internacional'),        
        ('banco_trabajadores', 'Banco de los Trabajadores')], 'Banco', required=False, copy=False)

    # @api.constrains('boleta')
    # def check_journal(self):
    #     for record in self:
    #         #Search by company
    #         move = self.env['account.payment'].search([('boleta', '=', record.boleta), ('id', '!=', record.id), ('company_id', '=', record.company_id.id), ('journal_id', '=', record.journal_id.id)])
    #         if len(move) > 1 and record.company_id.name == 'Corporación CME, S.A. de C.V.':
    #             raise ValidationError('Ya existe este numero de boleta en el diario')
    #         elif len(move) == 1 and record.company_id.name == 'Corporación CME, S.A. de C.V.':
    #             if move.boleta != '0':
    #                 raise ValidationError('Ya existe este numero de boleta en el diario')
AccountPayment()

class PaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    pago_selection = [
        ('cheque_propio', 'Cheque propio'),
        ('cheque_ajeno', 'Cheque ajeno'),        
        ('transferencias', 'Transferencias'),
        ('efectivo', 'Efectivo'),
        ('nota_cargo', 'Nota de Cargo'),
        ('cheques', 'Cheques'),
    ]
    forma_pago = fields.Selection(pago_selection, 'Formas de pago')
    boleta = fields.Char('Boleta')
    # payment_type = fields.Selection([
    #     ('inbound', 'Inbound'),
    #     ('outbound', 'Outbound')], 'Type', compute="_compute_type")
    
    # @api.depends('invoice_ids')
    # def _compute_type(self):
    #     payment_type = False
    #     for rec in self:
    #         if rec.invoice_ids and rec.invoice_ids[0].is_inbound():
    #             payment_type = 'inbound'
    #         else:
    #             payment_type = 'outbound'
    #         rec.update({
    #             'payment_type': payment_type,
    #         })
                

    #@api.constrains('boleta')
    #def check_journal(self):
    #    for record in self:
    #        #Search by company
    #        move = self.env['account.payment'].search([('boleta', '=', record.boleta), ('id', '!=', record.id), ('company_id', '=', record.company_id.id), ('journal_id', '=', record.journal_id.id)])
    #        if len(move) > 1 and record.company_id.name == 'Corporación CME, S.A. de C.V.':
    #            raise ValidationError('Ya existe este numero de boleta en el diario')
    #        elif len(move) == 1 and record.company_id.name == 'Corporación CME, S.A. de C.V.':
    #            if move.boleta > 0:
    #                raise ValidationError('Ya existe este numero de boleta en el diario')


    # def _prepare_payment_vals(self, invoices):
    #     res = super(PaymentRegister, self)._prepare_payment_vals(invoices)
    #     for rec in self:
    #         if rec.payment_type == 'inbound':
    #             res.update({
    #                 'forma_pago': rec.forma_pago or False,
    #                 'boleta': rec.boleta or False, 
    #             })
    #     return res

PaymentRegister()


