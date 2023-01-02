# -*- coding: utf-8 -*-
#------- 24-7 IT Support - Rafael Valencia - rvalencia@24-7itsupport.com -------# 
{
    'name' : "Custom formato presupuesto -GravoPlex- ",
    'summary': "Formato de impresion personalizado del presupuesto",
    'autor': "24-7 IT Support",
    "version": "15.0.1.0.1",
    'sequence': 2,
    'depends':['base','base_setup', 'sale'],
    'data':[
        'report/action.xml',
        'report/sale_report_gravo.xml',
    ],
    'demo':[],
    'qweb':[],
    'application':True,
    'installable':True,
    'auto_install':False,
}