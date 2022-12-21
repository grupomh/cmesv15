# -*- coding: utf-8 -*-

import random

import datetime
import uuid

from odoo import fields, models, api
from odoo.exceptions import UserError, Warning
from odoo.addons.account_invoice_megaprint import numero_a_texto
import base64
from odoo.tools.translate import _
import requests
import json
from ast import literal_eval

#XML libraries
from xml.etree.ElementTree import Element, SubElement, Comment, tostring, fromstring
from xml.dom import minidom
from odoo.addons.account_invoice_megaprint import cdata

import logging


_logger = logging.getLogger( __name__ )

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    uuid_fel = fields.Char(string='No. Factura', readonly=True, default=0, copy=False,
                           states={'draft': [('readonly', False)]}, help='UUID returned by certifier')  # No. Invoice
    fel_serie = fields.Char(string='Serie', readonly=True, states={'draft': [('readonly', False)]}, copy=False,
                            help='Raw Serial number return by GFACE or FEL provider')  # Fel Series
    fel_no = fields.Char(string='Numero.', readonly=True, states={'draft': [('readonly', False)]}, copy=False,
                         help='Raw Serial number return by GFACE or FEL provider')
    fel_date = fields.Char(string='Fecha DTE.', readonly=True, states={'draft': [('readonly', False)]}, copy=False,
                         help='Raw date return by GFACE or FEL provider')
    fel_received_sat = fields.Char(string='Acuse Recibo SAT', readonly=True, states={'draft': [('readonly', False)]}, copy=False)
    uuid = fields.Char(string='UUID', readonly=True, states={'draft': [('readonly', False)]}, copy=False,
                       help='UUID given to the certifier to register the document')
    no_acceso = fields.Char(string='Numero de Acceso', readonly=True, states={'draft': [('readonly', False)]},
                            copy=False, help='Electronic singnature given sent to FEL')  # Access Number
    frase_ids = fields.Many2many('satdte.frases', 'inv_frases_rel', 'inv_id', 'frases_id', 'Frases')
    nce_frase_ids = fields.Many2many('satdte.frases', 'nce_frases_rel', 'inv_id', 'nce_frases_id', 'NCE Frases')

    factura_cambiaria = fields.Boolean('Factura Cambiaria', related='journal_id.factura_cambiaria', readonly=True)
    number_of_payments = fields.Integer('Cantidad De Abonos', default=1, copy=False, help='Number Of Payments')
    frecuencia_de_vencimiento = fields.Integer('Frecuencia De Vencimiento', copy=False, help='Due date frequency (calendar days)')
    megaprint_payment_lines = fields.One2many('megaprint.payment.line', 'invoice_id', 'Payment Info', copy=False)
    xml_request = fields.Text(string='XML Request', readonly=True, states={'draft': [('readonly', False)]}, copy=False)
    xml_response = fields.Text(string='XML Response', readonly=True, states={'draft': [('readonly', False)]}, copy=False)
    xml_response_cancel = fields.Text(string='XML Response', readonly=True, states={'draft': [('readonly', False)]}, copy=False)
    xml_notes = fields.Text('XML Children')
    uuid_refund = fields.Char('UUID a rectificar', related="invoice_refund_id.uuid")
    txt_filename = fields.Char('Archivo', required=False, readonly=True, copy=False)
    file = fields.Binary('Archivo', required=False, readonly=True, copy=False)
    txt_filename_xml = fields.Char('Archivo XML', required=False, readonly=True, copy=False)
    file_xml = fields.Binary('Archivo XML', required=False, readonly=True, copy=False)
    invoice_refund_id = fields.Many2one('account.move', 'Invoice Refund', required=False, readonly=False)
    is_fel = fields.Boolean('FEL', related="journal_id.is_fel")
    be_cancel = fields.Boolean('DTE Anulado', default=False)
    partner_vat = fields.Char('Nit', related="partner_id.vat", readonly=False)
    #serie_fel = fields.Char('Serie FEL')
    #number_fel = fields.Char('Numero FEL')

    #Only for export
    exportacion_fel = fields.Boolean('Exportacion FEL')
    peso_total = fields.Char('Peso total')
    oc_number = fields.Char(compute='_oc_number')

    @api.depends('invoice_origin')
    def _oc_number(self):
        number = ""
        for data in self:
            if data.move_type == 'out_invoice' and data.invoice_origin:
                sale_orders = self.env['sale.order'].search([('name', '=', data.invoice_origin)], limit=1)
                for so in sale_orders:
                    number += so.client_order_ref if so.client_order_ref else ""
            data.update({
                'oc_number': number or "",
            })

    @api.onchange('company_id')
    def onchange_frases(self):
        if self.company_id:
            if self.company_id.frase_ids:
                self.frase_ids = self.company_id.frase_ids.ids
            if self.company_id.nce_frase_ids:
                self.nce_frase_ids = self.company_id.nce_frase_ids

    def days_between(self, d1, d2):
        result = False
        d1 = datetime.datetime.strptime(str(d1), "%Y-%m-%d")
        d2 = datetime.datetime.strptime(str(d2), "%Y-%m-%d")
        if d1 and d2:
            result = abs((d2 - d1).days)
        return result

    def calculate_payment_info(self):
        for inv in self:
            #is_fcam = inv.journal_id.factura_cambiaria
            number_of_payments = inv.number_of_payments or 1
            invoice_date = inv.invoice_date or fields.Date.today()
            days = self.days_between(invoice_date, inv.invoice_date_due)
            frecuency_due = inv.frecuencia_de_vencimiento or days
            if inv.journal_id.factura_cambiaria and number_of_payments and frecuency_due and invoice_date:
                inv.megaprint_payment_lines.unlink()  # Delete Old Payment Lines
                amount = inv.amount_total / number_of_payments
                new_date = None
                for i in range(number_of_payments):
                    if not new_date:
                        new_date = datetime.datetime.strptime(str(invoice_date), '%Y-%m-%d').date() + datetime.timedelta(days=frecuency_due)
                    else:
                        new_date = new_date + datetime.timedelta(days=frecuency_due)
                    self.env['megaprint.payment.line'].create({
                        'invoice_id': inv.id,
                        'serial_no': i + 1,
                        'amount': amount,
                        'due_date': new_date.strftime('%Y-%m-%d')
                    })
    
    def action_post(self):
        xml = ""
        res = super(AccountInvoice, self).action_post()
        if self.move_type in ('out_invoice', 'out_refund') and self.journal_id.is_fel == True:
            if self.exportacion_fel:
                xml = self.generate_xml_export()
                _logger.info("**********FACTURA DE EXPORTACION**********")
                _logger.info(xml.decode('utf-8'))
                #raise UserError(('%s') %(xml))
            elif self.journal_id.is_nota_abono:
                nabn_dict = self.generate_xml_nabn()
                xml = self.GenerateXML_NABN(data=nabn_dict)
                #raise UserError(('%s') %(xml))
                _logger.info("**********NOTA DE ABONO**********")
                _logger.info(xml.decode('utf-8'))

            else:
                xml = self.generate_xml()
                _logger.info("**********FACTURA**********")
                _logger.info(xml.decode('utf-8'))
            #raise UserError(('%s') %(xml))
            xml_request = self.dte_request(xml_string=xml.decode('utf-8'), type_request='FirmaDocumentoRequest')
            #_logger.info(xml_request.decode('utf-8'))
            xml_sing = self.get_signature(xml_request.decode('utf-8'))
            #_logger.info(xml_sing.decode('utf-8'))
            xml_signed = self.dte_request(xml_string=xml_sing, type_request='RegistraDocumentoXMLRequest')
            #_logger.info(xml_signed.decode('utf-8'))
            self.register_dte(xml_signed.decode('utf-8'))
        elif (self.move_type == 'in_invoice' and self.journal_id.is_fel == True):
            if self.journal_id.is_factura_especial:
                fe_dict = self.generate_xml_fe()
                _logger.info(fe_dict)
                xml = self.GenerateXML_FESP(data=fe_dict)
                # raise UserError(('%s') %(xml.decode('utf-8')))
                xml_request = self.dte_request(xml_string=xml.decode('utf-8'), type_request='FirmaDocumentoRequest')
                xml_sing = self.get_signature(xml_request.decode('utf-8'))
                xml_signed = self.dte_request(xml_string=xml_sing, type_request='RegistraDocumentoXMLRequest')
                self.register_dte(xml_signed.decode('utf-8'))
        return res

    def get_delivery_address(self, partner_id=False):
        partner_obj = self.env['res.partner']
        address = ""
        sep = ","
        delivery = False
        if partner_id:
            delivery = partner_obj.search([('id', '=', partner_id)], limit=1)
            if delivery.street:
                address += delivery.street + sep
            if delivery.street2:
                address += delivery.street2 + sep
            if delivery.city:
                address += delivery.city + sep
            if delivery.state_id:
                address += delivery.state_id.name + sep
            if delivery.country_id:
                address += delivery.country_id.name
        return delivery and delivery.name, address or False

    def generate_xml_fe(self):
        megaprint_dateformat = "%Y-%m-%dT%H:%M:%S"
        item_no = 0
        dte = {}
        adenda = []
        complement_data = []
        complement = {}
        details = []
        details_taxes = []
        details_total_taxes = []
        frases_lines = []
        total_taxes = 0.00
        total_with_taxes = 0.00
        for inv in self:
            access_number = str(random.randint(100000000, 999999999))
            while True:
                access_count = self.env['account.move'].search_count([('no_acceso', '=', access_number)])
                if access_count > 0:
                    access_number = str(random.randint(100000000, 999999999))
                else:
                    break
            dte['access_number'] = access_number
            date_dte = fields.Datetime.context_timestamp(self.with_context(tz=self.env.user.tz),
                                                         datetime.datetime.now())
            dte['date_dte'] = date_dte.strftime(megaprint_dateformat)
            inv.fel_date = date_dte.strftime(megaprint_dateformat)
            dte['tipo'] = 'FESP'
            if self.frase_ids:
                for frase in self.frase_ids:
                    frases_lines.append([frase.codigo_escenario, frase.tipo_frase])
            else:
                frases_lines = [[1, 1]]
            # Datos emisor
            dte['frases'] = frases_lines
            dte['moneda'] = inv.currency_id.name or 'GTQ'
            dte['establecimiento'] = inv.journal_id.codigo_est
            dte['regimeniva'] = inv.company_id.regimen_iva
            dte['correoemisor'] = inv.company_id.email
            dte['nitemisor'] = inv.company_id.vat
            dte['nombrecomercial'] = inv.company_id.nombre_comercial
            dte['nombreemisor'] = inv.company_id.name
            dte['calleemisor'] = inv.company_id.street if inv.company_id.street else ''
            dte['municipioemisor'] = inv.company_id.city or ''
            dte['departamentoemisor'] = inv.company_id.state_id.name or ''
            dte['postalemisor'] = inv.company_id.zip or ''
            dte['paisemisor'] = inv.company_id.country_id.code or ''
            # Datos Receptor
            dte['correoreceptor'] = inv.partner_id.email or ''
            dte['nitreceptor'] = inv.partner_id.vat or 'CF'
            dte['TipoDocu'] = inv.partner_id.type_document
            dte['nombrereceptor'] = inv.partner_id.name
            dte['callereceptor'] = inv.partner_id.street if inv.partner_id.street else ''
            dte['municipiorecptor'] = inv.partner_id.city or ''
            dte['departamentoreceptor'] = inv.partner_id.state_id.name
            dte['postalreceptor'] = inv.partner_id.zip or ''
            dte['paisreceptor'] = inv.partner_id.country_id.code
            for line in inv.invoice_line_ids:
                # Variables x item
                item = {}
                tax_line = {}
                details_taxes = []
                details_total_taxes = []
                subtotal_taxes = 0.00
                item_no += 1
                price_unit = round(line.price_unit, 2)
                discount_unit = (line.price_unit * (line.discount / 100))
                taxes_unit = line.product_id.supplier_taxes_id.compute_all((price_unit - discount_unit),
                                                                           inv.currency_id, 1.00, line.product_id,
                                                                           inv.partner_id)
                # taxes = line.tax_ids.compute_all((price_unit - discount_unit), inv.currency_id, line.quantity, line.product_id, inv.partner_id)
                price_unit_included = round(taxes_unit.get('total_included', 0.00), 2)
                # Taxes calculted
                item['grabable'] = str(round((line.quantity * price_unit_included), 2))
                total_with_taxes += round((line.quantity * price_unit_included), 2)
                item['subtotal'] = str(round((line.quantity * price_unit_included), 2))
                item['descuento'] = str(0.00)
                item['cantidad'] = str(line.quantity)
                item['descripcion'] = str(line.name)
                item['preciounitario'] = str(round(taxes_unit.get('total_included', 0.00), 2))
                item['uom'] = 'UNI'
                item['line'] = str(item_no)
                item['exento'] = '2' if not line.tax_ids else '1'
                item['tipoitem'] = 'S' if line.product_id.type == 'service' else 'B'
                for tax in taxes_unit.get('taxes', False):
                    base_amount = round(tax.get('base', 0.00), 2)
                    tax_amount = round(tax.get('amount', 0.00), 2)
                    tax_name = ""
                    subtotal_taxes += round((line.quantity * tax_amount), 2)
                    total_taxes += subtotal_taxes
                    if tax.get('name', '')[0:3] == "IVA":
                        tax_name = 'IVA'
                    else:
                        tax_name = tax.get('name', '')
                    tax_line = {
                        'tax': str(round((line.quantity * tax_amount), 2)),
                        'base': str(round((line.quantity * base_amount), 2)),
                        'tax_name': tax_name,
                        'quantity': str(line.quantity),
                    }
                    details_taxes.append(tax_line)
                    details_total_taxes.append(tax_line)
                    item['itemsimpuestos'] = details_taxes
                    item['subtotalimpuestos'] = str(round(subtotal_taxes, 3))
                    details.append(item)
                # raise UserError(('%s') %(str(inv.amount_by_group)))
                for tax in inv.amount_by_group:
                    # raise UserError(('%s') %(str(tax)))
                    if float(tax[1]) < 0.00:
                        complement = {
                            'EtiquetaFel': self.env['account.tax.group'].browse([tax[6]]).fel_code,
                            'Amount': str(abs(round(tax[1], 2))),
                        }
                        complement_data.append(complement)
                complement = {
                    'EtiquetaFel': "TotalMenosRetenciones",
                    'Amount': str(round(inv.amount_total, 2)),
                }
                complement_data.append(complement)
            dte['complementos'] = complement_data
            dte['items'] = details
            dte['totalimpuestos'] = str(round(total_taxes, 3))
            dte['total'] = str(round(total_with_taxes, 2))
        return dte

    def generate_xml_nabn(self):
        megaprint_dateformat = "%Y-%m-%dT%H:%M:%S"
        item_no = 0
        dte = {}
        adenda = []
        complement_data = []
        complement = {}
        details = []
        details_taxes = []
        details_total_taxes = []
        frases_lines = []
        total_taxes = 0.00
        total_with_taxes = 0.00
        for inv in self:
            access_number = str(random.randint(100000000, 999999999))
            while True:
                access_count = self.env['account.move'].search_count([('no_acceso', '=', access_number)])
                if access_count > 0:
                    access_number = str(random.randint(100000000, 999999999))
                else:
                    break
            dte['access_number'] = access_number
            date_dte = fields.Datetime.context_timestamp(self.with_context(tz=self.env.user.tz),
                                                         datetime.datetime.now())
            dte['date_dte'] = date_dte.strftime(megaprint_dateformat)
            inv.fel_date = date_dte.strftime(megaprint_dateformat)
            dte['tipo'] = 'NABN'
            if self.frase_ids:
                for frase in self.frase_ids:
                    frases_lines.append([frase.codigo_escenario, frase.tipo_frase])
            else:
                frases_lines = [[1, 1]]
            # Datos emisor
            dte['frases'] = frases_lines
            dte['moneda'] = inv.currency_id.name or 'GTQ'
            dte['establecimiento'] = inv.journal_id.codigo_est
            dte['regimeniva'] = inv.company_id.regimen_iva
            dte['correoemisor'] = inv.company_id.email
            dte['nitemisor'] = inv.company_id.vat
            dte['nombrecomercial'] = inv.company_id.nombre_comercial
            dte['nombreemisor'] = inv.company_id.name
            dte['calleemisor'] = inv.company_id.street if inv.company_id.street else ''
            dte['municipioemisor'] = inv.company_id.city or ''
            dte['departamentoemisor'] = inv.company_id.state_id.name or ''
            dte['postalemisor'] = inv.company_id.zip or ''
            dte['paisemisor'] = inv.company_id.country_id.code or ''
            # Datos Receptor
            dte['correoreceptor'] = inv.partner_id.email or ''
            dte['nitreceptor'] = inv.partner_id.vat or 'CF'
            dte['TipoDocu'] = inv.partner_id.type_document
            dte['nombrereceptor'] = inv.partner_id.name
            dte['callereceptor'] = inv.partner_id.street if inv.partner_id.street else ''
            dte['municipiorecptor'] = inv.partner_id.city or ''
            dte['departamentoreceptor'] = inv.partner_id.state_id.name
            dte['postalreceptor'] = inv.partner_id.zip or ''
            dte['paisreceptor'] = inv.partner_id.country_id.code
            for line in inv.invoice_line_ids:
                # Variables x item
                item = {}
                tax_line = {}
                details_taxes = []
                details_total_taxes = []
                subtotal_taxes = 0.00
                item_no += 1
                price_unit = round(line.price_unit, 2)
                discount_unit = (line.price_unit * (line.discount / 100))
                taxes_unit = line.product_id.supplier_taxes_id.compute_all((price_unit - discount_unit),
                                                                           inv.currency_id, 1.00, line.product_id,
                                                                           inv.partner_id)
                # taxes = line.tax_ids.compute_all((price_unit - discount_unit), inv.currency_id, line.quantity, line.product_id, inv.partner_id)
                price_unit_included = round(taxes_unit.get('total_included', 0.00), 2)
                # Taxes calculted
                item['grabable'] = str(round((line.quantity * price_unit_included), 2))
                total_with_taxes += round((line.quantity * price_unit_included), 2)
                item['subtotal'] = str(round((line.quantity * price_unit_included), 2))
                item['descuento'] = str(0.00)
                item['cantidad'] = str(line.quantity)
                item['descripcion'] = str(line.name)
                item['preciounitario'] = str(round(taxes_unit.get('total_included', 0.00), 2))
                item['uom'] = 'UNI'
                item['line'] = str(item_no)
                item['exento'] = '2' if not line.tax_ids else '1'
                item['tipoitem'] = 'S' if line.product_id.type == 'service' else 'B'
                for tax in taxes_unit.get('taxes', False):
                    base_amount = round(tax.get('base', 0.00), 2)
                    tax_amount = round(tax.get('amount', 0.00), 2)
                    tax_name = ""
                    subtotal_taxes += round((line.quantity * tax_amount), 2)
                    total_taxes += subtotal_taxes
                    if tax.get('name', '')[0:3] == "IVA":
                        tax_name = 'IVA'
                    else:
                        tax_name = tax.get('name', '')
                    tax_line = {
                        'tax': str(round((line.quantity * tax_amount), 2)),
                        'base': str(round((line.quantity * base_amount), 2)),
                        'tax_name': tax_name,
                        'quantity': str(line.quantity),
                    }
                    details_taxes.append(tax_line)
                    details_total_taxes.append(tax_line)
                    item['itemsimpuestos'] = details_taxes
                    item['subtotalimpuestos'] = str(round(subtotal_taxes, 3))
                details.append(item)
                # raise UserError(('%s') %(str(inv.amount_by_group)))
                #for tax in inv.amount_by_group:
                #    # raise UserError(('%s') %(str(tax)))
                #    if float(tax[1]) < 0.00:
                #        complement = {
                #            'EtiquetaFel': self.env['account.tax.group'].browse([tax[6]]).fel_code,
                #            'Amount': str(abs(round(tax[1], 2))),
                #        }
                #        complement_data.append(complement)
                #complement = {
                #    'EtiquetaFel': "TotalMenosRetenciones",
                #    'Amount': str(round(inv.amount_total, 2)),
                #}
                #complement_data.append(complement)
            #dte['complementos'] = complement_data
            dte['items'] = details
            dte['totalimpuestos'] = str(round(total_taxes, 3))
            dte['total'] = str(round(total_with_taxes, 2))
        return dte

    def generate_xml(self):
        res_xml = False
        megaprint_dateformat = "%Y-%m-%dT%H:%M:%S"
        no_lin = 1
        AdendaSummary = []
        Complemento_Data = {}
        _items = []
        total_impuesto = 0

        gran_total = 0

        # Generate 9 digit random number as a Access Number
        no_acceso = str(random.randint(100000000, 999999999))
        while True:
            acceso = self.env['account.move'].search_count([('no_acceso', '=', no_acceso)])
            if acceso > 0:
                no_acceso = str(random.randint(100000000, 999999999))
            else:
                break

        # Current time For the tag FechaHoraEmision
        fecha = fields.Datetime.context_timestamp(self.with_context(tz=self.env.user.tz), datetime.datetime.now())
        if fecha:
            fecha_str = str(fecha.strftime(megaprint_dateformat))
            self.fel_date = fecha_str
        delivery_name = ""
        delivery_street = ""
        partner_address = self.partner_id.address_get(['delivery', 'invoice'])
        delivery_address = self.get_delivery_address(partner_id=partner_address['delivery'])
        delivery_street = delivery_address[1]
        delivery_name = delivery_address[0]
        if self.name:
            numero = self.name.split('/')
            if numero:
                AdendaSummary.append(numero[0]) #valor1
                AdendaSummary.append(numero[2]) #valor2
        AdendaSummary.append(str(numero_a_texto.Numero_a_Texto(self.amount_total))) #valor3
        AdendaSummary.append(str(self.amount_total)) #valor4
        AdendaSummary.append(str(self.invoice_payment_term_id.name)) #valor5 Plazo de Pago en Factura
        AdendaSummary.append(str(self.invoice_origin)) #valor6 Documento Origen SO
        AdendaSummary.append(str(self.name or '')) #valor7 (CORRELATIVO INTERNO DE ODOO EN EL PDF DE LA FACTURA.)
        AdendaSummary.append(str(self.ref or '')) #valor8 (Numero de OC del cliente [Ref Cliente].) 
        #AdendaSummary.append(str(self.narration or '')) #valor9 (MOSTRAR COMENTARIOS QUE SE AGREGUEN  EN EL CAMPO "NARRATION" DEL FORM DE  LA FACTURA EN EL PDF DE IMPRESIÓN)

        #if delivery_name and delivery_address:
        #AdendaSummary.append(str(delivery_name)) #valor10
        #AdendaSummary.append(str(delivery_street)) #valor11
        #AdendaSummary.append(str(self.partner_id.code)) #valor12
        #AdendaSummary.append(str(self.company_id.phone)) #valor13
        for inv_line in self.invoice_line_ids:
            if inv_line.display_type == 'line_section':
                continue
            detail = []
            if inv_line.product_id.type == 'service':
                bien_servicio = 'S'
            else:
                bien_servicio = 'B'

            total_price = round((inv_line.price_unit * inv_line.quantity),2)
            discount = round(total_price * ((inv_line.discount or 0.0) / 100.0),2)
            # grabable = total_price - discount
            grabable = round(((total_price - discount) / 1.12),2)
            MontoImp = round((total_price - discount - grabable),2)
            total_impuesto += MontoImp
            total = grabable + MontoImp
            gran_total += total
            descripcion_not = inv_line.name
            #AdendaSummary.append(inv_line.name)

            if str(inv_line.product_uom_id.name):
                uom = "UNI"
            else:
                uom = inv_line.product_uom_id.name
                uom = uom.encode('utf-8')

            for tax in inv_line.tax_ids:
                if tax.name[0:3] == "IVA":
                    iva_grabable = str(grabable)
                    iva_qty = str(inv_line.quantity)
                    iva = str(round((total_price - grabable),2))
                    #if inv_line.price_tax:
                    #    iva = str(inv_line.price_tax)
                    # iva = '''<dte:Impuestos><dte:Impuesto><dte:NombreCorto>IVA</dte:NombreCorto><dte:CodigoUnidadGravable>1</dte:CodigoUnidadGravable><dte:MontoGravable>'''+grabable+'''</dte:MontoGravable><dte:CantidadUnidadesGravables>'''+str(inv_line.quantity)+'''</dte:CantidadUnidadesGravables><dte:MontoImpuesto>'''+str(inv_line.price_tax)+'''</dte:MontoImpuesto></dte:Impuesto></dte:Impuestos>'''

            detail.append(bien_servicio)  # Product Type
            detail.append(no_lin)  # Line number
            no_lin += 1
            detail.append(inv_line.quantity)  # Product Quantity
            detail.append(uom)  # Unit Of Measure
            detail.append(descripcion_not)  # Product description
            detail.append(inv_line.price_unit)  # Price of the product
            detail.append(round(total_price,2))  # Total Price
            detail.append(discount)  # Product Discount
            # IVA info
            detail.append(round(grabable, 2))
            detail.append(inv_line.quantity)  # Product Quantity
            detail.append(round(MontoImp, 2))
            detail.append(round(total, 2))
            _items.append(detail)

        total_impuesto = round(total_impuesto, 2)
        gran_total = round(gran_total, 2)

        codeEstab = self.journal_id.codigo_est or ''  # Company Establishment Code
        afIVA = self.company_id.regimen_iva or 'GEN'  # Company Associated VAT regime OR 'GEN'(Default)
        correoEmisor = self.company_id.email or ''  # Company Email
        nitEmisor = self.company_id.vat or ''  # Compant vat No
        nombreComercial = self.company_id.nombre_comercial or ''  # Company Tradename
        nombreRec = ""
        calleRec = ""
        departamentoRec = ""
        postalRec = ""
        paisRec = ""
        municipioRec = ""
        DatosCliente = False
        nombreEmisor = self.company_id.name or ''  # Company Name
        # Company Address Details
        if self.company_id.street:
            calleEmisor = self.company_id.street or ''
        else:
            calleEmisor = ""
        if self.company_id.street2:
            calleEmisor = calleEmisor + ' ' + self.company_id.street2 or ''
        if self.company_id.city:
            municipioEmisor = self.company_id.city or ''
        else:
            municipioEmisor = ''
        if self.company_id.state_id:
            departamentoEmisor = self.company_id.state_id.name or ''
        else:
            departamentoEmisor = ""
        if self.company_id.zip:
            postalEmisor = self.company_id.zip
        else:
            postalEmisor = "502"
        if self.company_id.country_id.code:
            paisEmisor = self.company_id.country_id.code or 'GT'
        else:
            paisEmisor = "GT"
        # Partner Details
        #if not self.partner_id.vat or self.partner_id.var != "CF":
        #DatosCliente = self.get_datos_cliente(nitEmisor, self.partner_id.vat)
        if self.partner_id.email:
            correoRec = self.partner_id.email
        else:
            correoRec = ""
        if self.partner_id.vat:
            vatRec = self.partner_id.vat
        elif self.partner_id.vat == 'EXPORT':
            vatRec = "EXPORT"
        elif self.partner_id.vat == "CF":
            vatRec = "CF"
        else:
            vatRec = "CF"
        if vatRec not in ['CF', 'EXPORT']:
            DatosCliente = self.get_datos_cliente((self.partner_vat if self.partner_vat else self.partner_id.vat))
            if DatosCliente:
                nombreRec = DatosCliente[0] if DatosCliente[0] else "Consumidor Final"
                calleRec = DatosCliente[1] if DatosCliente[1] else "Ciudad"
                postalRec = self.partner_id.zip if self.partner_id.zip else "502"
                paisRec = self.partner_id.country_id.code if self.partner_id.country_id.code else "GT"
                municipioRec = self.partner_id.city if self.partner_id.city else ""
        else:
            if self.partner_id.name:   
                nombreRec = self.partner_id.name
            if self.partner_id.street:
                calleRec = self.partner_id.street
            else:
                calleRec = "Ciudad"
            if self.partner_id.street2:
                calleRec = calleRec + ' ' + self.partner_id.street2
            if self.partner_id.city:
                municipioRec = self.partner_id.city
            else:
                municipioRec = ""
            if self.partner_id.state_id:
                departamentoRec = self.partner_id.state_id.name
            else:
                departamentoRec = ""
            if self.partner_id.zip:
                postalRec = self.partner_id.zip
            else:
                postalRec = "502"
            if self.partner_id.country_id:
                paisRec = self.partner_id.country_id.code
            else:
                paisRec = "GT"

        fases_lines = []  # Frase Information
        if not self.frase_ids:
            fases_lines = [[1, 1]]
        else:
            for frase in self.frase_ids:
                fases_lines.append([frase.codigo_escenario, frase.tipo_frase])
        #if self.move_type in ('out_refund', 'in_refund'):
        #    if self.nce_frase_ids:
        #        for frase in self.nce_frase_ids:
        #            fases_lines.append([frase.codigo_escenario, frase.tipo_frase])
        

        # currency = self.currency_id.name
        currency = self.currency_id.name or 'GTQ'

        uuid_txt = uuid.uuid4()
        self.uuid = uuid_txt

        Complemento_Data['origin_date'] = str(self.invoice_refund_id.invoice_date)
        Complemento_Data['auth_number_doc_origin'] = str(self.uuid)

        if self.move_type in ['out_invoice', 'in_invoice']:
            #raise UserError('Entro a genera el XML')
            if self.journal_id.factura_cambiaria:  # Cambiaria Invoice
                self.calculate_payment_info()
                _logger.info('****************FACTURA CAMBIARIA************************')
                res_xml = self.GenerateXML_FCAM(currency, fecha_str, no_acceso, "FCAM", afIVA, codeEstab, correoEmisor, nitEmisor, nombreComercial,
                                      nombreEmisor, calleEmisor, postalEmisor, municipioEmisor, departamentoEmisor, paisEmisor, correoRec,
                                      vatRec, nombreRec, calleRec, postalRec, municipioRec, departamentoRec, paisRec, fases_lines,
                                      _items, total_impuesto, gran_total, uuid_txt, Complemento_Data, AdendaSummary)
                #self.send_appfirma(res_xml)
                #self.xml_request = res_xml
            else:  # Normal Invoice
                res_xml = self.GenerateXML_FACT(currency, fecha_str, no_acceso, "FACT", afIVA, codeEstab, correoEmisor, nitEmisor, nombreComercial,
                                      nombreEmisor, calleEmisor, postalEmisor, municipioEmisor, departamentoEmisor, paisEmisor, correoRec,
                                      vatRec, nombreRec, calleRec, postalRec, municipioRec, departamentoRec, paisRec, fases_lines,
                                      _items, total_impuesto, gran_total, uuid_txt, AdendaSummary)
                #raise UserError(('%s')%(res_xml))
                #self.send_appfirma(res_xml)
                #self.xml_request = res_xml

        if self.move_type in ['out_refund', 'in_refund']:  # Credit Note
            #uuid_txt = self.uuid_refund
            #self.uuid = uuid_txt
            Complemento_Data['auth_number_doc_origin'] = str(self.uuid_refund)
            res_xml = self.GenerateXML_NCRE(currency, fecha_str, no_acceso, "NCRE", afIVA, codeEstab, correoEmisor, nitEmisor, nombreComercial,
                                  nombreEmisor, calleEmisor, postalEmisor, municipioEmisor, departamentoEmisor, paisEmisor, correoRec,
                                  vatRec, nombreRec, calleRec, postalRec, municipioRec, departamentoRec, paisRec, fases_lines,
                                  _items, total_impuesto, gran_total, uuid_txt, Complemento_Data, AdendaSummary)
            #self.send_appfirma(res_xml)
            #self.xml_request = res_xml
        # return super(AccountInvoice, self).action_invoice_open()
        return res_xml

    def generate_xml_export(self):
        res_xml = False
        megaprint_dateformat = "%Y-%m-%dT%H:%M:%S"
        no_lin = 1
        AdendaSummary = []
        Complemento_Data = {}
        _items = []
        total_impuesto = 0

        gran_total = 0

        # Generate 9 digit random number as a Access Number
        no_acceso = str(random.randint(100000000, 999999999))
        while True:
            acceso = self.env['account.move'].search_count([('no_acceso', '=', no_acceso)])
            if acceso > 0:
                no_acceso = str(random.randint(100000000, 999999999))
            else:
                break

        # Current time For the tag FechaHoraEmision
        fecha = fields.Datetime.context_timestamp(self.with_context(tz=self.env.user.tz), datetime.datetime.now())
        if fecha:
            fecha_str = str(fecha.strftime(megaprint_dateformat))
            self.fel_date = fecha_str
        
        if self.name:
            numero = self.name.split('/')
            if numero:
                AdendaSummary.append(numero[0]) #valor1
                AdendaSummary.append(numero[2]) #valor2
        AdendaSummary.append(str(numero_a_texto.Numero_a_Texto(self.amount_total))) #valor3
        AdendaSummary.append(str(self.amount_total)) #valor4
        AdendaSummary.append(str(self.invoice_payment_term_id.name)) #valor5
        AdendaSummary.append(str(self.invoice_origin)) #valor6
        for inv_line in self.invoice_line_ids:
            if inv_line.display_type == 'line_section':
                continue
            detail = []
            if inv_line.product_id.type == 'service':
                bien_servicio = 'S'
            else:
                bien_servicio = 'B'

            total_price = round((inv_line.price_unit * inv_line.quantity),2)
            discount = round(total_price * ((inv_line.discount or 0.0) / 100.0),2)
            # grabable = total_price - discount
            grabable = total_price
            MontoImp = 0.0
            total_impuesto += MontoImp
            total = grabable + MontoImp
            gran_total += total
            descripcion_not = inv_line.name
            #AdendaSummary.append(inv_line.name)

            if str(inv_line.product_uom_id.name):
                uom = "UNI"
            else:
                uom = inv_line.product_uom_id.name
                uom = uom.encode('utf-8')


            detail.append(bien_servicio)  # Product Type
            detail.append(no_lin)  # Line number
            no_lin += 1
            detail.append(inv_line.quantity)  # Product Quantity
            detail.append(uom)  # Unit Of Measure
            detail.append(descripcion_not)  # Product description
            detail.append(inv_line.price_unit)  # Price of the product
            detail.append(round(total_price,2))  # Total Price
            detail.append(discount)  # Product Discount
            # IVA info
            detail.append(round(grabable, 2))
            detail.append(inv_line.quantity)  # Product Quantity
            detail.append(round(MontoImp, 2))
            detail.append(round(total, 2))
            _items.append(detail)

        total_impuesto = round(total_impuesto, 2)
        gran_total = round(gran_total, 2)

        codeEstab = self.journal_id.codigo_est or ''  # Company Establishment Code
        afIVA = self.company_id.regimen_iva or 'GEN'  # Company Associated VAT regime OR 'GEN'(Default)
        correoEmisor = self.company_id.email or ''  # Company Email
        nitEmisor = self.company_id.vat or 'CF'  # Compant vat No
        nombreComercial = self.company_id.nombre_comercial or ''  # Company Tradename
        nombreRec = ""
        calleRec = ""
        departamentoRec = ""
        postalRec = ""
        paisRec = ""
        municipioRec = ""
        DatosCliente = False
        nombreEmisor = self.company_id.name or ''  # Company Name
        # Company Address Details
        if self.company_id.street:
            calleEmisor = self.company_id.street or ''
        else:
            calleEmisor = ""
        if self.company_id.street2:
            calleEmisor = calleEmisor + ' ' + self.company_id.street2 or ''
        if self.company_id.city:
            municipioEmisor = self.company_id.city or ''
        else:
            municipioEmisor = ''
        if self.company_id.state_id:
            departamentoEmisor = self.company_id.state_id.name or ''
        else:
            departamentoEmisor = ""
        if self.company_id.zip:
            postalEmisor = self.company_id.zip
        else:
            postalEmisor = "502"
        if self.company_id.country_id.code:
            paisEmisor = self.company_id.country_id.code or 'GT'
        else:
            paisEmisor = "GT"
        # Partner Details
        #if not self.partner_id.vat or self.partner_id.var != "CF":
        #DatosCliente = self.get_datos_cliente(nitEmisor, self.partner_id.vat)
        if self.partner_id.email:
            correoRec = self.partner_id.email
        else:
            correoRec = ""
        if self.partner_id.vat:
            vatRec = self.partner_id.vat
        elif self.partner_id.vat == 'EXPORT':
            vatRec = "EXPORT"
        elif self.partner_id.vat == "CF":
            vatRec = "CF"
        else:
            vatRec = "CF"
        if vatRec not in ['CF', 'EXPORT']:
            DatosCliente = self.get_datos_cliente((self.partner_vat if self.partner_vat else self.partner_id.vat))
            if DatosCliente:
                nombreRec = DatosCliente[0] if DatosCliente[0] else self.partner_id.name
                calleRec = DatosCliente[1] if DatosCliente[1] else "Ciudad"
                postalRec = self.partner_id.zip if self.partner_id.zip else "502"
                paisRec = self.partner_id.country_id.code if self.partner_id.country_id.code else "GT"
                municipioRec = self.partner_id.city if self.partner_id.city else ""
        else:
            if self.partner_id.name:   
                nombreRec = self.partner_id.name
            if self.partner_id.street:
                calleRec = self.partner_id.street
            else:
                calleRec = "Ciudad"
            if self.partner_id.street2:
                calleRec = calleRec + ' ' + self.partner_id.street2
            if self.partner_id.city:
                municipioRec = self.partner_id.city
            else:
                municipioRec = ""
            if self.partner_id.state_id:
                departamentoRec = self.partner_id.state_id.name
            else:
                departamentoRec = ""
            if self.partner_id.zip:
                postalRec = self.partner_id.zip
            else:
                postalRec = "502"
            if self.partner_id.country_id:
                paisRec = self.partner_id.country_id.code
            else:
                paisRec = "GT"

        fases_lines = [[1, 1]]  # Frase Information
        #if not self.frase_ids:
        #    fases_lines = [[1, 1]]
        #else:
        for frase in self.frase_ids:
            fases_lines.append([frase.codigo_escenario, frase.tipo_frase])
        #if not fases_lines:
        #    fases_lines = [[1, 1]]
            
        # Complementos (Accessories)
        arioODestinatario = ''
        direccionConsign = ''
        otraReferencia = ''
        incoterm = ''
        nombreExportador = ''
        codigoExportador = ''
        if self.partner_id :
            arioODestinatario = self.partner_id.name
        
        if self.partner_id.street:
            direccionConsign = self.partner_id.street
            
        if self.name :
            otraReferencia = self.name
        
        if self.invoice_incoterm_id :
            incoterm = self.invoice_incoterm_id.code
            
        if self.company_id.nombre_comercial :
            nombreExportador = self.company_id.nombre_comercial
        
        if self.company_id.codigoexportador :
            codigoExportador = self.company_id.codigoexportador
            
        
        

        # currency = self.currency_id.name
        currency = 'USD'
                         
        # Added by Dhrup 
        expr = ''
        if self.exportacion_fel:
            expr = "SI"  # for Exp=”SI”

        uuid_txt = uuid.uuid4()
        self.uuid = uuid_txt

        Complemento_Data['origin_date'] = str(self.invoice_refund_id.invoice_date)
        Complemento_Data['auth_number_doc_origin'] = str(self.uuid)

        if self.move_type in ['out_invoice', 'in_invoice']:
            res_xml = self.GenerateXML_EXPORT(currency,expr , fecha_str, no_acceso, "FACT", afIVA, codeEstab, correoEmisor, nitEmisor, nombreComercial,
                                  nombreEmisor, calleEmisor, postalEmisor, municipioEmisor, departamentoEmisor, paisEmisor, correoRec,
                                  vatRec, nombreRec, calleRec, postalRec, municipioRec, departamentoRec, paisRec, fases_lines,
                                  _items, total_impuesto, gran_total, uuid_txt, AdendaSummary, arioODestinatario, direccionConsign, otraReferencia, incoterm, nombreExportador, codigoExportador)
            #self.xml_request = res_xml
        if self.move_type in ['out_refund', 'in_refund']:  # Credit Note
            #uuid_txt = self.uuid_refund
            #self.uuid = uuid_txt
            Complemento_Data['auth_number_doc_origin'] = str(self.uuid_refund)
            res_xml = self.GenerateXML_NCRE_EXPORT(currency, expr, fecha_str, no_acceso, "NCRE", afIVA, codeEstab, correoEmisor, nitEmisor, nombreComercial,
                                  nombreEmisor, calleEmisor, postalEmisor, municipioEmisor, departamentoEmisor, paisEmisor, correoRec,
                                  vatRec, nombreRec, calleRec, postalRec, municipioRec, departamentoRec, paisRec, fases_lines,
                                  _items, total_impuesto, gran_total, uuid_txt, Complemento_Data, AdendaSummary)
        return res_xml


    def dte_request(self, xml_string=False, type_request=False, uuid_res=False, nit=False):
        xml = ""
        uuid_txt = uuid.uuid4()
        if xml_string:
            try:
                if type_request == 'FirmaDocumentoRequest':
                    FirmaDocument = Element('FirmaDocumentoRequest')
                    xml_dte = SubElement(FirmaDocument, 'xml_dte')
                    xml_dte.append(cdata.CDATA(xml_string))
                    xml = tostring(FirmaDocument)
                elif type_request == 'RegistraDocumentoXMLRequest':
                    RegistraDocumento = Element('RegistraDocumentoXMLRequest')
                    RegistraDocumento.set('id', str(uuid_txt).upper())
                    xml_dte = SubElement(RegistraDocumento, 'xml_dte')
                    xml_dte.append(cdata.CDATA(xml_string))
                    xml = tostring(RegistraDocumento)
                elif type_request == 'AnulaDocumentoXMLRequest':
                    AnulaDocumentoXMLRequest = Element('AnulaDocumentoXMLRequest')
                    AnulaDocumentoXMLRequest.set('id', str(uuid_txt).upper())
                    xml_dte = SubElement(AnulaDocumentoXMLRequest, 'xml_dte')
                    xml_dte.append(cdata.CDATA(xml_string))
                    xml = tostring(AnulaDocumentoXMLRequest)
                elif type_request == 'RetornaPDFRequest':
                    RetornaPDFRequest = Element('RetornaPDFRequest')
                    uuid_tag = SubElement(RetornaPDFRequest, 'uuid')
                    uuid_tag.text = str(uuid_res)
                    xml = tostring(RetornaPDFRequest)
                elif type_request == 'RetornaDatosClienteRequest':
                    RetornaCliente = Element('RetornaDatosClienteRequest')
                    nit_node = SubElement(RetornaCliente, 'nit')
                    nit_node.text = str(nit)
                    xml = tostring(RetornaCliente)
                return xml
            except Exception as e:
                raise UserError(("%s") %(e))
            #finally:
            #    return xml

    def register_dte(self, xml_signed):
        if xml_signed:
            _logger.info("*********************register_dte()***************************")
            _logger.info(xml_signed)
            xml = fromstring(xml_signed)
            xml_res = tostring(xml)
            response  = self.post_dte(xml_res.decode('utf-8'), 'register_dte')
            if response and response.status_code == 200:
                _logger.info(response.content.decode('utf-8'))
                self.xml_validation(response.content.decode('utf-8'))
                res_dict = self.get_xml_dict(response.content.decode('utf-8'))
                fel_dict = self.get_number_fel(res_dict['uuid'])
                pdf_xml = self.dte_request(xml_res, 'RetornaPDFRequest', res_dict['uuid'])
                pdf_response  = self.post_dte(pdf_xml.decode('utf-8'), 'pdf_dte')
                pdf_dict = self.get_pdf_dict(pdf_response.content.decode('utf-8'))
                self.write({
                    'xml_response': response.content.decode('utf-8'),
                    'uuid': res_dict['uuid'],
                    'fel_serie': fel_dict['serie'],
                    'fel_no': fel_dict['numero'],
                    'txt_filename': "%s.pdf" %(res_dict['uuid']),
                    #'file': base64.encodestring(base64.decodestring(str(pdf_dict['pdf']))),
                    'file': base64.decodebytes(base64.b64encode(str(pdf_dict.get('pdf', '')).encode('utf-8'))),
                })
            else:
                self.xml_validation(response.content.decode('utf-8'))
        return True
    
    def get_signature(self, xml_request):
        xml_signed = ""
        _logger.info("*********************get_signature()***************************")
        _logger.info(xml_request)
        if xml_request:
            response  = self.post_dte(xml_request, 'sign_dte')
            _logger.info(response.content.decode('utf-8'))
            if response and response.status_code == 200:
                self.xml_validation(response.content.decode('utf-8'))
                res_dict = self.get_xml_dict(response.content.decode('utf-8'))
                xml_signed = res_dict['xml_dte']
                self.write({
                    'xml_request': res_dict['xml_dte'],
                    'uuid': res_dict['uuid'],
                })
            else:
                self.xml_validation(response.content.decode('utf-8'))
        return xml_signed
    
    def post_dte(self, xml_request, type):
        """
            Types:
                * sign_dte : this type send a xml to sign at FirmaDocumentoRequest
                * register_dte : This type send a xm to sign a RegistraDocumentoXMLRequest
                * cancel_dte : This type send a xml to cancel
                * pdf_dte : This type return the binary pdf
                * customer_data : This tyep return the data of customer on invoice
        """
        if xml_request and type:
            response = False
            #Validaciones de contenido
            if not self.company_id.token_access:
                raise UserError(('La empresa %s no tiene token de autorizacion generado') %(self.company_id.name))
            if not self.company_id.url_request_signature:
                raise UserError(('No hay URL para firma de DTE en la compañia %s') %(self.company_id.name))
            if not self.company_id.url_request:
                raise UserError(('No hay URL para registro de DTE en la compañia %s') %(self.company_id.name))
            if not self.company_id.url_cancel:
                raise UserError(('No hay URL para anulacion de DTE en la compañia %s') %(self.company_id.name))
            if not self.company_id.url_pdf:
                raise UserError(('No hay URL para retorno de PDF para el DTE en la compañia %s') %(self.company_id.name))
            #Get url to send the xml
            if type == 'sign_dte':
                post_url = self.journal_id.company_id.url_request_signature
            elif type == 'register_dte':
                post_url = self.journal_id.company_id.url_request
            elif type == 'cancel_dte':
                post_url = self.journal_id.company_id.url_cancel
            elif type == 'pdf_dte':
                post_url = self.journal_id.company_id.url_pdf
            elif type == 'datos_cliente':
                post_url = self.journal_id.company_id.url_customer
            headers = {
                "Content-type": "application/xml",
                "Authorization": "Bearer " + str(self.company_id.token_access)
            }
            try:
                response  = requests.post(post_url, data=xml_request, headers=headers, stream=True, verify=False)
                return response
            except Exception as e:
                raise UserError(('%s') %(e))
            #finally:
            #    return response

    def get_xml_dict(self, xml_reponse):
        dict_res = {}
        if xml_reponse:
            xml = fromstring(xml_reponse)
            for child in xml:
                if child.tag ==  'xml_dte':
                    dict_res.update({'xml_dte': child.text})
                elif child.tag == 'uuid':
                    dict_res.update({'uuid': child.text})
        return dict_res

    def get_pdf_dict(self, xml_reponse):
        dict_res = {}
        if xml_reponse:
            xml = fromstring(xml_reponse)
            for child in xml:
                if child.tag == 'pdf':
                    dict_res.update({'pdf': child.text})
        return dict_res
    
    def xml_validation(self, xml_str):
        lst_errores = ""
        lst_tags = ""
        if xml_str:
            tree = fromstring(xml_str)
            for child in tree:
                if child.tag == 'tipo_respuesta':
                    if child.text != '0':
                        for subchild in tree:
                            if subchild.tag == 'listado_errores':
                                for error in subchild:
                                    for suberror in error:
                                       lst_errores += "%s %s \n" %(suberror.tag, suberror.text)
                                raise UserError(('%s') %(lst_errores))
            return True

    def get_number_fel(self, uuid):
        if uuid:
            hexa = '0x'
            uuid_res = uuid.split('-')
            serie = uuid_res[0]
            number = literal_eval(hexa + uuid_res[1] + uuid_res[2])
            return {
                'serie': serie,
                'numero': number,
            }

    def generate_xml_cancel(self):
        megaprint_dateformat = "%Y-%m-%dT%H:%M:%S"
        xml_str = ""
        for rec in self:
            try:
                GTAnulacionDocumento = Element('ns:GTAnulacionDocumento')
                GTAnulacionDocumento.set('xmlns:ds', 'http://www.w3.org/2000/09/xmldsig#')
                GTAnulacionDocumento.set('xmlns:ns', 'http://www.sat.gob.gt/dte/fel/0.1.0')
                GTAnulacionDocumento.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
                GTAnulacionDocumento.set('Version', '0.1')
                sat = SubElement(GTAnulacionDocumento, 'ns:SAT')
                AnulacionDTE = SubElement(sat, 'ns:AnulacionDTE')
                AnulacionDTE.set('ID', 'DatosCertificados')
                DatosGenerales = SubElement(AnulacionDTE, 'ns:DatosGenerales')
                DatosGenerales.set('ID', 'DatosAnulacion')
                DatosGenerales.set('NumeroDocumentoAAnular', str(rec.uuid))
                DatosGenerales.set('NITEmisor', str(rec.company_id.vat))
                DatosGenerales.set('IDReceptor', str(rec.partner_id.vat))
                DatosGenerales.set('FechaEmisionDocumentoAnular', str(rec.fel_date))
                date_fel = fields.Datetime.context_timestamp(self.with_context(tz=self.env.user.tz), datetime.datetime.now())
                DatosGenerales.set('FechaHoraAnulacion', str(date_fel.strftime(megaprint_dateformat)))
                DatosGenerales.set('MotivoAnulacion', str(rec.narration))
                #To XML to String
                xml_str = tostring(GTAnulacionDocumento)
                return xml_str
            except Exception as e:
                raise UserError(('%s') %(e))

    def action_cancel_fel(self):
        view = self.env.ref('account_invoice_megaprint.wizard_cancel_fel')
        new_id = self.env['wizard.fel.cancel']
        for rec in self:
            vals = {
                'invoice_id': rec.id or False,
            }
            view_id = new_id.create(vals)
            return {
                'name': _("Anulacion FEL"),
                'view_mode': 'form',
                'view_id': view.id,
                'res_id': view_id.id,
                'view_type': 'form',
                'res_model': 'wizard.fel.cancel',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }

    def post_cancel_dte(self):
        xml = self.generate_xml_cancel()
        xml_request = self.dte_request(xml_string=xml.decode('utf-8'), type_request='FirmaDocumentoRequest')
        response  = self.post_dte(xml_request, 'sign_dte')
        if response and response.status_code == 200:
            self.xml_validation(response.content.decode('utf-8'))
            res_dict = self.get_xml_dict(response.content.decode('utf-8'))
            xml_sign = res_dict['xml_dte']
            xml_signed = self.dte_request(xml_string=xml_sign, type_request='AnulaDocumentoXMLRequest')
            #raise UserError(('%s') %(xml_signed))
            response_2  = self.post_dte(xml_signed.decode('utf-8'), 'cancel_dte')
            if response_2 and response_2.status_code == 200:
                self.xml_validation(response_2.content.decode('utf-8'))
                #raise UserError(('%s') %(response_2.content)
                self.write({
                    'xml_response_cancel': response_2.content.decode('utf-8'),
                })
        return True

    def get_datos_cliente(self, nit_cliente=False):
        NombreCliente = ""
        DireccionCliente = ""
        if nit_cliente:
            XmlRequest = self.dte_request(xml_string=True, type_request='RetornaDatosClienteRequest', uuid_res=False, nit=nit_cliente)
            if XmlRequest:
                res = self.post_dte(xml_request=XmlRequest, type='datos_cliente')
                self.xml_validation(res.content.decode('utf-8'))
                NombreCliente = self.get_nombre(res.content.decode('utf-8'))
                DireccionCliente = self.get_direccion(res.content.decode('utf-8'))
        return NombreCliente, DireccionCliente
    
    def get_direccion(self, xml_str):
        var = ""
        if xml_str:
            tree = fromstring(xml_str)
            #root = tree.getroot()
            for child in tree:
                if child.tag == 'direcciones':
                    for subchild in child:
                        if subchild.tag == 'direccion':
                            var = subchild.text
        return var

    def get_nombre(self, xml_str):
        var = ""
        tree = fromstring(xml_str)
        for child in tree:
            if child.tag == 'nombre':
                var = child.text
        return var

    @api.model
    def create(self, vals):
        if 'frase_ids' not in vals:
            vals.update({
                'frase_ids': self.env.user.company_id.frase_ids.ids if self.env.user.company_id.frase_ids else False,
            })
        if 'nce_frase_ids' not in vals:
            vals.update({
                'nce_frase_ids': self.env.user.company_id.nce_frase_ids.ids if self.env.user.company_id.nce_frase_ids else False,
            })
        res = super(AccountInvoice, self).create(vals)
        return res

    # def action_print_fel(self):
    #     rec = self
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'name': 'Factura Electroncia',
    #         'url':"/web/content/?model=" + "account.move" +"&id=" + str(rec.id) + "&filename_field=file_name&field=file&download=true&filename=" + str(rec.txt_filename),
    #         'target': 'self',
    #     }

    def action_print_fel(self):
        return self.env.ref('account_invoice_megaprint.xetechs_fel_format').report_action(self)


    
    @api.onchange('partner_vat')
    def onchange_nit(self):
        if self.partner_vat:
            nit = self.partner_vat
            if '-' in nit:
                self.partner_vat = nit.replace('-', '')

AccountInvoice()
        
class MegaprintPaymentLine(models.Model):
    _name = 'megaprint.payment.line'
    _description = 'Megaprint Payment Line'
    _order = 'serial_no'

    invoice_id = fields.Many2one('account.move', 'Inovice')
    serial_no = fields.Integer('#No', readonly=True)
    amount = fields.Float('Monto', readonly=True, help='Amount')
    due_date = fields.Date('Vencimiento', readonly=True, help='Due Date')

MegaprintPaymentLine()

class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'
    def _prepare_default_reversal(self, move):
        res = super(AccountMoveReversal, self)._prepare_default_reversal(move)
        res.update({
            'invoice_refund_id': move.id or False,
        })
        return res

AccountMoveReversal()

class AccountInvoiceSend(models.TransientModel):
    _inherit = 'account.invoice.send'

    def _send_email(self):
        if self.is_email:
            for invoice in self.invoice_ids:
                if invoice.file:
                    pdf_attachment_id = self.env['ir.attachment'].create({
                        'name': invoice.txt_filename,
                        'datas': invoice.file,
                        'res_model': 'mail.compose.message',
                        'res_id': 0,
                        'type': 'binary'
                    })
                    self.composer_id.update({
                        'attachment_ids': [(6, 0, [pdf_attachment_id.id])],
                        'subject': (_('Factura %s') %(invoice.uuid)),
                    })
        return super(AccountInvoiceSend, self)._send_email()
AccountInvoiceSend()



