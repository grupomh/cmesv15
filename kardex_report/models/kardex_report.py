# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import config, date_utils, get_lang


class KardexReport(models.AbstractModel):
    _name = "kardex.report"
    _description = "Kardex Report"
    _inherit = "account.report"

    filter_date = {'mode': 'range', 'filter': 'this_month'}
    filter_product = True

    @api.model
    def _get_report_name(self):
        return "Kardex Report"

    def _get_templates(self):
        templates = super(KardexReport, self)._get_templates()
        templates['main_template'] = 'kardex_report.main_template'
        templates['line_template'] = 'kardex_report.line_template'
        return templates

    def _get_columns_name(self, options):
        return [{'name': ''}] * 18

    @api.model
    def _init_filter_product(self, options, previous_options=None):
        if not self.filter_product:
            return

        options['product'] = True
        options['products'] = previous_options and previous_options.get('products') or []
        selected_product_ids = [int(product) for product in options['products']]
        selected_products = selected_product_ids and self.env['product.product'].browse(selected_product_ids) or \
                            self.env[
                                'product.product']
        options['selected_products'] = selected_products.mapped('name')

    def _set_context(self, options):
        """This method will set information inside the context based on the options dict as some options need to be in context for the query_get method defined in account_move_line"""
        ctx = super(KardexReport, self)._set_context(options)
        if options.get('products'):
            ctx['products'] = self.env['product.product'].browse(
                [int(product) for product in options['products']])
        return ctx

    def get_report_informations(self, options):
        '''
        return a dictionary of informations that will be needed by the js widget, manager_id, footnotes, html of report and searchview, ...
        '''
        options = self._get_options(options)
        if options.get('product'):
            options['selected_products'] = [self.env['product.product'].browse(int(product)).name for product in
                                            options['products']]
        return super(KardexReport, self).get_report_informations(options)

    def _get_stock_moves(self, date, product):
        stock_moves = self.env['stock.move'].search([
            ('date', '>=', date.get('date_from')),
            ('date', '<=', date.get('date_to')),
            ('product_id', '=', product),
            ('company_id', '=', self.env.company.id),
            ('state', '=', 'done')
        ], order='date')
        if stock_moves:
            return stock_moves
        else:
            return []

    def _get_qty_on_inventory(self, date, product):
        query = """
            SELECT
                   COALESCE(SUM(CASE
                               WHEN spt.code = 'incoming'
                                   THEN sm.product_qty
                               WHEN sm.picking_id IS NULL
                                    THEN sm.product_qty
                               ELSE sm.product_qty * -1
                               END
                       ), 0) AS total
            FROM stock_move sm
                     LEFT JOIN stock_picking sp ON (sm.picking_id = sp.id)
                     LEFT JOIN stock_picking_type spt ON (sm.picking_type_id = spt.id)
            WHERE sm.product_id = %s
              AND sm.date < %s
              AND sm.state = 'done'
              AND sm.company_id = %s
        """
        self.env.cr.execute(query, (product, date.get('date_from'), self.env.company.id))
        print(query % (product, date.get('date_from'), self.env.company.id))
        result = self.env.cr.dictfetchall()
        return result[0]['total'] if result else 0

    @api.model
    def _get_lines(self, options, line_id=None):
        lines = []
        date = options.get('date')
        products = options.get('products')
        date_from = date.get('date_from')
        for product in products:
            product = self.env['product.product'].search([('id', '=', product)])[0]
            moves = self._get_stock_moves(date, product.id)
            qty_on_inventory = int(self._get_qty_on_inventory(date, product.id))
            amount_inventory = qty_on_inventory * product.standard_price
            total_inbound = 0
            total_outbound = 0
            total_amount_inbound = 0
            total_amount_outbound = 0
            lines += self._get_header(product)
            lines.append(self._get_initial_line(amount_inventory, date_from, product, qty_on_inventory))
            for index, move in enumerate(moves):
                order_line = move.sale_line_id if move.sale_line_id else move.purchase_line_id
                origin = order_line.order_id
                product = move.product_id
                inbound = int(move.product_qty) if (move.picking_type_id.code == 'incoming') or not move.picking_type_id else 0
                outbound = int(move.product_qty) * -1 if move.picking_type_id.code == 'outgoing' else 0
                amount_inbound = inbound * (order_line.price_unit if order_line else product.standard_price)
                amount_outbound = outbound * order_line.price_unit
                invoices = origin.invoice_ids.filtered(lambda inv: inv.state == 'posted')
                document = invoices[0].journal_id.name if invoices else move.name
                no_doc = invoices[0].name.split('/')[-1] if invoices else None
                total_inbound += inbound
                total_outbound += outbound
                total_amount_inbound += amount_inbound
                total_amount_outbound += amount_outbound
                lines.append({
                    'id': 'kardex_report_line{}'.format(index),
                    'name': str(index + 1),
                    'columns': [
                        {'name': move.date.date(), 'class': 'date'},
                        {'name': document, 'class': 'whitespace_print'},
                        {'name': no_doc, 'class': 'whitespace_print'},
                        {'name': origin.name, 'class': 'whitespace_print'},
                        {'name': origin.partner_id.name, 'class': 'whitespace_print'},
                        {'name': origin.partner_id.country_id.name, 'class': 'whitespace_print'},
                        {'name': product.categ_id.name, 'class': 'whitespace_print'},
                        {'name': product.uom_id.name, 'class': 'whitespace_print'},
                        {'name': self.format_value(order_line.price_unit), 'class': 'number'},
                        {'name': qty_on_inventory, 'class': 'number'},
                        {'name': inbound, 'class': 'number'},
                        {'name': outbound, 'class': 'number'},
                        {'name': qty_on_inventory + inbound + outbound, 'class': 'number'},
                        {'name': self.format_value(amount_inventory), 'class': 'number'},
                        {'name': self.format_value(amount_inbound), 'class': 'number'},
                        {'name': self.format_value(amount_outbound),
                         'class': 'number'},
                        {'name': self.format_value(amount_inventory + amount_inbound + amount_inbound),
                         'class': 'number'},
                    ],
                    'class': 'top-vertical-align',
                    'level': 3
                })
                qty_on_inventory += inbound + outbound
                amount_inventory += amount_inbound + amount_outbound
            lines.append(
                self._get_total_line(total_amount_inbound, total_amount_outbound, total_inbound, total_outbound))
            lines.append({'id': 'empty_line', 'columns': [{'name': ''}], 'level': 3})
            lines.append({'id': 'empty_line', 'columns': [{'name': ''}], 'level': 3})
        return lines

    def _get_total_line(self, total_amount_inbound, total_amount_outbound, total_inbound, total_outbound):
        return {
            'id': 'kardex_report_line_total',
            'name': '',
            'columns': [
                {'name': ''},
                {'name': ''},
                {'name': ''},
                # {'name': ''},
                {'name': ''},
                {'name': ''},
                {'name': ''},
                {'name': ''},
                {'name': ''},
                {'name': ''},
                {'name': ''},
                {'name': total_inbound, 'class': 'number report_total'},
                {'name': total_outbound * -1, 'class': 'number report_total'},
                {'name': ''},
                {'name': ''},
                {'name': self.format_value(total_amount_inbound), 'class': 'number report_total'},
                {'name': self.format_value(total_amount_outbound), 'class': 'number report_total'},
                {'name': ''}
            ],
            'level': 2
        }

    def _get_initial_line(self, amount_inventory, date_from, product, qty_on_inventory):
        return {
            'id': 'kardex_report_line0',
            'name': 0,
            'columns': [
                {'name': date_from, 'class': 'date'},
                {'name': '', 'class': 'whitespace_print'},
                {'name': '', 'class': 'whitespace_print'},
                {'name': '', 'class': 'whitespace_print'},
                {'name': 'SALDOS INICIALES', 'class': 'whitespace_print'},
                {'name': '', 'class': 'whitespace_print'},
                {'name': product.categ_id.name, 'class': 'whitespace_print'},
                {'name': product.uom_id.name, 'class': 'whitespace_print'},
                {'name': self.format_value(product.standard_price), 'class': 'number'},
                {'name': qty_on_inventory, 'class': 'number'},
                {'name': 0, 'class': 'number'},
                {'name': 0, 'class': 'number'},
                {'name': qty_on_inventory, 'class': 'number'},
                {'name': self.format_value(amount_inventory), 'class': 'number'},
                {'name': 0, 'class': 'number'},
                {'name': 0, 'class': 'number'},
                {'name': self.format_value(amount_inventory), 'class': 'number'},
            ],
            'class': 'top-vertical-align',
            'level': 3
        }

    def _get_header(self, product):
        return [
            {
                'id': 'header_product_1',
                'name': 'ID de Producto:',
                'columns': [
                    {'name': product.default_code if product.default_code else '',
                     'colspan': 5},
                ],
                'level': 2,
                'class': 'header_producto'

            },
            {
                'id': 'header_product_2',
                'name': 'Producto:',
                'columns': [
                    {'name': product.name, 'colspan': 5},
                ],
                'level': 2,
                'class': 'header_producto'

            },
            {
                'id': 'header_2',
                'name': '',
                'columns': [
                    {'name': ''},
                    {'name': ''},
                    {'name': ''},
                    {'name': ''},
                    {'name': ''},
                    {'name': ''},
                    {'name': ''},
                    {'name': ''},
                    {'name': ''},
                    {'name': 'UNIDADES', 'colspan': 4, 'class': 'header_1'},
                    {'name': 'MONTOS', 'colspan': 4, 'class': 'header_1'},
                ],
                'level': 3,
            },
            {
                'id': 'header_2',
                'name': 'No.',
                'columns': [
                    {'name': 'Fecha'},
                    {'name': 'Documento'},
                    {'name': 'No. Doc.'},
                    {'name': 'No. Fuente'},
                    {'name': 'Cliente / Proveedor'},
                    {'name': 'Nacionalidad'},
                    {'name': 'Categoria'},
                    {'name': 'Uni'},
                    {'name': 'Costo'},
                    {'name': 'Inicial'},
                    {'name': 'Entradas'},
                    {'name': 'Salidas'},
                    {'name': 'Final'},
                    {'name': 'Inicial'},
                    {'name': 'Entradas'},
                    {'name': 'Salidas'},
                    {'name': 'Final'},
                ],
                'level': 1
            }]

    # def get_pdf(self, options, minimal_layout=True):
    #     # As the assets are generated during the same transaction as the rendering of the
    #     # templates calling them, there is a scenario where the assets are unreachable: when
    #     # you make a request to read the assets while the transaction creating them is not done.
    #     # Indeed, when you make an asset request, the controller has to read the `ir.attachment`
    #     # table.
    #     # This scenario happens when you want to print a PDF report for the first time, as the
    #     # assets are not in cache and must be generated. To workaround this issue, we manually
    #     # commit the writes in the `ir.attachment` table. It is done thanks to a key in the context.
    #     if not config['test_enable']:
    #         self = self.with_context(commit_assetsbundle=True)
    #
    #     base_url = self.env['ir.config_parameter'].sudo().get_param('report.url') or self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #     rcontext = {
    #         'mode': 'print',
    #         'base_url': base_url,
    #         'company': self.env.company,
    #     }
    #
    #     body = self.env['ir.ui.view']._render_template(
    #         "account_reports.print_template",
    #         values=dict(rcontext),
    #     )
    #     body_html = self.with_context(print_mode=True).get_html(options)
    #
    #     body = body.replace(b'<body class="o_account_reports_body_print">', b'<body class="o_account_reports_body_print">' + body_html)
    #     if minimal_layout:
    #         header = ''
    #         footer = self.env['ir.actions.report']._render_template("web.internal_layout", values=rcontext)
    #         spec_paperformat_args = {'data-report-margin-top': 10, 'data-report-header-spacing': 10}
    #         footer = self.env['ir.actions.report']._render_template("web.minimal_layout", values=dict(rcontext, subst=True, body=footer))
    #     else:
    #         rcontext.update({
    #                 'css': '',
    #                 'o': self.env.user,
    #                 'res_company': self.env.company,
    #             })
    #         header = ''
    #         header = header.decode('utf-8') # Ensure that headers and footer are correctly encoded
    #         spec_paperformat_args = {}
    #         # Default header and footer in case the user customized web.external_layout and removed the header/footer
    #         headers = header.encode()
    #         footer = b''
    #         # parse header as new header contains header, body and footer
    #         try:
    #             root = lxml.html.fromstring(header)
    #             match_klass = "//div[contains(concat(' ', normalize-space(@class), ' '), ' {} ')]"
    #
    #             for node in root.xpath(match_klass.format('header')):
    #                 headers = lxml.html.tostring(node)
    #                 headers = self.env['ir.actions.report']._render_template("web.minimal_layout", values=dict(rcontext, subst=True, body=headers))
    #
    #             for node in root.xpath(match_klass.format('footer')):
    #                 footer = lxml.html.tostring(node)
    #                 footer = self.env['ir.actions.report']._render_template("web.minimal_layout", values=dict(rcontext, subst=True, body=footer))
    #
    #         except lxml.etree.XMLSyntaxError:
    #             headers = header.encode()
    #             footer = b''
    #         header = headers
    #
    #     landscape = False
    #     if len(self.with_context(print_mode=True).get_header(options)[-1]) > 5:
    #         landscape = True
    #
    #     return self.env['ir.actions.report']._run_wkhtmltopdf(
    #         [body],
    #         header='', footer=footer,
    #         landscape=landscape,
    #         specific_paperformat_args=spec_paperformat_args
    #     )
