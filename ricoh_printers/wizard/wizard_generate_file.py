# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError
#import cStringIO
import base64
from odoo.addons.ricoh_printers import numero_a_texto
import json

class WizardGenerateFile(models.TransientModel):
    _name = 'wizard.generate.file'
    _description = 'Wizard to Generate File'

    txt_filename = fields.Char('Archivo', required=False, readonly=True, copy=False)
    file = fields.Binary('Archivo', required=False, readonly=True, copy=False)
    invoice_ids = fields.Many2many('account.move', 'rel_invoice_wizard', 'inv_id', 'wizard_id', string="Documentos")


    @api.model
    def default_get(self, fields):
        res = super(WizardGenerateFile, self).default_get(fields)
        res_id = self._context.get('active_ids')
        res_model = self._context.get('active_model')
        #res.update({'res_id': res_id, 'res_model': res_model})
        if res_id and res_model == 'account.move':
            records = self.env[res_model].browse(res_id)
            #text = "prueba de archivo"
            res.update({
                'invoice_ids': records.ids or False,
                #'file': base64.encodestring(str(text).encode('utf-8')),
                #'txt_filename': 'ricoh_file.txt',
            })
        return res

    def generate_file(self):
        view_id = self.env.ref('ricoh_printers.wizard_generate_file_form').id
        res_text = ""
        res_json = ""
        for rec in self:
            #for item in range(0,10):
            #    texto += '\t' + "prueba de texto" + str(item) + '\n'
            res_text = self.generate_text(invoice_ids=rec.invoice_ids)
            if res_text:
                res_json = json.dumps(res_text, indent = 4) 
                rec.write({
                    'txt_filename': ("ricoh_file.json"),
                    'file': base64.encodestring(str(res_json).encode('utf-8')),
                })
            return {
                'name': _('Ricoh Files'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'wizard.generate.file',
                'view_id': view_id,
                'res_id': rec.id,
                'views': [(view_id, 'form')],
                'target': 'new',
                'context': {}
            }

    def generate_text(self, invoice_ids=None):
        text = ""
        invoice_dict = {}
        print_count = 0
        for inv in invoice_ids:
            print_count = inv.count_print
            #inv.write({
            #    'count_print' : (print_count + 1),
            #})
            if inv.journal_id.ricoh_type:
                #text += '\t' + str(inv.journal_id.ricoh_type) + '\n'
                #text += '\t' + str(inv.journal_id.ricoh_type) + '\n'
                invoice_dict.update({
                    'TIPO': str(inv.journal_id.ricoh_type),
                })
            if inv.journal_id.resolution_number:
                #text += 'RES: ' + str(inv.journal_id.resolution_number) + '\n'
                invoice_dict.update({
                    'RES' : str(inv.journal_id.resolution_number) 
                })
            if inv.name and '/' in inv.name:
                number = inv.name.split('/')
                #text += 'NDO: ' + str(number[2]) + '\n'
                invoice_dict.update({
                    'NDO': str(number[2]),
                })
            if inv.invoice_date:
                #text += 'DAT: ' + str(inv.invoice_date.strftime("%d/%m/%Y")) + '\n'
                invoice_dict.update({
                    'DAT': str(inv.invoice_date.strftime("%d/%m/%Y")),
                })
            if inv.invoice_date_due:
                #text += 'DUE: ' + str(inv.invoice_date_due.strftime("%d/%m/%Y")) + '\n'
                invoice_dict.update({
                    'DUE': str(inv.invoice_date_due.strftime("%d/%m/%Y")),
                })
            if inv.invoice_user_id:
                #text += 'SALE: ' + str(inv.invoice_user_id.name) + '\n'
                invoice_dict.update({
                    'SALE': str(inv.invoice_user_id.name),
                })
            if inv.partner_id:
                street = ""
                #if inv.partner_id.code:
                #    text += 'IDC: ' + str(inv.partner_id.code) + '\n'
                #else:
                #Id del cliente
                #text += 'IDC: ' + str(inv.partner_id.id) + '\n'
                #text += 'CUS: ' + str(inv.partner_id.name) + '\n'
                invoice_dict.update({
                    'IDC': str(inv.partner_id.id),
                    'CUS': str(inv.partner_id.name),
                })
                if inv.partner_id.street:
                    street += inv.partner_id.street + ','
                if inv.partner_id.street2:
                    street += inv.partner_id.street2 + ','
                if inv.partner_id.city_id:
                    street += inv.partner_id.city_id.name + ','
                if inv.partner_id.state_id:
                    street += inv.partner_id.state_id.name + ','
                if inv.partner_id.country_id:
                    street += inv.partner_id.country_id.name
                #text += 'ADRE: ' + str(street) + '\n'
                invoice_dict.update({
                    'ADRE': str(street),
                })
                if inv.partner_id.nrc:
                    #text += 'REG: ' + str(inv.partner_id.nrc) + '\n'
                    #text += 'GIRO: ' + str(inv.partner_id.nrc) + '\n'
                    invoice_dict.update({
                        'REG': str(inv.partner_id.nrc),
                        'GIRO': str(inv.partner_id.category_id[0].name if inv.partner_id.category_id else ""),
                    })
                if inv.partner_id.vat:
                    #text += 'N.I.T: ' + str(inv.partner_id.vat) + '\n'
                    invoice_dict.update({
                        'N.I.T': str(inv.partner_id.vat),
                    })
            if inv.invoice_payment_term_id:
                #text += 'TER: ' + str(_(inv.invoice_payment_term_id.name)) + '\n'
                invoice_dict.update({
                    'TER': str(_(inv.invoice_payment_term_id.name)),
                })
            if inv.partner_id and inv.partner_id.phone:
                #text += 'TEL: ' + str(inv.partner_id.phone) + '\n'
                invoice_dict.update({
                    'TEL': str(inv.partner_id.phone),
                })
            if inv.narration:
                #text += 'NOT: ' + str(inv.narration) + '\n'
                invoice_dict.update({
                    'NOT': str(inv.narration),
                    'PRINTER': 'P1NVL', 
                    'EMPRE': str(inv.company_id.name),
                    'SUCUR': str(inv.branch_id.name),
                })
            #text += 'FINHEADER' + '\n'
            detalle_dict = {}
            detalle_list = []
            item = 0
            for line in inv.invoice_line_ids:
                item += 1
                #text += '\t' + str(line.product_id.default_code) + '\t' + str(line.quantity) + '\t' + str(line.name)  + '\t' + str(line.price_unit)  + '\t' + str(inv.branch_id.name) + '\t' + str(line.price_total) + '\n'
                detalle_dict.update({
                    'ITEM': str(item),
                    'CODIGO': str(line.product_id.default_code),
                    'DESCRIPCION': str(line.product_id.name),
                    'TIENDA': str(inv.branch_id.name),
                    'CANT': str(line.quantity),
                    'PUNI': str(line.price_unit),
                    'SUBTOTAL': str(line.price_total),
                })
                detalle_list.append(detalle_dict)
            invoice_dict.update({
                'DETALLE': detalle_list,
                'SON:': str(numero_a_texto.Numero_a_Texto(inv.amount_total)),
                'SUM': str(round(inv.amount_untaxed, 2)),
                'IVA': str(round(inv.amount_tax, 2)),
                'SUB': str(round((inv.amount_untaxed + inv.amount_tax), 2)),
                'PER': 0.00,
                'TOT': str(round(inv.amount_total, 2)),
            })
            inv.write({
                'count_print' : (print_count + 1),
            })
        return invoice_dict
                
WizardGenerateFile()