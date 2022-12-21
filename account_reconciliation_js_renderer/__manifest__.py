# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Account reconciliation js renderer',
    'version': '1.0',
    'summary': 'Account reconciliation js renderer',
    'description': """
        Inherit assign payments widget and modify the template
    """,
    'category': 'Account',
    'depends': ['account','account_reports'],
    'data': [
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/template.xml'
    ],
    'web.assets_backend': [
        '/account_reconciliation_js_renderer/static/src/js/reconciliation_renderer.js'
    ],

}
