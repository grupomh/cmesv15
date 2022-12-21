# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class CallOfAttention(models.Model):
    _name = "call.of.attention"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "Llamado de atencion"
    _rec_order = "id desc"
    _rec_name = "name"


    def print_report(self):
        return self.env.ref('call_of_attention.action_report_call_of_attention').report_action(self)

    production_id = fields.Many2one('mrp.production', 'Orden de fabricacion', required=False,copy=False,readonly=True)
    bpm_id = fields.Many2one('registration.bpm', 'Registro BPMs', required=False, copy=False,readonly=True)
    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee','Empleado',required=True,copy=False,readonly=False,tracking=3)
    date = fields.Datetime('Fecha / Hora', required=True,copy=False,readonly=False,help="Ingrese una fecha valida",tracking=4)
    area = fields.Selection([
        ('refinado','Refinado'),
        ('confiteria','Confiteria'),
        ('envasado','Envasado'),
        ('encajado','Encajado'),
        ('extrusion','Extrusion'),
        ('bodega', 'Bodega'),
        ('administracion','Administracion'),
        ('otros','Otros')],'Area', required=True,readonly=False,copy=False,tracking=5)
    description = fields.Text('Descripcion', required=True,readonly=False, copy=False,tracking=2)
    company_id = fields.Many2one('res.company', 'Company', required=False, default=lambda self: self.env.company.id,readonly=True)
    type_bpm = fields.Boolean('BPMs', required=False,readonly=False,copy=False)
    type_ino = fields.Boolean('Inocuidad', required=False,readonly=False,copy=False)
    type_calidad = fields.Boolean('Calidad', required=False,readonly=False,copy=False)
    type_mante = fields.Boolean('Mantenimiento', required=False,readonly=False,copy=False)
    type_comp = fields.Boolean('Comportamiento', required=False,readonly=False,copy=False)
    type_otr = fields.Boolean('Otros', required=False,readonly=False,copy=False)
    firm = fields.Boolean('Firma', required=False,readonly=False,copy=False,tracking=1)
    

    bpm_selec = fields.Selection([
        ('uniforme', 'Uniforme'),
        ('lav_manos', 'Lavado de manos'),
        ('uñas', 'Uñas'),
        ('maquillaje', 'Maquillaje'),
        ('barba', 'Barba'),
        ('vestidor', 'Vestidor'),
        ('comedor','Comedor'),
        ('ingreso','Ingreso'),
        ('hig_personal','Higiene personal'),
        ('otros','Otros')],'BPMs',required=False,readonly=False,copy=False )

    ino_selec = fields.Selection([
        ('limpieza_area', 'Limpieza de area'),
        ('tablero_ino', 'Tablero de inocuidad'),
        ('limpieza','Limpieza'),
        ('contami_prod','Contaminacion en productos'),
        ('utensilios','Utensilios'),
        ('no_cumple_requi_v','No cumple requisitos de vestidores'),
        ('no_cumple_proto_cov', 'No cumple protocolo covid'),
        ('otros','Otros')],'Inocuidad',required=False,readonly=False,copy=False)
    
    cali_selec = fields.Selection([
        ('mal_proces', 'Mal procesamiento de productos'),
        ('falla_production', 'Fallas en produccion'),
        ('problem_envasa', 'Problemas de mal envasado'),
        ('state_product','Estado del producto'),
        ('otros','Otros')], 'Calidad',required=False,readonly=False,copy=False)

    mante_selec = fields.Selection([
        ('mala_mani_equip', 'Mala manipulacion de equipos'),
        ('danio_equip','Daño de equipos'),
        ('danio_infraestr', 'Daño de infraestructura'),
        ('otros','Otros')],'Mantenimiento',required=False,readonly=False,copy=False)
    
    comp_selec = fields.Selection([
        ('falta_norma','Falta a las normas'),
        ('puntualidad', 'Puntualidad'),
        ('ausencia','Ausencia'),
        ('vocabulario','Vocabulario'),
        ('falta_respeto','Falta de respeto'),
        ('no_acata_orden','No acata ordenes'),
        ('otros','Otros')],'Comportamiento',required=False,readonly=False,copy=False)


    @api.model
    def create(self,vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('call.of.attention') or _('New')
        res = super(CallOfAttention, self).create(vals)
        return res
    
CallOfAttention()