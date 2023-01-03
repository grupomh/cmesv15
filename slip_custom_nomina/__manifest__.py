# -*- coding: utf-8 -*-
#------- 24-7 IT Support - Rafael Valencia - rvalencia@24-7itsupport.com -------# 
{
    'name' :'Custom Nomina report -Comprobante de pago-',
    'category': 'Accounting/Expenses',
    'author': '24-7 IT Support',
    'sequence': 1,
    'summary': 'Nomina personalizada para Comprobante de pago con envio de boleta via mail',
    "version": "15.0.1.0.1",
    'depends':['base_setup','account','mail'],
    'data': [
        'security/groups.xml',
        'report/reports.xml',
        'report/custom_nomina_template_devel.xml',
        'data/email_template.xml',
        'views/hr_payslip_view.xml',
    ],
    'application':True,
    'installable':True,
    'auto_install':False,
}