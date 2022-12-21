# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.
{
	'name': 'Multiple Payment Branch',
	'version': '13.0.0.1',
	'category': 'Accounting',
	'sequence': 1,
    'summary': 'Multi-Payment Branch',
    'description': """Multi-Payment Branch""",
	'author' : 'Xetechs, S.A.',
	'website': 'https://www.xetechs.com',
	'depends': ['branch','bi_cs_multiple_payment'],
	'data': [
	    'views/account_payment_view.xml',
	],
	'installable': True,
	'application': True,
}
