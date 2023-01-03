# -*- coding: utf-8 -*-
#------- 24-7 IT Support - Rafael Valencia - rvalencia@24-7itsupport.com -------# 
{
    'name' :'Agregados a traslados (Inventarios)',
    'category': 'Production',
    'author': '24-7 IT Support',
    'sequence': 1,
    'summary': 'Contiene campo para traslados identificados con prespuestos para produccion, modificacion en domain para los traslados solo muestra lotes disponibles y deacuerdo a origen',
    "version": "15.0.1.0.1",
    'depends':['base_setup','mrp','stock','sale_management'],
    'data': [
        'views/stock_picking_view.xml',
        'report/albaran_report_inherit.xml',
        'report/reports.xml',
        'report/nota_envio.xml',

    ],
    'application':True,
    'installable':True,
    'auto_install':False,
}