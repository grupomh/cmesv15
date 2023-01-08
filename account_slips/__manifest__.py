# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Account Slips',
    'version': '1.0',
    'summary': 'Account Slips For outstanding payments and receipts.',
    'sequence': 1,
    'description': """
Manage your outstaing Payments (Payment Slips) and Outstanding Receipts (Collection Slips).
    """,
    'category': 'Account',
    'author': 'Xetechs, S.A.',
    'support': 'Luis Aquino - laquino@xetechs.com',
    'website': 'https://www.xetechs.com',
    'depends': ['sale', 'purchase', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/sequence_data.xml',
        'views/account_slip_view.xml',
        'views/collection_slip_report_template.xml',
        'views/collection_slip_report.xml',
        'views/res_company_view.xml',
        'data/email_template_data.xml',
    ],
    'demo': [],
    'images': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
