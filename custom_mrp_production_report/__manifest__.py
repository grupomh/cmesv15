# -*- coding: utf-8 -*-

{
    'name' :'Reporte fabricacion perzonalizado -MH-',
    'category': 'Production',
    'author': 'Rafael Valencia',
    'sequence': 1,
    'summary': 'Reporte de produccion para fabricacion por lotes o tandas. tambien contiene campo para traslados identificados con prespuestos para produccion',
    'depends':['base_setup','mrp'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'report/reports.xml',
        'report/custom_production_report.xml',
        'views/mrp_production.xml',
    ],
    'application':True,
    'installable':True,
    'auto_install':False,
}