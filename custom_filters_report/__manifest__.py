# -*- coding: utf-8 -*-
{
    'name': "Custom filters report",
    'summary': """
       Custom filters for the account reports""",
    'description': """
         Custom filters for the account reports
    """,
    'author': 'Fernando Flores --> fflores@xetechs.com',
	'maintainer': 'XETECHS, S.A.',
	'website': 'https://www.xetechs.com',
	'category': 'account',
    'version': '0.1',
    'depends': ['base', 'account_reports'],
    'data': [
        'views/assets.xml',
    ],
    'web.assets_backend': [
        '/custom_filters_report/static/src/js/account_reports.js'
    ],
}