from odoo import api, models, fields
class AccountMove(models.Model):
    _inherit = 'account.move'
    
    name_concat = fields.Char(invisible = True, string="Name concatenate")
    force_name = fields.Char(string = "Factura No:")
    
    @api.depends('company_id','journal_id','force_name')
    def action_post(self):
        res = super(AccountMove,self).action_post()
        for invoice in self:
            if (invoice.company_id.id == 4 and invoice.journal_id.type == 'sale') and invoice.force_name:
                new_name = (invoice.journal_id.serie if invoice.journal_id and invoice.journal_id.serie else "") + (invoice.force_name if invoice.force_name else "")
                invoice.update({'name_concat': new_name,'name': new_name})

            elif invoice.journal_id.type == 'purchase' and invoice.force_name:
                invoice.update({'name_concat': invoice.force_name,'name': invoice.force_name})
                
            elif invoice.company_id.id != 4 and  invoice.force_name:
                invoice.update({'name_concat': invoice.force_name,'name': invoice.force_name})

            else:
                invoice.update({'name_concat': ''})
        return res
    
    def button_draft(self):
        for invoice in self:
            if invoice.company_id != 4 and not invoice.force_name:
                invoice.update({'force_name':invoice.name})
                invoice.update({'state':'draft'})
                invoice.update({'name':'/'})
            else:
                invoice.update({'name': '/'})
        return super(AccountMove,self).button_draft()

    def button_cancel(self):
        for invoice in self:
            if invoice.force_name:
                invoice.update({'name':invoice.force_name})
            return super(AccountMove,self).button_cancel()





        


    
