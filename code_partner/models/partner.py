# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.osv import expression
from odoo.exceptions import ValidationError


ROUTE_LIST = [
        ('01' ,'01'),
        ('02' ,'02'),
        ('03' ,'03'),
        ('04' ,'04'),
        ('05' ,'05'),
        ('06' ,'06'),
        ('07' ,'07'),
        ('08' ,'08'),
        ('09', '09'),
        ('10', '10')
    ]

class ResPartner(models.Model):
    _inherit = 'res.partner'

    route = fields.Selection(ROUTE_LIST, string="Route", default='01')
    number = fields.Char(string='Number')
    code = fields.Char(string="code")#, readonly=True, store=False, index=True, compute="_compute_code")
    '''
    @api.model
    def create(self, values):
        if not values.get('number', False):
            values['number'] = self.env['ir.sequence'].next_by_code('code.partner')
        return super(ResPartner, self).create(values)

    @api.depends('number', 'route')
    def _compute_code(self):
        for record in self:
            # record.check_code()
            if not record.route or not record.number:
                code = ''
            else:
                code = '%s.%s'%(record.route, record.number)
            record.update( dict(code=code) )
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if operator in ('ilike', 'like', '=', '=like', '=ilike'):
            domain = \
                expression.AND([args or [], ['|', '|',
                                             ('name', operator, name),
                                             ('number', operator, name),
                                             ('route', operator, name),
                                             ('code', operator, name)]
                                ])
            return self.search(domain, limit=limit).name_get()
        return super(ResPartner, self).name_search(name, args, operator, limit)
    '''
    def name_get(self):
        res = []
        new_name = ""
        for partner in self:
            new_name = ""
            name = partner._get_name()
            if partner.vat:
                new_name += "[%s]" %(partner.vat)
            if partner.code:
                new_name += "[%s]" %(partner.code)
            name = "%s - %s"  %(new_name, name)
            res.append((partner.id, name))
        return res