# -*- coding: utf-8 -*-
#------- 24-7 IT Support - Rafael Valencia - rvalencia@24-7itsupport.com -------# 
{
    'name': "Quality Control Points",
    'summary': "Puntos de control de calidad de modulo de fabricacion",
    'autor': "24-7 IT Support",
    "version": "15.0.1.0.1",
    'sequence': 2,
    'depends': ['base', 'base_setup','stock','mrp','hr'],
    'data':[
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/registration_bpm_data.xml',
        'views/quality_control_points_view.xml',
        'views/mrp_bom_view.xml',
        'views/mrp_production_view.xml',
        'views/registration_bpm_view.xml',
        'report/actions.xml',
        'report/registration_bpm_template.xml',
    ],
    'demo':[],
    'qweb':[],
    'application':True,
    'installable':True,
    'auto_install':False,
}