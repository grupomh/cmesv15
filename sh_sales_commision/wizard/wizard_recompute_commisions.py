# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models,fields,api
from odoo.exceptions import UserError, ValidationError
import time
from datetime import datetime
from dateutil import relativedelta


class WizardRecomputeCommisions(models.TransientModel):
    _name = 'wizard.recompute.commissions'
    _description = 'Wizard Recompute Commissions'

    date_from = fields.Date('Desde', required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    date_to = fields.Date('From', required=True, default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
    user_ids = fields.Many2many('res.users', 'rel_wizard_user', 'user_id', 'wizard_id', string='Vendedor', required=False)
    delete_old  = fields.Boolean('Borrar Comisiones Antigua', default=False)


    def recompute_commissions(self):
        for rec in self:
            args = [('payment_date', '>=', rec.date_from),('payment_date', '<=', rec.date_to),('state', 'not in', ('draft', 'cancelled')), ('company_id', '=', self.env.company.id)]
            if rec.user_ids:
                args.append(('vendedor_id', 'in', rec.user_ids.ids))
            payments_ids = self.env['account.payment'].search(args)
            if rec.delete_old:
                commision_ids = self.env['sale.commission.analysis'].search([('date', '>=', rec.date_from), ('date', '<=', rec.date_to), ('sales_person_id','in', rec.user_ids.ids)])
                commision_ids.unlink()
            for pay in payments_ids:
                pay.recompute_sale_commission()
        return True

WizardRecomputeCommisions()