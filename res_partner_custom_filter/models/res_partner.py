from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

class ProductTemplate(models.Model):
    _inherit = "res.partner"

    @api.depends('current_user')
    def _check_user(self):
        for data in self:
            current_user = data.env.user
            in_user = self.env['res.users'].search([('partner_id', '=', data.id)], limit=1)
            if in_user:
                data.show = True
            if data.company_id.id in data.env.companies.ids:
                data.show = True
            else:
                data.show = False

    @api.depends('company_id')
    def _compute_current_user(self):
        for data in self:
            data.current_user = self.env.user
            data._check_user()

    show = fields.Boolean(default=True)
    current_user = fields.Many2one('res.users', 'Current User', compute="_compute_current_user")






