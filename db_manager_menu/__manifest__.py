# -*- coding: utf-8 -*-
{
    'name': 'Button For Database Manager',
    'version': '1.0',
    'summary': """Adding new button to access database manager. In the menu.""",
    'description': """Adding new button to access database manager.""",
    'category': 'Base',
    'author': 'bisolv',
    'website': "",
    'license': 'AGPL-3',

    'depends': ['base'],

    'data': [
    ],

    'assets': {
        # 'web.assets_qweb': [
        #     'db_manager_menu/static/src/xml/menu.xml',
        # ],
        'web.assets_backend': [
            'db_manager_menu/static/src/js/database.js',
        ],
    },

    'demo': [

    ],
    'images': ['static/description/banner.png'],
    # 'qweb': [
    #     'static/src/xml/menu.xml',
    # ],

    'installable': True,
    'auto_install': False,
    'application': False,
}
