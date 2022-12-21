# -*- coding: utf-8 -*-


from odoo import fields, models, api, _
from odoo.exceptions import UserError
import base64
from odoo.addons.ricoh_printers import numero_a_texto
import json

import logging

_logger = logging.getLogger( __name__ )


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    count_print = fields.Integer('Contador', readonly=True, default=0)

    def print_ricoh_files(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        counter = 0
        for rec in self:
            res_text = {}
            if rec.type in ('out_invoice', 'out_refund'):
                if rec.journal_id and rec.journal_id.ricoh_type == 'FCFE':
                    res_text = rec.generate_json_exento()
                else:
                    res_text = rec.generate_json()
            if rec.type in ('in_invoice', 'in_refund'):
                if rec.journal_id.ricoh_type == 'FSE':
                    res_text = rec.generate_json_fse()
                else:
                    res_text = rec.generate_json_purchase()
                #raise UserError(('%s') %(res_text))
            if res_text:
                res_json = json.dumps(res_text, indent = 4)
                rec.validate_prints()
                #counter = rec.count_print + 1
                rec.write({
                    'txt_filename': (("%s.json") %(rec._get_report_base_filename())),
                    'file': base64.encodestring(str(res_json).encode('utf-8')),
                })
                return {
                    'type': 'ir.actions.act_url',
                    'name': 'Ricoh Files',
                    'url': base_url + "/web/content/?model=" + "account.move" +"&id=" + str(rec.id) + "&filename_field=file_name&field=file&download=true&filename=" + str(rec.txt_filename),
                    'target': 'self',
                }

    def validate_prints(self):
        #print_count = 0
        for rec in self:
            if rec.count_print == 0:
                rec.write({
                    'count_print' : (rec.count_print + 1),
                    })
                continue
            if rec.count_print > 0:
                if self.env.user.has_group('ricoh_printers.group_ricoh_reprint'):
                    continue
                else:
                    raise UserError(('%s, no tiene autorizado a reimprimir plantillas de Ricoh') %(self.env.user.name))
            
    def generate_json(self):
        text = ""
        invoice_dict = {}
        print_count = 0
        multiplier = 1.00
        for inv in self:
            if inv.type == 'out_refund':
                multiplier = -1.
                #if inv.invoice_refund_id:
                #    invoice_dict.update({
                #        'REF': str(inv.invoice_refund_id.name),
                #    })
            #print_count = inv.count_print
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
                    'RES' : str(inv.journal_id.serie) 
                })
            if inv.force_name:
                invoice_dict.update({
                    'NDO': str(inv.force_name),
                })
            else:
                if inv.name and '/' in inv.name:
                    number = inv.name.split('/')
                    #text += 'NDO: ' + str(number[2]) + '\n'
                    invoice_dict.update({
                        'NDO': str(number[2]),
                    })
                elif inv.name and '-' in inv.name:
                    number = inv.name.split('-')
                    invoice_dict.update({
                        'NDO': str(number[2]),
                        })
                else:
                    invoice_dict.update({
                        'NDO': str(inv.name),
                    })
            if inv.type == 'out_refund' and inv.invoice_refund_id:
                ccf_number = ("%s (%s)" %(inv.invoice_refund_id.name, (inv.invoice_refund_id.ref if inv.invoice_refund_id.ref else "")))
                invoice_dict.update({
                    'REF': str(ccf_number),
                })
            else:
                invoice_dict.update({
                    'REF': str(inv.ref),
                })
            #if inv.name and '-' in inv.name:
            #    number = inv.name.split('-')
            #    #text += 'NDO: ' + str(number[2]) + '\n'
            #    invoice_dict.update({
            #        'NDO': str(number[2]),
            #    })
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
                    'IDC': str(inv.partner_id.ref),
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
                #if inv.partner_id.nrc:
                #text += 'REG: ' + str(inv.partner_id.nrc) + '\n'
                #text += 'GIRO: ' + str(inv.partner_id.nrc) + '\n'
                invoice_dict.update({
                    'REG': inv.partner_id.nrc or "",
                    'GIRO': inv.partner_id.giro or "",
                })
                if inv.partner_id.vat:
                    #text += 'N.I.T: ' + str(inv.partner_id.vat) + '\n'
                    invoice_dict.update({
                        'NIT': str(inv.partner_id.vat),
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
            notes = ""
            if inv.narration:
                #text += 'NOT: ' + str(inv.narration) + '\n'
                notes = inv.narration
            invoice_dict.update({
                'NOT': str(notes),
            })
            invoice_dict.update({
                'PRINTER': str(inv.branch_id.printer_name), 
                'EMPRE': str(inv.company_id.name),
                #'SUCUR': str(inv.branch_id.name),
            })
            if inv.branch_id.name == 'Mariona':
                invoice_dict.update({
                    'SUCUR': 'San Salvador',
                })
            else:
                invoice_dict.update({
                    'SUCUR': str(inv.branch_id.name),
                })
            #text += 'FINHEADER' + '\n'
            detalle_dict = {}
            detalle_list = []
            item = 0
            wh_code = ""
            for line in inv.invoice_line_ids:
                item += 1
                wh_code = ""
                #text += '\t' + str(line.product_id.default_code) + '\t' + str(line.quantity) + '\t' + str(line.name)  + '\t' + str(line.price_unit)  + '\t' + str(inv.branch_id.name) + '\t' + str(line.price_total) + '\n'
                if line.sale_line_ids:
                    wh_code = line.sale_line_ids[0].order_id.warehouse_id.code
                if inv.journal_id.ricoh_type in ('FCF', 'FEX'):
                    detalle_dict = {
                        'ITEM': str(item),
                        'CODIGO': str(line.product_id.default_code),
                        'DESCRIPCION': str(line.product_id.name),
                        'TIENDA': str(wh_code),
                        'CANT': "{0:,.2f}".format(line.quantity),
                        'PUNI': "{0:,.2f}".format(line.price_unit),
                        'SUBTOTAL': "{0:,.2f}".format(round((line.price_total * multiplier), 2)),
                    }
                    detalle_list.append(detalle_dict)
                if inv.journal_id.ricoh_type in ('NDC', 'CCF', 'CCFNS'):
                    price_unit_dict = line.tax_ids.compute_all(line.price_unit, inv.currency_id, 1.00, line.product_id, inv.partner_id)
                    detalle_dict = {
                        'ITEM': str(item),
                        'CODIGO': str(line.product_id.default_code),
                        'DESCRIPCION': str(line.product_id.name),
                        'TIENDA': str(wh_code),
                        'CANT': "{0:,.2f}".format(line.quantity),
                        'PUNI': "{0:,.2f}".format(price_unit_dict.get('total_excluded', 0.00)),
                        'NS': "{0:,.2f}".format(line.price_total) if inv.journal_id.ricoh_type == 'CCFNS' else '',
                        'SUBTOTAL': "{0:,.2f}".format(round((line.price_subtotal * multiplier), 2)),
                    }
                    detalle_list.append(detalle_dict)
            base = iva = subtotal = perc = total = 0.00
            son = ""
            if inv.journal_id.ricoh_type in ('FCF', 'FEX'):
                base = round((inv.amount_total * multiplier), 2)
                iva = 0.00
                subtotal = round((inv.amount_total  * multiplier), 2)
                perc = 0.00
                total = round((inv.amount_total * multiplier), 2)
                son = numero_a_texto.Numero_a_Texto(inv.amount_total)
            else:
                base = round((inv.amount_untaxed * multiplier), 2)
                iva = 0.00
                subtotal = round(((inv.amount_untaxed + inv.amount_tax) * multiplier), 2)
                perc = 0.00
                total = round(((inv.amount_untaxed + inv.amount_tax) * multiplier), 2)
                son = numero_a_texto.Numero_a_Texto(inv.amount_total)
            invoice_dict.update({
                'DETALLE': detalle_list,
                'SON': son,
                'SUM': "{0:,.2f}".format(base),
                'IVA': str('0.00'),
                #'SUB': str(subtotal),
                'PER': str('0.00'),
                #'TOT': str(total),
            })
            amount_iva = amount_percibido = 0.00
            _logger.info("Amount Taxes by Group")
            #Sin IVA y otros impuestos para FCF y FEX
            if inv.journal_id.ricoh_type not in ('FCF', 'FEX'):
                for tax in inv.amount_by_group:
                    _logger.info(tax)
                    if str(tax[0]).upper() == 'IVA':
                        amount_iva = float(tax[1])
                        invoice_dict.update({
                            'IVA': "{0:,.2f}".format(round((amount_iva * multiplier), 2)),
                        })
                for tax in inv.amount_by_group:
                    _logger.info(tax)
                    if str(tax[0]).upper() == 'PERCIBIDO':
                        amount_percibido = float(tax[1])
                        invoice_dict.update({
                            'PER': "{0:,.2f}".format(round((amount_percibido * multiplier), 2)),
                        })
            invoice_dict.update({
                'SUB': "{0:,.2f}".format(base + (amount_iva  * multiplier)),
                'TOT': "{0:,.2f}".format(total),
                'NS': "{0:,.2f}".format(total) if inv.journal_id.ricoh_type == 'CCFNS' else '',
            })
            #inv.write({
            #    'count_print' : (print_count + 1),
            #})
        return invoice_dict

    def generate_json_purchase(self):
        text = ""
        invoice_dict = {}
        print_count = 0
        multiplier = 1.00
        for inv in self:
            if inv.type == 'in_refund':
                multiplier = -1.
                #if inv.invoice_refund_id:
                #    invoice_dict.update({
                #        'REF': str(inv.invoice_refund_id.name),
                #    })
            #print_count = inv.count_print
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
                    'RES' : str(inv.journal_id.serie) 
                })
            if inv.force_name:
                invoice_dict.update({
                    'NDO': str(inv.force_name),
                })
            else:
                if inv.name and '/' in inv.name:
                    number = inv.name.split('/')
                    #text += 'NDO: ' + str(number[2]) + '\n'
                    invoice_dict.update({
                        'NDO': str(number[2]),
                    })
                else:
                    invoice_dict.update({
                        'NDO': str(inv.name),
                    })
            if inv.type == 'in_refund' and inv.invoice_refund_id:
                ccf_number = ("%s (%s)" %(inv.invoice_refund_id.name, (inv.invoice_refund_id.ref if inv.invoice_refund_id.ref else "")))
                invoice_dict.update({
                    'REF': str(ccf_number),
                })
            else:
                invoice_dict.update({
                    'REF': str(inv.ref),
                })
            #if inv.name:
            #    number = inv.name.split(' ')
            #    #text += 'NDO: ' + str(number[2]) + '\n'
            #    invoice_dict.update({
            #        'NDO': str(number[1]),
            #    })
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
                    'IDC': str(inv.partner_id.ref),
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
                #if inv.partner_id.nrc:
                #text += 'REG: ' + str(inv.partner_id.nrc) + '\n'
                #text += 'GIRO: ' + str(inv.partner_id.nrc) + '\n'
                invoice_dict.update({
                    'REG': inv.partner_id.nrc or "",
                    'GIRO': inv.partner_id.giro or "",
                })
                if inv.partner_id.vat:
                    #text += 'N.I.T: ' + str(inv.partner_id.vat) + '\n'
                    invoice_dict.update({
                        'NIT': str(inv.partner_id.vat),
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
            notes = ""
            if inv.narration:
                #text += 'NOT: ' + str(inv.narration) + '\n'
                notes = inv.narration
            invoice_dict.update({
                'NOT': str(notes),
            })
            invoice_dict.update({
                'PRINTER': str(inv.branch_id.printer_name), 
                'EMPRE': str(inv.company_id.name),
                #'SUCUR': str(inv.branch_id.name),
            })
            if inv.branch_id.name == 'Mariona':
                invoice_dict.update({
                    'SUCUR': 'San Salvador',
                })
            else:
                invoice_dict.update({
                    'SUCUR': str(inv.branch_id.name),
                })
            #text += 'FINHEADER' + '\n'
            detalle_dict = {}
            detalle_list = []
            item = 0
            #wh_code = ""
            #for line in inv.invoice_line_ids:
            #    item += 1
            #    wh_code = ""
            #    #text += '\t' + str(line.product_id.default_code) + '\t' + str(line.quantity) + '\t' + str(line.name)  + '\t' + str(line.price_unit)  + '\t' + str(inv.branch_id.name) + '\t' + str(line.price_total) + '\n'
            #    if line.sale_line_ids:
            #        wh_code = line.sale_line_ids[0].order_id.warehouse_id.code
            if inv.journal_id.ricoh_type in ('CDR'):
                detalle_dict = {
                    'ITEM': str(1),
                    'CODIGO': "",
                    'DESCRIPCION': "Retencion 1%",
                    'TIENDA': "",
                    'CANT': "",
                    'PUNI': "{0:,.2f}".format(round((inv.amount_untaxed * multiplier), 2)),
                    'SUBTOTAL': "{0:,.2f}".format(round((inv.amount_untaxed * multiplier), 2)),
                }
                detalle_list.append(detalle_dict)
                #if inv.journal_id.ricoh_type in ('NDC', 'CCF'):
                #    price_unit_dict = line.tax_ids.compute_all(line.price_unit, inv.currency_id, 1.00, line.product_id, inv.partner_id)
                #    detalle_dict = {
                #        'ITEM': str(item),
                #        'CODIGO': str(line.product_id.default_code),
                #        'DESCRIPCION': str(line.product_id.name),
                #        'TIENDA': str(wh_code),
                #        'CANT': "{0:,.2f}".format(line.quantity),
                #        'PUNI': "{0:,.2f}".format(price_unit_dict.get('total_excluded', 0.00)),
                #        'SUBTOTAL': "{0:,.2f}".format(round((line.price_subtotal * multiplier), 2)),
                #    }
                #    detalle_list.append(detalle_dict)
            base = iva = subtotal = perc = total = 0.00
            son = ""
            #if inv.journal_id.ricoh_type in ('FCF', 'FEX'):
            #    base = round((inv.amount_total * multiplier), 2)
            #    iva = 0.00
            #    subtotal = round((inv.amount_total  * multiplier), 2)
            #    perc = 0.00
            #    total = round((inv.amount_total * multiplier), 2)
            #    son = numero_a_texto.Numero_a_Texto(inv.amount_total)
            if inv.journal_id.ricoh_type in ('CDR'):
                base = round((inv.amount_untaxed * multiplier), 2)
                iva = 0.00
                subtotal = round(((inv.amount_untaxed + inv.amount_tax) * multiplier), 2)
                perc = 0.00
                total = round(((inv.amount_untaxed + inv.amount_tax) * multiplier), 2)
                son = numero_a_texto.Numero_a_Texto(inv.amount_total)
            invoice_dict.update({
                'DETALLE': detalle_list,
                'SON': son,
                'SUM': "{0:,.2f}".format(base),
                'IVA': str('0.00'),
                'RET': str('0.00'),
            })
            amount_iva = amount_retenido = 0.00
            _logger.info("Amount Taxes by Group")
            #Sin IVA y otros impuestos para FCF y FEX
            if inv.journal_id.ricoh_type in ('CDR'):
                for tax in inv.amount_by_group:
                    _logger.info(tax)
                    if str(tax[0]).upper() == 'IVA':
                        amount_iva = float(tax[1])
                        invoice_dict.update({
                            'IVA': "{0:,.2f}".format(round((amount_iva * multiplier), 2)),
                        })
                for tax in inv.amount_by_group:
                    _logger.info(tax)
                    if 'IVA RETENIDO' in str(tax[0]).upper():
                        amount_retenido = float(tax[1])
                        invoice_dict.update({
                            'RET': "{0:,.2f}".format(round((amount_retenido * multiplier), 2)),
                        })
                        break

                    elif 'RETENCION ISR'in str(tax[0]).upper():
                        amount_retenido = float(tax[1])
                        invoice_dict.update({
                            'RET': "{0:,.2f}".format(round((amount_retenido * multiplier), 2)),
                        })
                        break
                        
            invoice_dict.update({
                'SUB': "{0:,.2f}".format(base + (amount_iva  * multiplier)),
                'TOT': "{0:,.2f}".format(total),
            })
            #inv.write({
            #    'count_print' : (print_count + 1),
            #})
        return invoice_dict

    def generate_json_fse(self):
        text = ""
        invoice_dict = {}
        print_count = 0
        multiplier = 1.00
        for inv in self:
            if inv.type == 'in_refund':
                multiplier = -1.
                #if inv.invoice_refund_id:
                #    invoice_dict.update({
                #        'REF': str(inv.invoice_refund_id.name),
                #    })
            #print_count = inv.count_print
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
                    'RES' : str(inv.journal_id.serie) 
                })
            #if inv.name and '/' in inv.name:
            #    number = inv.name.split('/')
            #    #text += 'NDO: ' + str(number[2]) + '\n'
            #    invoice_dict.update({
            #        'NDO': str(number[2]),
            #    })
            #else:
            invoice_dict.update({
                'NDO': str(inv.name),
            })
            if inv.type == 'in_refund' and inv.invoice_refund_id:
                ccf_number = ("%s (%s)" %(inv.invoice_refund_id.name, (inv.invoice_refund_id.ref if inv.invoice_refund_id.ref else "")))
                invoice_dict.update({
                    'REF': str(ccf_number),
                })
            else:
                invoice_dict.update({
                    'REF': str(inv.ref),
                })
            #if inv.name:
            #    number = inv.name.split(' ')
            #    #text += 'NDO: ' + str(number[2]) + '\n'
            #    invoice_dict.update({
            #        'NDO': str(number[1]),
            #    })
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
                    'IDC': str(inv.partner_id.ref),
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
                #if inv.partner_id.nrc:
                #text += 'REG: ' + str(inv.partner_id.nrc) + '\n'
                #text += 'GIRO: ' + str(inv.partner_id.nrc) + '\n'
                invoice_dict.update({
                    'REG': inv.partner_id.nrc or "",
                    'GIRO': inv.partner_id.giro or "",
                })
                if inv.partner_id.vat:
                    #text += 'N.I.T: ' + str(inv.partner_id.vat) + '\n'
                    invoice_dict.update({
                        'NIT': str(inv.partner_id.vat),
                    })
            #if inv.invoice_payment_term_id:
            #    #text += 'TER: ' + str(_(inv.invoice_payment_term_id.name)) + '\n'
            #    invoice_dict.update({
            #        'TER': str(_(inv.invoice_payment_term_id.name)),
            #    })
            if inv.partner_id and inv.partner_id.phone:
                #text += 'TEL: ' + str(inv.partner_id.phone) + '\n'
                invoice_dict.update({
                    'TEL': str(inv.partner_id.phone),
                })
            notes = ""
            if inv.narration:
                #text += 'NOT: ' + str(inv.narration) + '\n'
                notes = inv.narration
            invoice_dict.update({
                'NOT': str(notes),
            })
            invoice_dict.update({
                'PRINTER': str(inv.branch_id.printer_name), 
                'EMPRE': str(inv.company_id.name),
                'TER': '',
                #'SUCUR': str(inv.branch_id.name),
            })
            if inv.branch_id.name == 'Mariona':
                invoice_dict.update({
                    'SUCUR': 'San Salvador',
                })
            else:
                invoice_dict.update({
                    'SUCUR': str(inv.branch_id.name),
                })
            #text += 'FINHEADER' + '\n'
            detalle_dict = {}
            detalle_list = []
            item = 0
            for line in inv.invoice_line_ids:
                item += 1
                wh_code = ""
                #text += '\t' + str(line.product_id.default_code) + '\t' + str(line.quantity) + '\t' + str(line.name)  + '\t' + str(line.price_unit)  + '\t' + str(inv.branch_id.name) + '\t' + str(line.price_total) + '\n'
                #if line.sale_line_ids:
                #    wh_code = line.sale_line_ids[0].order_id.warehouse_id.code
                #if inv.journal_id.ricoh_type in ('FCF', 'FEX'):
                detalle_dict = {
                    'ITEM': str(item),
                    'CODIGO': "",
                    'DESCRIPCION': str(line.product_id.name),
                    'TIENDA': "",
                    'CANT': "{0:,.2f}".format(line.quantity),
                    'PUNI': "{0:,.2f}".format(line.price_unit),
                    'SUBTOTAL': "{0:,.2f}".format(round((line.price_total * multiplier), 2)),
                }
                detalle_list.append(detalle_dict)
            base = iva = subtotal = perc = total = 0.00
            #wh_code = ""
            #for line in inv.invoice_line_ids:
            #    item += 1
            #    wh_code = ""
            #    #text += '\t' + str(line.product_id.default_code) + '\t' + str(line.quantity) + '\t' + str(line.name)  + '\t' + str(line.price_unit)  + '\t' + str(inv.branch_id.name) + '\t' + str(line.price_total) + '\n'
            #    if line.sale_line_ids:
            #        wh_code = line.sale_line_ids[0].order_id.warehouse_id.code
            #if inv.journal_id.ricoh_type in ('FSE'):
            #    detalle_dict = {
            #        'ITEM': str(1),
            #        #'CODIGO': "",
            #        'DESCRIPCION': "Retencion 1%",
            #        #'TIENDA': "",
            #        'CANT': "",
            #        'PUNI': "{0:,.2f}".format(round((inv.amount_untaxed * multiplier), 2)),
            #        'SUBTOTAL': "{0:,.2f}".format(round((inv.amount_untaxed * multiplier), 2)),
            #    }
            #    detalle_list.append(detalle_dict)
            #    #if inv.journal_id.ricoh_type in ('NDC', 'CCF'):
            #    #    price_unit_dict = line.tax_ids.compute_all(line.price_unit, inv.currency_id, 1.00, line.product_id, inv.partner_id)
            #    #    detalle_dict = {
            #    #        'ITEM': str(item),
            #    #        'CODIGO': str(line.product_id.default_code),
            #    #        'DESCRIPCION': str(line.product_id.name),
            #    #        'TIENDA': str(wh_code),
            #    #        'CANT': "{0:,.2f}".format(line.quantity),
            #    #        'PUNI': "{0:,.2f}".format(price_unit_dict.get('total_excluded', 0.00)),
            #    #        'SUBTOTAL': "{0:,.2f}".format(round((line.price_subtotal * multiplier), 2)),
            #    #    }
            #    #    detalle_list.append(detalle_dict)
            base = iva = subtotal = perc = total = 0.00
            son = ""
            #if inv.journal_id.ricoh_type in ('FCF', 'FEX'):
            #    base = round((inv.amount_total * multiplier), 2)
            #    iva = 0.00
            #    subtotal = round((inv.amount_total  * multiplier), 2)
            #    perc = 0.00
            #    total = round((inv.amount_total * multiplier), 2)
            #    son = numero_a_texto.Numero_a_Texto(inv.amount_total)
            if inv.journal_id.ricoh_type in ('FSE'):
                base = round((inv.amount_untaxed * multiplier), 2)
                iva = 0.00
                subtotal = round(((inv.amount_untaxed + inv.amount_tax) * multiplier), 2)
                perc = 0.00
                total = round(((inv.amount_untaxed + inv.amount_tax) * multiplier), 2)
                son = numero_a_texto.Numero_a_Texto(inv.amount_total)
            invoice_dict.update({
                'DETALLE': detalle_list,
                'SON': son,
                'SUM': "{0:,.2f}".format(base),
                'IVA': str('0.00'),
                'RET': str('0.00'),
            })
            amount_iva = amount_retenido = 0.00
            _logger.info("Amount Taxes by Group")
            #Sin IVA y otros impuestos para FCF y FEX
            if inv.journal_id.ricoh_type in ('FSE'):
                for tax in inv.amount_by_group:
                    _logger.info(tax)
                    if 'IVA' in str(tax[0]).upper():
                        amount_iva = float(tax[1])
                        invoice_dict.update({
                            'IVA': "{0:,.2f}".format(round((amount_iva * multiplier), 2)),
                        })
                for tax in inv.amount_by_group:
                    _logger.info(tax)
                    if 'RETEN' in str(tax[0]).upper():
                        amount_retenido = float(tax[1])
                        invoice_dict.update({
                            'RET': "{0:,.2f}".format(round((amount_retenido * multiplier), 2)),
                        })
            invoice_dict.update({
                'SUB': "{0:,.2f}".format(base + (amount_iva  * multiplier)),
                'TOT': "{0:,.2f}".format(total),
            })
            #inv.write({
            #    'count_print' : (print_count + 1),
            #})
        return invoice_dict

    def generate_json_exento(self):
        text = ""
        invoice_dict = {}
        print_count = 0
        multiplier = 1.00
        for inv in self:
            if inv.type == 'out_refund':
                multiplier = -1.
                #if inv.invoice_refund_id:
                #    invoice_dict.update({
                #        'REF': str(inv.invoice_refund_id.name),
                #    })
            #print_count = inv.count_print
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
                    'RES' : str(inv.journal_id.serie) 
                })
            if inv.force_name:
                invoice_dict.update({
                    'NDO': str(inv.force_name),
                })
            else:
                if inv.name and '/' in inv.name:
                    number = inv.name.split('/')
                    #text += 'NDO: ' + str(number[2]) + '\n'
                    invoice_dict.update({
                        'NDO': str(number[2]),
                    })
                elif inv.name and '-' in inv.name:
                    number = inv.name.split('-')
                    invoice_dict.update({
                        'NDO': str(number[2]),
                        })
                else:
                    invoice_dict.update({
                        'NDO': str(inv.name),
                    })
            if inv.type == 'out_refund' and inv.invoice_refund_id:
                ccf_number = ("%s (%s)" %(inv.invoice_refund_id.name, (inv.invoice_refund_id.ref if inv.invoice_refund_id.ref else "")))
                invoice_dict.update({
                    'REF': str(ccf_number),
                })
            else:
                invoice_dict.update({
                    'REF': str(inv.ref),
                })
            #if inv.name and '-' in inv.name:
            #    number = inv.name.split('-')
            #    #text += 'NDO: ' + str(number[2]) + '\n'
            #    invoice_dict.update({
            #        'NDO': str(number[2]),
            #    })
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
                    'IDC': str(inv.partner_id.ref),
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
                #if inv.partner_id.nrc:
                #text += 'REG: ' + str(inv.partner_id.nrc) + '\n'
                #text += 'GIRO: ' + str(inv.partner_id.nrc) + '\n'
                invoice_dict.update({
                    'REG': inv.partner_id.nrc or "",
                    'GIRO': inv.partner_id.giro or "",
                })
                if inv.partner_id.vat:
                    #text += 'N.I.T: ' + str(inv.partner_id.vat) + '\n'
                    invoice_dict.update({
                        'NIT': str(inv.partner_id.vat),
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
            notes = ""
            if inv.narration:
                #text += 'NOT: ' + str(inv.narration) + '\n'
                notes = inv.narration
            invoice_dict.update({
                'NOT': str(notes),
            })
            invoice_dict.update({
                'PRINTER': str(inv.branch_id.printer_name), 
                'EMPRE': str(inv.company_id.name),
                #'SUCUR': str(inv.branch_id.name),
            })
            if inv.branch_id.name == 'Mariona':
                invoice_dict.update({
                    'SUCUR': 'San Salvador',
                })
            else:
                invoice_dict.update({
                    'SUCUR': str(inv.branch_id.name),
                })
            #text += 'FINHEADER' + '\n'
            detalle_dict = {}
            detalle_list = []
            item = 0
            wh_code = ""
            for line in inv.invoice_line_ids:
                item += 1
                wh_code = ""
                #text += '\t' + str(line.product_id.default_code) + '\t' + str(line.quantity) + '\t' + str(line.name)  + '\t' + str(line.price_unit)  + '\t' + str(inv.branch_id.name) + '\t' + str(line.price_total) + '\n'
                if line.sale_line_ids:
                    wh_code = line.sale_line_ids[0].order_id.warehouse_id.code
                if inv.journal_id.ricoh_type in ('FCF', 'FEX', 'FCFE'):
                    detalle_dict = {
                        'ITEM': str(item),
                        'CODIGO': str(line.product_id.default_code),
                        'DESCRIPCION': str(line.product_id.name),
                        'TIENDA': str(wh_code),
                        'CANT': "{0:,.2f}".format(line.quantity),
                        'PUNI': "{0:,.2f}".format(line.price_unit),
                        'EX': "{0:,.2f}".format(round((line.price_total * multiplier), 2)),
                    }
                    detalle_list.append(detalle_dict)
                if inv.journal_id.ricoh_type in ('NDC', 'CCF', 'CCFNS'):
                    price_unit_dict = line.tax_ids.compute_all(line.price_unit, inv.currency_id, 1.00, line.product_id, inv.partner_id)
                    detalle_dict = {
                        'ITEM': str(item),
                        'CODIGO': str(line.product_id.default_code),
                        'DESCRIPCION': str(line.product_id.name),
                        'TIENDA': str(wh_code),
                        'CANT': "{0:,.2f}".format(line.quantity),
                        'PUNI': "{0:,.2f}".format(price_unit_dict.get('total_excluded', 0.00)),
                        'NS': "{0:,.2f}".format(line.price_total) if inv.journal_id.ricoh_type == 'CCFNS' else '',
                        'EX': "{0:,.2f}".format(round((line.price_subtotal * multiplier), 2)),
                    }
                    detalle_list.append(detalle_dict)
            base = iva = subtotal = perc = total = 0.00
            son = ""
            if inv.journal_id.ricoh_type in ('FCF', 'FEX'):
                base = round((inv.amount_total * multiplier), 2)
                iva = 0.00
                subtotal = round((inv.amount_total  * multiplier), 2)
                perc = 0.00
                total = round((inv.amount_total * multiplier), 2)
                son = numero_a_texto.Numero_a_Texto(inv.amount_total)
            else:
                base = round((inv.amount_untaxed * multiplier), 2)
                iva = 0.00
                subtotal = round(((inv.amount_untaxed + inv.amount_tax) * multiplier), 2)
                perc = 0.00
                total = round(((inv.amount_untaxed + inv.amount_tax) * multiplier), 2)
                son = numero_a_texto.Numero_a_Texto(inv.amount_total)
            invoice_dict.update({
                'DETALLE': detalle_list,
                'SON': son,
                'SUM': "{0:,.2f}".format(total),
                'IVA': str('0.00'),
                #'SUB': str(subtotal),
                'PER': str('0.00'),
                'TOT': "{0:,.2f}".format(total),
            })
            amount_iva = amount_percibido = 0.00
            _logger.info("Amount Taxes by Group")
            #Sin IVA y otros impuestos para FCF y FEX o si el diario es un documento exento
            #if inv.journal_id.ricoh_type not in ('FCF', 'FEX') or inv.journal_id.is_exento == True:
            #    for tax in inv.amount_by_group:
            #        _logger.info(tax)
            #        if str(tax[0]).upper() == 'IVA':
            #            amount_iva = float(tax[1])
            #            invoice_dict.update({
            #                'IVA': "{0:,.2f}".format(round((amount_iva * multiplier), 2)),
            #            })
            #    for tax in inv.amount_by_group:
            #        _logger.info(tax)
            #        if str(tax[0]).upper() == 'PERCIBIDO':
            #            amount_percibido = float(tax[1])
            #            invoice_dict.update({
            #                'PER': "{0:,.2f}".format(round((amount_percibido * multiplier), 2)),
            #           })
            invoice_dict.update({
                #'SUB': "{0:,.2f}".format(base + (amount_iva  * multiplier)),
                'EX': "{0:,.2f}".format(total),
                'NS': "{0:,.2f}".format(total) if inv.journal_id.ricoh_type == 'CCFNS' else '',
            })
            #inv.write({
            #    'count_print' : (print_count + 1),
            #})
        return invoice_dict


AccountMove()


class ResBranch(models.Model):
    _inherit = 'res.branch'

    printer_name = fields.Char('Impresora', required=False)
ResBranch()