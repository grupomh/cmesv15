# -*- coding: utf-8 -*-

{
    'name' : "Kardex stock",
    'summary': "Kardex stock ",
    'autor': "support S.A.",
    'website':"",
    'sequence': 2,
    'depends':['base','base_setup'],
    'data':[
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/kardex_data.xml',
        'views/kardex_stock_views.xml',
    ],
    "assets": {
        'web.assets_backend': [
            '/kardex_testing/static/src/js/tree_view_button.js'
        ],
    },
    'demo':[],
    'qweb':['static/src/xml/*.xml'],
    'application':True,
    'installable':True,
    'auto_install':False,
}