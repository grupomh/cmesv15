# -*- coding: utf-8 -*-

from email.policy import default
from odoo import api, fields, models, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    count_call_of_atention=fields.Integer (string='Call of attention count', compute='_compute_call_of_attention_count')


    def _compute_call_of_attention_count(self):
        for rec in self:
            count_call_of_atention = self.env['call.of.attention'].search_count([('employee_id','=',rec.id)])
            rec.count_call_of_atention = count_call_of_atention

    def call_of_attention_action_open(self):
        return{
            'type':'ir.actions.act_window',
            'name':'Llamado de atencion',
            'res_model':'call.of.attention',
            'domain':[('employee_id','=',self.id)],
            'view_mode':'tree,form',
            'target':'current',
        }

HrEmployee()