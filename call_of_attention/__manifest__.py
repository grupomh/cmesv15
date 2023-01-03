# -*- coding: utf-8 -*-
#------- 24-7 IT Support - Rafael Valencia - rvalencia@24-7itsupport.com -------#
{
    'name': "call_of_attention",
    'summary': "Sub-modulo de llamados de atencion visualizcion principal en el modulo de puntos de control, grupo MH",
    'author': "24-7 IT Support",
    "version": "15.0.1.0.1",
    'sequence' : 2,
    'depends':['base','base_setup','contacts','hr','mrp','quality_control_points'],
    'data':[
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/call_of_attention_data.xml',
        'views/call_of_attention_view.xml',
        'views/hr_employee_view.xml',
        'views/mrp_production_view.xml',
        'views/quality_control_points_view.xml',
        'report/actions.xml',
        'report/call_of_attention_template.xml',
        'report/paperformat.xml',
        'views/registration_bpm_view.xml'
        
    ],
    'demo':[],
    'qweb':[],
    'application':True,
    'installable':True,
    'auto_install':False,
}