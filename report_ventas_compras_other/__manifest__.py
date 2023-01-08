# -*- encoding: UTF-8 -*-

{
	'name': 'Libro de Ventas/Compras -Agregados-',
	'summary': """Libro de Ventas/Compras -Agregados-""",
	'version': '15.0.',
	'description': """Modulos que estaban en report_ventas_compras""",
	'category': 'account',
	'depends': ['account'],
	'license': 'AGPL-3',
	'data': [
		'views/product_template_view.xml',
		'views/account_journal.xml',
		'views/account_invocie_view.xml',
	],
	'demo': [],
	'installable': True,
	'auto_install': False,
}
