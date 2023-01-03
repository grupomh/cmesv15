#-*- coding:utf-8 -*-
#------- 24-7 IT Support - Rafael Valencia - rvalencia@24-7itsupport.com -------# 
{
    'name' : "Payroll accounding posted(account module)",
    'summary':"Realiza la validacion del asiento contable despues de validar la nomina",
    'author': "24-7 IT Support",
    "version": "15.0.1.0.1",
    'sequence': 2,
    'depends':['hr_payroll', 'account_accountant'],
    'data':[
        'views/hr_payroll_account_views.xml'
    ],
    'demo':[],
    'application':True,
    'installable':True,
    'auto_install':False,

}