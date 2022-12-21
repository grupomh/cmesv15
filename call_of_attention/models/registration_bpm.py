# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class RegistrationBpm(models.Model):
    _inherit = "registration.bpm"

    count_call_of_atention = fields.Integer (string='Call of attention count', compute='_compute_call_of_attention_count')

    def _compute_call_of_attention_count(self):
        for rec in self:
            count_call_of_atention = self.env['call.of.attention'].search_count([('bpm_id','=',rec.id)])
            rec.count_call_of_atention = count_call_of_atention


    def button_call_of_attention_action(self):
        self.ensure_one()
        return {
            'name': _('New Llamado de atencion'),
            'view_mode': 'form',
            'res_model': 'call.of.attention',
            'type': 'ir.actions.act_window',
            'context': {
                'default_company_id': self.company_id.id,
                'default_bpm_id': self.id,
            },
            'domain': [('bpm_id', '=', self.id)],
        }
    
    def call_of_attention_action_open_(self):
        self.ensure_one()
        action = {
            'name': _('Llamado de atencion'),
            'view_mode': 'tree,form',
            'res_model': 'call.of.attention',
            'type': 'ir.actions.act_window',
            'context': {'default_bpm_id': self.id,
                        'default_company_id': self.company_id.id
                        },
            #'target': 'new',
            'domain': [('bpm_id', '=', self.id)],
        }
        if self.count_call_of_atention ==1:
            bpms= self.env['call.of.attention'].search([('bpm_id','=',self.id)])
            action ['view_mode'] = 'form'
            action ['res_id']= bpms.id
        return action

RegistrationBpm()