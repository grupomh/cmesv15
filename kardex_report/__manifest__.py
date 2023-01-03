# -*- coding: utf-8 -*-
{
    'name': 'Kardex Report',
    'summary': """Reporte Kardex by product""",
    'version': '1.0.',
    'description': """Generate the Kardex report by product and date range""",
    'author': 'Fernando Flores --> fflores@xetechs.com',
    'maintainer': 'Xetechs, S.A.',
    'website': 'https://www.xetechs.odoo.com',
    'category': 'account',
    'depends': ['account', 'account_reports'],
    'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/kardex_report_data.xml',
        'views/report_kardex.xml',
        'views/search_template_view.xml',
    ],
}