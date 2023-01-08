# -*- coding: utf-8 -*-
#------- 24-7 IT Support - Rafael Valencia - rvalencia@24-7itsupport.com -------# 
{
    'name': 'Custom report Nomina Bono14/Agui',
    'author': '24-7 IT Support',
    'category': 'payslip',
    'summary': 'Reporte para poder imprimir nominas de Bonos 14 y aguinaldos GT para grupo MH. se tiene que modificar la fecha en el codigo. dependiendo de la fecha a imprimir se utiliza dos veces al año',
    'depends':['hr_contract','hr_holidays','hr_work_entry'],
    'data':[
        'reports/report_payslip_template2.xml',
        'reports/reports.xml',
    ],
    'installable':True,
    'auto_install':False,
}