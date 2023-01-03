# -*- coding: utf-8 -*-
#------- 24-7 IT Support - Rafael Valencia - rvalencia@24-7itsupport.com -------# 
{
    'name': "Run scheduler custom mrp",
    'summary': "Boton ejecucion planificada en modulo de fabricacion",
    'author': "24-7 IT Support",
    "version": "15.0.1.0.1",
    'sequence' : 2,
    'depends':['base','base_setup','mrp'],
    'data':[
        'views/mrp_production_view.xml'

    ],
    'demo':[],
    'qweb':[],
    'application':True,
    'installable':True,
    'auto_install':False,
}