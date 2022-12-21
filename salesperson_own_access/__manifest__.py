# -*- coding: utf-8 -*-

{
  "name"                 :  "Salesperson Own Orders & Invoices",
  "summary"              :  """Salesperson Own Orders & Invoices""",
  "category"             :  "Website",
  "version"              :  "1.0.1",
  "sequence"             :  1,
  "author"               :  "Xetechs, S.A.",
  "license"              :  "Other proprietary",
  "website"              :  "https://www.xetechs.com",
  "support"              :  "Luis Aquino -> laquino@xetechs.com",
  "description"          :  """Sale order: see own leads group will have the below access: can see own Sales orders, can see own Invoices & can create invoices for own orders.""",
  "depends"              :  ['sale_management'],
  "data"                 :  [
                             'security/salesperson_security.xml',
                             'security/ir.model.access.csv',
                             'views/salesperson_own_access_views.xml',
                            ],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "pre_init_hook"        :  "pre_init_check",
}