# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Sales Double Validation-Approval Workflow in Odoo',
    'version': '12.0.0.2',
    'category': 'sales',
    'summary': 'sale double approve sale order Double Validation Approval sale double approval process sale double validation sale order double approval sale approval workflow sale approval process sale order triple approval sale triple validation sale manager approval',
    'description': """
    Odoo Sales Double Validation sale double approve validation sale double validate sales double validate
    Odoo Sales Double approval workflow Sales Approval workflow Sales validation workflow Sale double validation
    Odoo sale approval workflow sale two step approval sale two step validation double validation on sales
    Odoo approval workflow on sales Validation process on sales Double validation on sales Confirm sales approval

    Odoo Quotation Double Validation Quotation Double approval workflow Quotation Approval workflow Quotation validation workflow
    Odoo Quotation double validation Quotation approval workflow Quotation two step approval Quotation two step validation
    Odoo double validation on quotation approval workflow on quotation Validation process on quotation Double validation on quotation Confirm Quotation approval
    
    Odoo Sales order Double Validation Sale order Double approval workflow Sales order Double approval workflow
    Odoo Sale order Double approval workflow Odoo Sales order Approval workflow
    Odoo Sales order validation workflow Sales order double validation Sales double approval Sales two time approval 
    Odoo sale approval Process Sale order approval workflow Sale double step approval sale aprroval process for sale
    Odoo Sales Order two step approval Sales Order two step validation sale double validation on sales
    approval workflow on sales Validation process on sales Double validation on sales Confirm sale approval


    Odoo Quotation Double Validation Quotation Double approval workflow Quotation Approval workflow
    Odoo Quotation validation workflow Quotation double validation Quotation approval workflow
    Odoo Quotation two step approval Quotation two step validation
    odoo double validation on Quotation approval workflow on Quotation Validation process on Quotation
    Odoo Double validation on Quotation Confirm customer order approval sale double approve


""",
    'author': 'BrowseInfo',
    'price': 25,
    'currency': "EUR",
    'live_test_url':'https://youtu.be/JII3FEfUaKQ',
    'website': 'https://www.browseinfo.in/',
    'depends': [
        'sale_management',
        'sale_stock',
        'stock_account',
        'partner_credit_limit',
        'mail',
        ],
    'data': [
	'views/sale_config_view.xml',
    'views/sale_order_view.xml',
    'data/mail_template_one.xml'
],
    'demo': [],
    'js': [],
    'qweb': [],
    'installable': True,
    'auto_install': False,
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
