# -*- coding: utf-8 -*-

{
    'name': "Stock_lot_life",
    'summary': "Coloca la fecha de vencimineto en la vista tree de inventarios y cantidad a mano",
    'autor': "Rafael Valencia",
    'website':"",
    'sequence':2,
    'depends':['base','base_setup','stock'],
    'data':[
        'views/stock_quant_view.xml',

    ],
    'demo':[],
    'qweb':[],
    'application':True,
    'installable':True,
    'auto_install':False,
}