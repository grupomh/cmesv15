# -*- coding: utf-8 -*-
#------- 24-7 IT Support - Rafael Valencia - rvalencia@24-7itsupport.com -------# 
{
    'name': "ADD Customized contratos",
    'summary' : "Modulo agrega a hr_contracts, campos para poder realizar descuentos en la nomina",
    'author': "24-7 IT Support",
    "version": "15.0.1.0.1",
    'secuence':5,
    'depends':['base', 'base_setup', 'hr_contract','hr_payroll'],
    'data':[
        'data/hr_contract_data.xml',
        'views/hr_contract_view.xml',

    ],
    'demo':[],
    'qweb':[],
    'application':True,
    'installable':True,
    'auto_install':False,
}