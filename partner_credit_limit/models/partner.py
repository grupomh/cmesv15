# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends('company_id', 'user_id')
    def _show_credit_limit(self):
        self.ensure_one()
        for data in self:
            user = data.env.user
            if user.has_group('partner_credit_limit.group_access_credit_limit'):
                data.show_credit_limit = False
            else:
                data.show_credit_limit = True

    """# IMPORTANTE el campo show solo decide si mostrar uno de los dos credit_limit en la vista.
     revisar la vista de res_partner form en los views."""

    show_credit_limit = fields.Boolean(compute='_show_credit_limit')
    credit_limit = fields.Monetary(string='Credit Limit', default=1.00, tracking=True)
    apply_credit_limit = fields.Boolean(string='¿Aplicar Limite de credito?', default=False, tracking=True, help="Aplicar limite de credito, de lo contrario se tomara sin limite de credito")


ResPartner()
