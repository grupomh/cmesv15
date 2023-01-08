# -*- coding: utf-8 -*-
{
    'name': "Cancel invoices on batch",
    'summary': """Cancel invoices on batch""",
    'description': """
        Cancel invoices on batch
    """,

    'author': "Xetechs, S.A.",
    'support': "Luis Aquino --> laquino@xetechs.com",
    'website': "https://www.xetechs.com",
    'category': 'Account',
    'version': '1.0',
    'depends': ['account'],
    'data': [
        'wizard/wizard_confirm_batch_view.xml',
        'views/sale_view.xml',
    ],
}