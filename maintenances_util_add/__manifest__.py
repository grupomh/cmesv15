# -*- coding: utf-8 -*-
#------- 24-7 IT Support - Rafael Valencia - rvalencia@24-7itsupport.com -------# 
{
    'name' : "Maintenances Utilities Add",
    'summary': "Utilidades agregadas al modulo de mantenimiento MH",
    'autor': "24-7 IT Support",
    "version": "15.0.1.0.1",
    'sequence': 2,
    'depends':['base','base_setup', 'stock','mrp','maintenance', 'account', 'mrp_workforce'],
    'data':[
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/maintenances_request_data.xml',
        'views/maintenance_equipment_view.xml',
        'views/stock_quant_view.xml',
        'views/account_move_views.xml',
        'views/maintenance_request_view.xml',
        'views/stock_picking_view.xml',
        'views/stock_move_line_views.xml',
        'views/maintenances_bom.xml',
        'views/product_tmpl_views.xml',
        'report/inherit_report_deliveryslip.xml',

    ],
    'demo':[],
    'qweb':[],
    'application':True,
    'installable':True,
    'auto_install':False,
}