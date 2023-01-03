# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, api, fields
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.misc import formatLang


class ReportSaleBook(models.AbstractModel):
    _name = 'report.report_ventas_compras.report_sale_book'

    @api.model
    def _get_report_values(self, docids, data=None):
        company_id = data.get('form', {}).get(
            'company_id', False)
        if not company_id:
            company_id = self.env.user.company_id
        else:
            company_id = self.env['res.company'].browse(company_id[0])
        date = self._get_date(data)
        rows_per_page = 36
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

    # @api.multi
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

    # @api.multi
    def generate_records(self, data, company_id, rows_per_page):
        result = []
        #Aqui valido que si 'form' no trae valor devuelvo lista vacia [].
        if not data.get('form', False):
            return result

        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        total_iva = 0.00
        total_bienes_gravados = 0.00
        total_bienes_exentos = 0.00
        total_bienes_iva = 0.00
        total_bienes = 0.00
        total_serv_gravados = 0.00
        total_serv_exentos = 0.00
        total_serv_iva = 0.00
        total_expo_gravados = 0.00
        total_expo_exentos = 0.00
        total_expo_iva = 0.00
        total_nc_gravados = 0.00
        total_nc_exentos = 0.00
        total_nc_iva = 0.00
        total_nc = 0.00
        total_nd_gravados = 0.00
        total_nd_exentos = 0.00
        total_nd_iva = 0.00
        total_nd = 0.00
        total_ret = 0.00
        count_fact = 0
        count_total = 0
        count_cancel = 0
        count_nc = 0
        count_nd = 0
        journal_ids = data['form']['journal_ids']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        empresa = self.env['res.company'].browse(
            data['form']['company_id'][0])
        folio = data['form']['folio_inicial']
        facturas = self.env['account.move'].search(
            [('state', 'in', ['posted', 'cancel']),
             ('journal_id', 'in', journal_ids),
             ('date', '>=', date_from),
             ('date', '<=', date_to),
             ('company_id', '=', empresa.id)], order='invoice_date')
        establecimientos = ", ".join([
            jou.name for jou in self.env['account.journal'].browse(
                journal_ids)])

        i = 1
        for inv in facturas:
            #count_total += 1
            bien_local_gravado = 0.00
            servicio_local_gravado = 0.00
            bien_local_exento = 0.00
            servicio_local_exento = 0.00
            bien_expo_gravada = 0.00
            servicio_expo_gravada = 0.00
            bien_expo_exenta = 0.00
            servicio_expo_exento = 0.00
            iva_bien_l = 0.00
            iva_servicio_l = 0.00
            iva_bien_expo = 0.00
            iva_servicio_expo = 0.00
            total_iva = 0.00
            # amount_g = 0.00
            # amount_e = 0.00
            # amount_iva = 0.00
            tipo = inv.journal_id.name
            serie = inv.fel_serie
            numero = inv.fel_no
            retencion = 0.0
            fac_no = inv.force_name
            if inv.fel_no != '/':
                for tax in inv.amount_by_group:
                    if 'PERCIBIDO' in str(tax[0]).upper():
                        retencion = float(tax[1])
                for tax in inv.amount_by_group:
                    if 'RETENIDO' in str(tax[0]).upper():
                        retencion += float(tax[1])
                total_ret += retencion

            if inv.type == "out_refund":
                tipo = 'NC' if inv.amount_untaxed >= 0 else 'ND'
                count_nc += 1
            if inv.type == 'out_invoice':
                if inv.state == 'cancel':
                    count_cancel += 1
                if inv.state != 'cancel':
                    count_fact += 1
            count_total += 1
            for line in inv.invoice_line_ids:
                if inv.state != 'cancel':
                    precio = (line.quantity * line.price_unit)
                    discount = ((line.quantity * line.price_unit) * ((line.discount or 0.0) / 100.0))
                    #count_fact += 1
                else:
                    precio = 0.00
                    discount = 0.00
                    #count_cancel += 1
                precio = (precio - discount)
                if inv.currency_id != empresa.currency_id:
                    # precio = inv.currency_id.compute(
                    #    precio, empresa.currency_id)
                    precio = inv.currency_id._convert(precio, empresa.currency_id, empresa, inv.invoice_date or fields.Date.today())
                # discount = ((line.quantity * line.price_unit) * (1 - (line.discount or 0.0) / 100.0))
                # precio = precio
                if tipo == 'NC':
                    precio = precio * -1
                    #count_nc += 1
                    #count_fact -= 1
                # taxes = line.tax_ids.compute_all(
                #    precio, empresa.currency_id, line.quantity,
                #    line.product_id, inv.partner_id)
                taxes = line.tax_ids.compute_all(
                    precio, empresa.currency_id, 1.00,
                    line.product_id, inv.partner_id)
                aux_gravado = taxes['total_excluded']
                aux_iva = 0.00
                if line.tax_ids:
                    for tax in taxes['taxes']:
                        aux_iva += tax['amount']
                if line.product_id.tipo_gasto == "compra":
                    if not inv.exportacion_fel and 'exportación' not in inv.journal_id.name.lower():
                        if line.tax_ids:
                            bien_local_gravado += aux_gravado
                            iva_bien_l += aux_iva
                            if tipo == 'NC':
                                total_nc_gravados += aux_gravado
                                total_nc_iva += aux_iva
                            elif tipo == 'ND':
                                total_nd_gravados += aux_gravado
                                total_nd_iva += aux_iva
                            else:
                                total_bienes_gravados += aux_gravado
                                total_bienes_iva += aux_iva
                        else:
                            bien_local_exento += aux_gravado
                            if tipo == 'NC':
                                total_nc_exentos += aux_gravado
                            elif tipo == 'ND':
                                total_nd_exentos += aux_gravado
                            else:
                                total_bienes_exentos += aux_gravado
                    else:
                        if line.product_id.type == "service":
                            if line.tax_ids:
                                servicio_expo_gravada += aux_gravado
                                iva_servicio_expo += aux_iva
                            else:
                                servicio_expo_exento += aux_gravado
                        else:
                            if line.tax_ids:
                                bien_expo_gravada += aux_gravado
                                iva_bien_expo += aux_iva
                            else:
                                bien_expo_exenta += aux_gravado
                        if line.tax_ids:
                            if tipo == 'NC':
                                total_nc_gravados += aux_gravado
                                total_nc_iva += aux_iva
                            elif tipo == 'ND':
                                total_nd_gravados += aux_gravado
                                total_nd_iva += aux_iva
                            else:
                                total_expo_gravados += aux_gravado
                                total_expo_iva += aux_iva
                        else:
                            if tipo == 'NC':
                                total_nc_exentos += aux_gravado
                            elif tipo == 'ND':
                                total_nd_exentos += aux_gravado
                            else:
                                total_expo_exentos += aux_gravado
                elif line.product_id.tipo_gasto == "servicio":
                    if line.tax_ids:
                        servicio_local_gravado += aux_gravado
                        iva_servicio_l += aux_iva
                        if tipo == 'NC':
                            total_nc_gravados += aux_gravado
                            total_nc_iva += aux_iva
                        elif tipo == 'ND':
                            total_nd_gravados += aux_gravado
                            total_nd_iva += aux_iva
                        else:
                            total_serv_gravados += aux_gravado
                            total_serv_iva += aux_iva
                    else:
                        servicio_local_exento += aux_gravado
                        if tipo == 'NC':
                            total_nc_exentos += aux_gravado
                        elif tipo == 'ND':
                            total_nd_exentos += aux_gravado
                        else:
                            total_serv_exentos += aux_gravado
                elif line.product_id.tipo_gasto == "exportacion":
                    if line.product_id.type == "service":
                        if line.tax_ids:
                            servicio_expo_gravada += aux_gravado
                            iva_servicio_expo += aux_iva
                        else:
                            servicio_expo_exento += aux_gravado
                    else:
                        if line.tax_ids:
                            bien_expo_gravada += aux_gravado
                            iva_bien_expo += aux_iva
                        else:
                            bien_expo_exenta += aux_gravado
                    if line.tax_ids:
                        if tipo == 'NC':
                            total_nc_gravados += aux_gravado
                            total_nc_iva += aux_iva
                        elif tipo == 'ND':
                            total_nd_gravados += aux_gravado
                            total_nd_iva += aux_iva
                        else:
                            total_expo_gravados += aux_gravado
                            total_expo_iva += aux_iva
                    else:
                        if tipo == 'NC':
                            total_nc_exentos += aux_gravado
                        elif tipo == 'ND':
                            total_nd_exentos += aux_gravado
                        else:
                            total_expo_exentos += aux_gravado
            total_iva = sum([iva_bien_l, iva_servicio_l, iva_bien_expo,
                             iva_servicio_expo])
            amount_total = sum([bien_local_gravado, servicio_local_gravado,
                                bien_local_exento, servicio_local_exento,
                                bien_expo_gravada, servicio_expo_gravada,
                                bien_expo_exenta, servicio_expo_exento,
                                total_iva])
            date = inv.invoice_date if inv.invoice_date else inv.date
            linea = {
                'company': empresa.name.encode('ascii', 'ignore') or "",
                'nit': empresa.company_registry or "",
                'direccion': empresa.street.encode('ascii', 'ignore'),
                'folio_no': int(folio),
                'establecimientos': establecimientos,
                # 'mes': mes,
                'fecha': datetime.strptime(
                    str(date),
                    DEFAULT_SERVER_DATE_FORMAT).strftime(date_format),
                'tipo': tipo,
                'serie': serie,
                'numero': numero if numero else inv.name,
                'nit_cliente': inv.partner_id.vat or "C/F",
                'nrc_cliente': inv.partner_id.nrc or "C/F",
                'cliente': str(inv.partner_id.name).encode('ascii', 'ignore'),
                'bienes_gravados': bien_local_gravado,
                'servicios_gravados': servicio_local_gravado,
                'bienes_exentos': bien_local_exento,
                'servicios_exentos': servicio_local_exento,
                'bienes_e_gravados': bien_expo_gravada,
                'servicios_e_gravados': servicio_expo_gravada,
                'bienes_e_exentos': bien_expo_exenta,
                'servicios_e_exentos': servicio_expo_exento,
                'iva': total_iva,
                'subtotal': amount_total + retencion,
                'no': i,
                'retencion': retencion,
                'fac_no': fac_no,
                'id': inv.id
            }
            i += 1
            result.append(linea)
        total_bienes = sum([total_bienes_gravados, total_bienes_exentos,
                            total_bienes_iva])
        total_servicios = sum([total_serv_gravados, total_serv_exentos,
                               total_serv_iva])
        total_nc = sum([total_nc_gravados, total_nc_exentos, total_nc_iva])
        total_nd = sum([total_nd_gravados, total_nd_exentos, total_nd_iva])
        total_gravado = sum([total_bienes_gravados, total_serv_gravados,
                             total_nc_gravados, total_nd_gravados,
                             total_expo_gravados])
        total_exento = sum([total_bienes_exentos, total_serv_exentos,
                            total_nc_exentos, total_nd_exentos,
                            total_expo_exentos])
        total_imp = sum([total_bienes_iva, total_serv_iva, total_nc_iva,
                         total_nd_iva, total_expo_iva])
        linea = {
            'cliente': "Totales",
            'total_bienes_gravados': total_bienes_gravados,
            'total_bienes_exentos': total_bienes_exentos,
            'total_bienes_iva': total_bienes_iva,
            'total_bienes': total_bienes,
            'total_servicios_gravados': total_serv_gravados,
            'total_servicios_exentos': total_serv_exentos,
            'total_servicios_iva': total_serv_iva,
            'total_servicios': total_servicios,
            'total_nc_gravados': total_nc_gravados,
            'total_nc_exentos': total_nc_exentos,
            'total_nc_iva': total_nc_iva,
            'total_nc': total_nc,
            'total_nd_gravados': total_nd_gravados,
            'total_nd_exentos': total_nd_exentos,
            'total_nd_iva': total_nd_iva,
            'total_nd': total_nd,
            'total_expo_gravados': total_expo_gravados,
            'total_expo_exentos': total_expo_exentos,
            'total_expo_iva': total_expo_iva,
            'total_expor': sum([total_expo_gravados, total_expo_exentos,
                                total_expo_iva]),
            'total_gravado': total_gravado,
            'total_exento': total_exento,
            'total_iva': sum([total_bienes_iva, total_serv_iva,
                              total_nc_iva, total_nd_iva, total_expo_iva]),
            'total_total': sum([total_gravado, total_exento, total_imp, total_ret]),
            'total_ret': total_ret,
            'total_docs': count_total,
            'total_anuladas': count_cancel,
            'total_count_nc': count_nc,
            'total_facturas': count_fact,

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


class ReportSaleBookGuatemala(ReportSaleBook):
    _name = 'report.report_ventas_compras.report_sale_book_guatemala'


class ReportSaleBookCF(ReportSaleBook):
    _name = 'report.report_ventas_compras.report_sale_cf_book'

    def generate_records(self, data, company_id):
        result, linea = super(ReportSaleBookCF, self).generate_records(data, company_id)
        grouped_result = {}
        for row in result:
            if not row['fac_no']:
                continue
            fecha = row['fecha']
            if row['bienes_e_gravados'] or row['servicios_e_gravados'] or row['bienes_e_exentos'] or row[
                'servicios_e_exentos']:
                fecha += 'e'

            if fecha not in grouped_result:
                grouped_result[fecha] = {
                    'fecha': row['fecha'],
                    'del': row['fac_no'],
                    'al': row['fac_no'],
                    'gravadas': 0,
                    'gravadas_iva': 0,
                    'exentas': 0,
                    'exportacion': 0,
                    'retencion': 0,
                    'subtotal': 0,
                    'iva': 0,
                    'ventas_ter': 0
                }
            grouped_result[fecha]['gravadas'] += row['bienes_gravados'] + row['servicios_gravados']
            grouped_result[fecha]['exentas'] += row['bienes_exentos'] + row['servicios_exentos']
            grouped_result[fecha]['exportacion'] += row['bienes_e_gravados'] + row['servicios_e_gravados'] + row[
                'bienes_e_exentos'] + row['servicios_e_exentos']
            grouped_result[fecha]['retencion'] += row['retencion']
            grouped_result[fecha]['iva'] += row['iva']
            try:
                grouped_result[fecha]['del'] = row['fac_no'] if int(row['fac_no']) < int(
                    grouped_result[fecha]['del']) else grouped_result[fecha]['del']
                grouped_result[fecha]['al'] = row['fac_no'] if int(row['fac_no']) > int(
                    grouped_result[fecha]['del']) else grouped_result[fecha]['del']
            except ValueError:
                continue
            grouped_result[fecha]['gravadas_iva'] = grouped_result[fecha]['gravadas'] + grouped_result[fecha]['iva']
            grouped_result[fecha]['subtotal'] = grouped_result[fecha]['gravadas_iva'] + \
                                                grouped_result[fecha]['exportacion'] - \
                                                grouped_result[fecha]['retencion']
        result = grouped_result.values()

        return result, linea

