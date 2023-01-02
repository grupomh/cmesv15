# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Mass Duplicate Records in Odoo',
    'version': '15.0.0.2',
    'category': 'Extra Tools',
    'sequence': 15,
    'summary': 'App Duplicate mass orders customer invoice mass duplicate invoice Mass copy Records sales order mass copy vendor bills copy multiple records duplicate records copy records copy data mass copy data all in one duplicate records mass duplicate button for all',
    'description': """Allows you to duplicate multiple records from tree/list view.
    Mass Duplicate Records
    mass duplicate orders
    easy to duplicate records
    DUplicate mass orders
    duplicate mass records
    easy to duplicate mass records
    sales order mass duplicate sales order
    customer invoice mass duplicate invoice
    customer invoice mass duplicate customer invoice
    Supplier invoice mass duplicate supplier invoice
    vendor bills mass duplicate vendor bills
    purchase order mass duplicate purchase order
    manufacutring mass duplicate manufacturing order
    picking mass duplicate picking

Allows you to copy multiple records from tree/list view.
    Mass copy Records
    mass copy orders
    easy to copy records
    copy mass orders
    copy mass records
    easy to copy mass records
    sales order mass copy sales order
    customer invoice mass copy invoice
    customer invoice mass copy customer invoice
    Supplier invoice mass copy supplier invoice
    vendor bills mass copy vendor bills
    purchase order mass copy purchase order
    manufacutring mass copy manufacturing order
    picking mass copy picking
    In default odoo only allows to duplicate one record at a time via form view. This odoo apps module helps to duplicate multiple records from list/tree view at a time in any model(object).Its very simple to use, select multiple records from the list view and click "Mass Duplicate" button from menu action and it's very time saving feature to users to duplicate everything in one single click instead of copy each record one by one. 


    """,
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/web_duplicate_views.xml',
        ],
    'web.assets_backend': [
        'bi_mass_duplicate/static/src/js/list_extend.js'
    ],
   
    'css': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    "images":['static/description/Banner.png'],
}
