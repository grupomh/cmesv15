# -*- coding: utf-8 -*-
#------- 24-7 IT Support - Rafael Valencia - rvalencia@24-7itsupport.com -------# 
{
    'name' : "Workforce",
    'summary' : "Control de mano de obra de modulo de fabricacion",
    'autor': "24-7 IT Support",
    "version": "15.0.1.0.1",
    'sequence': 3,
    'depends':['base', 'base_setup', 'stock', 'mrp', 'hr', 'quality_control_points'],
    'data':[
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/mrp_workforce_view.xml',
        'views/mrp_production_view.xml',

    ],
    'demo':[],
    'qweb':[],
    'application':True,
    'installable':True,
    'auto_install':False,
}