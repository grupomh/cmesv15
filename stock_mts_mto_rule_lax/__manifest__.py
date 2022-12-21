# -*- encoding: UTF-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2015-Today Laxicon Solution.
#    (<http://laxicon.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
{
    'name': 'Stock MTS+MTO Rule',
    'summary': 'Add a MTS+MTO route',
    'version': '13.0.1.0.2',
    'development_status': 'Mature',
    'category': 'Warehouse',
    'website': 'www.laxicon.in',
    'author': 'Laxicon Solution',
    'license': 'AGPL-3',
    'price': 30.0,
    'sequence': 1,
    'currency': 'USD',
    'application': False,
    'installable': True,
    'depends': [
        'stock',
    ],
    'data': [
        'data/stock_data.xml',
        'view/pull_rule.xml',
        'view/warehouse.xml',
    ],
    'images': ['static/description/module_image.png'],
}
