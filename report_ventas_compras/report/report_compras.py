# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.misc import formatLang


class ReportPurchaseBook(models.AbstractModel):
    _name = 'report.report_ventas_compras.report_purchase_book'

    @api.model
    def _get_report_values(self, docids, data=None):
        company_id = data.get('form', {}).get(
            'company_id', False)
        if not company_id:
            company_id = self.env.user.company_id
        else:
            company_id = self.env['res.company'].browse(company_id[0])
        date = self._get_date(data)
        rows_per_page = 38
        data, ultima = self.generate_records(data, company_id, rows_per_page)
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'self': self,
            'data': data,
            'ultima': ultima,
            'format_price': self._format_price,
            'format_price2': self._format_price2,
            'company_id': company_id,
            'month': date[0],
            'year': date[1],
            'rows_per_page': rows_per_page
        }
        return docargs

    def _get_date(self, data):
        month = datetime.strptime(data['form']['date_to'], DEFAULT_SERVER_DATE_FORMAT).strftime("%B")
        year = datetime.strptime(data['form']['date_to'], DEFAULT_SERVER_DATE_FORMAT).strftime("%Y")
        months = {'january': 'enero', 'february': 'febrero', 'march': 'marzo', 'april': 'abril', 'may': 'mayo',
                  'june': 'junio', 'july': 'julio', 'august': 'agosto', 'september': 'septiembre',
                  'november': 'noviembre', 'december': 'diciembre'}
        for k, v in months.items(): month = month.lower().replace(k, v)
        return month.capitalize(), year

    def _format_price(self, price, currency_id):
        if not price:
            return '0.00'
        amount_f = formatLang(self.env, price, dp='Product Price',
                              currency_obj=currency_id)
        amount_f = amount_f.replace(currency_id.symbol, '').strip()
        return amount_f

    def _format_price2(self, price, currency_id=None):
        if not price:
            return '0.00'
        return "{:,.2f}".format(price)

    def generate_records(self, data, company_id, rows_per_page):
        result = []
        if not data.get('form', False):
            return result

        tax = self.env['account.tax']
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        tipo_doc = ""
        bienes_gravados = 0.00
        servicios_gravados = 0.00
        bienes_exentos = 0.00
        servicios_exentos = 0.00
        bienes_pc = 0.00
        servicios_pc = 0.00
        # retenciones = 0.00
        bienes_i_gravados = 0.00
        servicios_i_gravados = 0.00
        bienes_i_exentos = 0.00
        servicios_i_exentos = 0.00
        iva_bienes = 0.00
        iva_combustibles = 0.00
        iva_servicios = 0.00
        iva_impo = 0.00
        # iva_impo_s = 0.00
        # iva_impo_b = 0.00
        iva_subtotal = 0.00
        otros_impuestos = 0.00
        # idp = 0.00
        amount_g = 0.00
        amount_e = 0.00
        amount_pc = 0.00
        # amount_imp = 0.00
        amount_iva = 0.00
        subtotal = 0.00
        # total_iva = 0.00
        total_bienes_g = 0.00
        total_bienes_e = 0.00
        total_bienes_pc = 0.00
        # total_bienes = 0.00
        total_serv_g = 0.00
        total_serv_e = 0.00
        total_serv_pc = 0.00
        # total_serv= 0.00
        total_impo_g = 0.00
        total_impo_e = 0.00
        total_impo_pc = 0.00
        # total_impo = 0.00
        total_comb_g = 0.00
        total_comb_e = 0.00
        total_comb_pc = 0.00
        # total_comb = 0.00
        fac_pc = 0
        establecimientos = ""
        mes = ""
        journal_ids = data['form']['journal_ids']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        tax_ids = tax.search(
            ['|', ('tax_group_id', '=', data['form']['tax_id'][0]),
             ('tax_group_id', '=', data['form']['tax_id'][0]),
             ('type_tax_use', '=', 'purchase')]).mapped('id')
        # base_id = data['form']['base_id']
        compania = data['form']['company_id']
        folio = data['form']['folio_inicial']
        total_ret = 0.00
        facturas = self.env['account.move'].search(
            [('state', 'in', ['posted']),
             ('journal_id', 'in', journal_ids),
             ('date', '>=', date_from),
             ('date', '<=', date_to),
             ('invoice_date', '!=', False),
             ('company_id', '=', compania[0])], order='invoice_date,force_name')
        empresa = self.env['res.company'].browse([compania[0]])
        establecimientos = ", ".join([
            jou.name for jou in self.env['account.journal'].browse(
                journal_ids)])
        # for journal in self.env['account.journal'].browse(journal_ids):
        #     establecimientos += journal.name.encode(
        #         'ascii', 'ignore') + ", "
        no = 1
        for inv in facturas:
            # tipo_doc = inv.tipo_documento
            # if inv.type != 'in_invoice':
            #     tipo_doc = 'NC'
            tipo_doc = 'NC' if inv.type != 'in_invoice' else inv.tipo_documento
            bienes_gravados = 0.00
            servicios_gravados = 0.00
            bienes_exentos = 0.00
            servicios_exentos = 0.00
            bienes_pc = 0.00
            servicios_pc = 0.00
            bienes_i_gravados = 0.00
            servicios_i_gravados = 0.00
            bienes_i_exentos = 0.00
            servicios_i_exentos = 0.00
            iva_subtotal = 0.00
            # iva_subtotal_b = 0.00
            # iva_subtotal_s = 0.00
            # iva_subtotal_c = 0.00
            # iva_subtotal_i = 0.00
            otros_impuestos_b = 0.00
            otros_impuestos_s = 0.00
            retenciones_s = 0.00
            retenciones_b = 0.00
            amount_g = 0.00
            amount_e = 0.00
            amount_pc = 0.00
            # fac_pc = 0
            # amount_imp = 0.00
            amount_iva = 0.00
            # idp = 0.00
            subtotal = 0.00
            tipo_cambio = 1
            # cheque = inv.doc_origen_serie or ""
            # orden = inv.doc_origen_num or ""
            # if inv.currency_id.id != inv.company_id.currency_id.id:
            #    total = 0
            #    #for line in inv.line_ids:
            #    #    if line.account_id.id == inv.account_id.id:
            #    #        total += line.credit - line.debit
            #    tipo_cambio = 1.00
            estado = 'E'
            if inv.state == 'cancel':
                estado = 'A'
            retencion = 0.0
            retencion_terceros = 0.0
            fac_no = inv.force_name

            for tax in inv.amount_by_group:
                if 'RETENIDO 1%' in str(tax[0]).upper():
                    retencion = float(tax[1]) if inv.journal_id.name != "Nota de Crédito Compra" else float(-tax[1])
            total_ret += retencion
            fovial = 0

            for tax in inv.amount_by_group:
                if 'ISR' in str(tax[0]).upper():
                    retencion_terceros = float(tax[1])

                # Verificar si es una factura de combustible
                if 'FOVIAL' in str(tax[0]).upper():
                    fovial += tax[1]

            for line in inv.invoice_line_ids:

                precio = line.price_total if inv.state != 'cancel' else 0.0
                if inv.currency_id != empresa.currency_id:
                    precio = inv.currency_id._convert(precio, empresa.currency_id, empresa, inv.invoice_date)
                precio = precio if estado != 'A' else 0.0
                if tipo_doc == 'NC':
                    precio = precio * -1
                # taxes = line.tax_ids.compute_all(
                #    precio, empresa.currency_id, line.quantity,
                #    line.product_id, inv.partner_id)
                taxes = line.tax_ids.compute_all(
                    precio, empresa.currency_id, 1.00,
                    line.product_id, inv.partner_id)
                if line.product_id.tipo_gasto == 'compra':
                    if inv.tipo_documento == 'FPC':
                        fac_pc += 1
                        for i in taxes['taxes']:
                            # if all([i['base_code_id'] == base_id[0],
                            #         i['tax_code_id'] == tax_id[0]]):
                            if i['id'] in tax_ids:
                                bienes_pc += i['amount']
                                total_bienes_pc += i['amount']
                            elif i['amount'] > 0:
                                otros_impuestos_b += i['amount']
                        bienes_pc += (taxes['total_excluded'])
                        total_bienes_pc += (taxes['total_excluded'])
                        otros_impuestos_b = 0.00
                    else:
                        if line.tax_ids:
                            for i in taxes['taxes']:
                                # if all([i['base_code_id'] == base_id[0],
                                #         i['tax_code_id'] == tax_id[0]]):
                                if i['id'] in tax_ids:
                                    iva_subtotal += line.balance * 0.13
                                    iva_bienes += line.balance * 0.13
                                    # iva_subtotal += i['amount']
                                    # iva_bienes += i['amount']
                                elif i['amount'] > 0:
                                    otros_impuestos_b += i['amount']
                                elif i['amount'] < 0:
                                    retenciones_b += i['amount']
                                # bienes_gravados += (taxes['total_excluded'])
                                # total_bienes_g += (taxes['total_excluded'])
                            bienes_gravados += line.balance
                            total_bienes_g += line.balance
                            otros_impuestos_b = 0.00
                            retenciones_b = 0.00
                        else:
                            bienes_exentos += taxes['total_excluded']
                            total_bienes_e += taxes['total_excluded']
                elif line.product_id.tipo_gasto == 'servicio':
                    if inv.tipo_documento == 'FPC':
                        fac_pc += 1
                        for i in taxes['taxes']:
                            # if all([i['base_code_id'] == base_id[0],
                            #         i['tax_code_id'] == tax_id[0]]):
                            if i['id'] in tax_ids:
                                servicios_pc += i['amount']
                                total_serv_pc += i['amount']
                            elif i['amount'] > 0:
                                otros_impuestos_s += i['amount']
                        servicios_pc += (taxes['total_excluded'])
                        total_serv_pc += (taxes['total_excluded'])
                        otros_impuestos_s = 0.00
                    else:
                        if line.tax_ids:
                            for i in taxes['taxes']:
                                # if all([i['base_code_id'] == base_id[0],
                                #         i['tax_code_id'] == tax_id[0]]):
                                if i['id'] in tax_ids:
                                    iva_subtotal += i['amount']
                                    iva_servicios += i['amount']
                                elif i['amount'] > 0:
                                    otros_impuestos_s += i['amount']
                                elif i['amount'] < 0:
                                    retenciones_s += i['amount']
                                servicios_gravados += (taxes['total_excluded'])
                                total_serv_g += (taxes['total_excluded'])
                                otros_impuestos_s = 0.00
                                retenciones_s = 0.00
                        else:
                            servicios_exentos += taxes['total_excluded']
                            total_serv_e += taxes['total_excluded']
                elif line.product_id.tipo_gasto == 'combustibles':
                    if inv.tipo_documento == 'FPC':
                        fac_pc += 1
                        for i in taxes['taxes']:
                            # if all([i['base_code_id'] == base_id[0],
                            #         i['tax_code_id'] == tax_id[0]]):
                            if i['id'] in tax_ids:
                                bienes_pc += i['amount']
                                total_comb_pc += i['amount']
                            elif i['amount'] > 0:
                                otros_impuestos += i['amount']
                        bienes_pc += (taxes['total_excluded'])
                        total_comb_pc += (taxes['total_excluded'])
                    else:
                        if line.tax_ids:
                            for i in taxes['taxes']:
                                # if all([i['base_code_id'] == base_id[0],
                                #         i['tax_code_id'] == tax_id[0]]):
                                if i['id'] in tax_ids:
                                    iva_subtotal += i['amount']
                                    iva_combustibles += i['amount']
                                elif i['amount'] > 0:
                                    bienes_exentos += i['amount']
                                    total_comb_e += i['amount']
                                elif i['amount'] < 0:
                                    otros_impuestos += i['amount']
                            bienes_gravados += taxes['total_excluded']
                            total_comb_g += taxes['total_excluded']
                        else:
                            bienes_exentos += taxes['total_excluded']
                            total_comb_e += taxes['total_excluded']
                elif line.product_id.tipo_gasto == 'importacion':
                    if inv.tipo_documento == 'FPC':
                        fac_pc += 1
                        for i in taxes['taxes']:
                            # if all([i['base_code_id'] == base_id[0],
                            #         i['tax_code_id'] == tax_id[0]]):
                            if i['id'] in tax_ids:
                                amount_iva = i['amount']
                            # elif i['amount'] > 0:
                            #     amount_imp = i['amount']
                        amount_pc = (taxes['total_excluded'] + amount_iva)
                        amount_iva = 0.00
                    else:
                        if line.tax_ids:
                            for i in taxes['taxes']:
                                # if all([i['base_code_id'] == base_id[0],
                                #         i['tax_code_id'] == tax_id[0]]):
                                if i['id'] in tax_ids:
                                    amount_iva = i['amount']
                                # elif i['amount'] > 0:
                                #     amount_imp = i['amount']
                            amount_g = taxes['total_excluded']
                        else:
                            amount_e = taxes['total_excluded']
                    if line.product_id.type == "service":
                        if inv.tipo_documento == 'FPC':
                            servicios_pc += amount_pc
                            total_impo_pc += amount_pc
                        else:
                            if line.tax_ids:
                                servicios_i_gravados += amount_g
                                iva_subtotal += amount_iva
                                total_impo_g += amount_g
                                iva_impo += amount_iva
                            else:

                                servicios_i_exentos += amount_e
                                total_impo_e += amount_e
                    else:
                        if inv.tipo_documento == 'FPC':
                            bienes_pc += amount_pc
                            total_impo_pc += amount_pc
                        else:
                            if line.tax_ids:
                                bienes_i_gravados += amount_g
                                iva_subtotal += amount_iva
                                total_impo_g += amount_g
                                iva_impo += amount_iva
                            else:
                                bienes_i_exentos += amount_e
                                total_impo_e += amount_e
            # Agregar el 13% de la importacion al iva_subtotal
            if inv.DUCA:
                iva_subtotal += inv.DUCA

            bienes_exentos += fovial
            subtotal = sum([bienes_gravados, servicios_gravados,
                            bienes_exentos, servicios_exentos,
                            bienes_pc, servicios_pc, bienes_i_gravados,
                            servicios_i_gravados, bienes_i_exentos,
                            servicios_i_exentos, iva_subtotal, retencion])

            if inv.DUCA:
                bienes_i_gravados += inv.DUCA / 0.13
            elif not inv.DUCA and inv.journal_id.importacion:
                bienes_gravados = 0
                servicios_gravados = 0
                bienes_exentos = 0
                servicios_exentos = 0
                bienes_pc = 0
                servicios_pc = 0
                bienes_i_gravados = 0
                servicios_i_gravados = 0
                bienes_i_exentos = 0
                servicios_i_exentos = 0
                iva_subtotal = 0
                retencion = 0
                subtotal = 0

            linea = {
                'nit': empresa.company_registry or "",
                'company': empresa.name.encode('ascii', 'ignore') or '',
                'direccion': empresa.street.encode(
                    'ascii', 'ignore') or '',
                'folio_no': int(folio),
                'establecimientos': establecimientos,
                'mes': mes,
                'fecha': datetime.strptime(
                    str(inv.invoice_date),
                    DEFAULT_SERVER_DATE_FORMAT).strftime(date_format),
                'tipo': tipo_doc,
                'estado': estado,
                'serie': inv.serie_factura,
                'numero': inv.num_factura,
                'origen': "N/A",
                'nit_cliente': inv.partner_id.vat or "C/F",
                'nrc_cliente': inv.partner_id.nrc or "C/F",
                'cliente': inv.partner_id.name or '',
                'bienes_gravados': bienes_gravados,
                'servicios_gravados': servicios_gravados,
                'bienes_exentos': bienes_exentos,
                'servicios_exentos': servicios_exentos,
                'bienes_pc': bienes_pc,
                'servicios_pc': servicios_pc,
                'bienes_i_gravados': bienes_i_gravados,
                'servicios_i_gravados': servicios_i_gravados,
                'bienes_i_exentos': bienes_i_exentos,
                'servicios_i_exentos': servicios_i_exentos,
                'iva': iva_subtotal,
                'subtotal': subtotal,
                'no': no,
                'retencion': retencion,
                'retencion_terceros': retencion_terceros,
                'fac_no': fac_no,
                'importacion': inv.journal_id.importacion,
                'journal_name': inv.journal_id.name

            }
            no += 1
            result.append(linea)
        total_comb = sum([total_comb_g, total_comb_e, total_comb_pc,
                          iva_combustibles])
        total_g = sum([total_bienes_g, total_comb_g, total_serv_g,
                       total_impo_g])
        total_e = sum([total_bienes_e, total_comb_e, total_serv_e,
                       total_impo_e])
        total_pc = sum([total_bienes_pc, total_comb_pc, total_serv_pc,
                        total_impo_pc])
        total_iva = sum([iva_bienes, iva_servicios, iva_impo,
                         iva_combustibles])
        # total_total = sum([total_g, total_e, total_pc, total_iva])
        linea = {
            'cliente': "Totales",
            'total_bienes_g': total_bienes_g,
            'total_bienes_e': total_bienes_e,
            'total_bienes_pc': total_bienes_pc,
            'total_bienes_iva': iva_bienes,
            'total_bienes': sum([total_bienes_g, total_bienes_e,
                                 total_bienes_pc, iva_bienes]),
            'total_serv_g': total_serv_g,
            'total_serv_e': total_serv_e,
            'total_serv_pc': total_serv_pc,
            'total_serv_iva': iva_servicios,
            'total_serv': sum([total_serv_g, total_serv_e, total_serv_pc,
                               iva_servicios]),
            'total_impo_g': total_impo_g,
            'total_impo_e': total_impo_e,
            'total_impo_pc': total_impo_pc,
            'total_impo_iva': iva_impo,
            'total_impo': sum([total_impo_g, total_impo_e, total_impo_pc,
                               iva_impo]),
            'total_comb_g': total_comb_g,
            'total_comb_e': total_comb_e,
            'total_comb_pc': total_comb_pc,
            'total_comb_iva': iva_combustibles,
            'total_comb': total_comb,
            'total_g': total_g,
            'total_e': total_e,
            'total_pc': total_pc,
            'total_iva': total_iva,
            'total_total': sum([total_g, total_e, total_pc, total_iva]),
            'fac_pc': int(fac_pc),
            'fac_c': len(facturas) - fac_pc,
            'fac_total': len(facturas),
        }

        if company_id.country_id.code != 'SV':
            return result, linea
        else:
            results = []
            folio = 1
            i = 1
            rows = []
            for row in result:
                rows.append(row)
                if i == rows_per_page:
                    results.append([folio, rows])
                    rows = []
                    i = 1
                    folio += 1
                else:
                    i += 1
            if len(rows) > 0:
                results.append([folio, rows])
            return results, linea


class ReportPurchaseBookGuatemala(ReportPurchaseBook):
    _name = 'report.report_ventas_compras.report_purchase_book_guatemala'
