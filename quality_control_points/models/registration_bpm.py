# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class RegistrationBpm(models.Model):
    _name='registration.bpm'
    _description='Registros de control de BPMs'
    _rec_order='id desc'
    _rec_name = "name"

    def print_report(self):
        return self.env.ref('quality_control_points.action_report_register_bpm').report_action(self)

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    date=fields.Datetime("Fecha", required=True, readonly=False, copy=False)
    company_id = fields.Many2one('res.company', 'Company', required=False, default=lambda self: self.env.company.id,readonly=True)
    turn=fields.Selection([
        ('diurno','Diurno'),
        ('nocturno','Nocturno')
        ], 'Turno', required=True,copy=False)
    #Relation Fields
    registration_bpm_lines_id = fields.One2many('registration.bpm.lines','registration_bpm_id', string="Lineas Registros de bpms", required=False, index=True,readonly=False,copy=False)
    
    @api.model
    def create(self,vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('registration.bpm') or _('New')
        res = super(RegistrationBpm, self).create(vals)
        return res

RegistrationBpm()

class RegistrationBpmLines(models.Model):
    _name = "registration.bpm.lines"
    _description = "Lineas en registro de bpms"
    _order = "id desc"

    
    employee_id=fields.Many2one('hr.employee', string="Empleado", required=True, copy=False,readonly=False, help="Ingrese el empleado que se ha revisado")
    description=fields.Text('Observaciones', required=False, copy=False, readonly=False)
    #UNIFORME
    t_shirt = fields.Boolean('Playera/Filipina', required=False, readonly=False, copy=False, help="Registre si cumple o no cumple", default=False)
    gabacha = fields.Boolean('Gabacha', required=False, readonly=False, copy=False, help="Registre si cumple o no cumple", default=False)
    pants = fields.Boolean('Pantalon', required=False, readonly=False, copy=False, help="Registre si cumple o no cumple", default=False)
    mask_cofia = fields.Boolean('Mascarilla/Cofia', required=False, readonly=False, copy=False, help="Registre si cumple o no cumple", default=False)
    shoe = fields.Boolean('Zapatos', required=False, readonly=False, copy=False, help="Registre si cumple o no cumple", default=False)
    equip_seg = fields.Boolean('Equipo de seg.', required=False, readonly=False, copy=False, help="Registre si cumple o no cumple", default=False)
    #ASEO PERSONAL
    maquillaje = fields.Boolean('Maquillaje/Barba', required=False, readonly=False, copy=False, help="Registre si cumple o no cumple", default=False)
    locion = fields.Boolean('Crema/Locion', required=False, readonly=False, copy=False, help="Registre si cumple o no cumple", default=False)
    long_pinter = fields.Boolean('Uñas /Largas /Pintada', required=False, readonly=False, copy=False, help="Registre si cumple o no cumple", default=False)
    accessory = fields.Boolean('Accesorios', required=False, readonly=False, copy=False, help="Registre si cumple o no cumple", default=False)
    object_perso = fields.Boolean('Objetos personales', required=False, readonly=False, copy=False, help="Registre si cumple o no cumple", default=False)
    


    #Relation Fields
    registration_bpm_id = fields.Many2one('registration.bpm', string='Registros de bpm', required=True, ondelete="cascade", index=True)
    reference = fields.Char('Referencia', related='registration_bpm_id.name', readonly=True, store=True)
RegistrationBpmLines()