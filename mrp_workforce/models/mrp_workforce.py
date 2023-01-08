# -*- coding: utf-8 -*-

#from importlib.metadata import requires
from odoo import api, fields, models, _


class MrpWorkforce(models.Model):
    _name="mrp.workforce"
    _description="Mano de obra fabricacion"
    _rec_order="id desc"
    _rec_name ="name"

    def _default_currency_id(self):
        company_id = self.env.context.get('company_id') or self.env.company.id
        return self.env['res.company'].browse(company_id).currency_id


    name = fields.Char(required=False, compute="_copy_production_id", readonly=True)
    production_id = fields.Many2one('mrp.production','Orden de produccion', require=False, ondelete="cascade", index=True,readonly=True,copy=False)
    date_production = fields.Datetime('Fecha de produccion', required=False, copy=False, readonly=True, related='production_id.date_planned_start')
    company_id = fields.Many2one('res.company', 'Compañia', required=False, default=lambda self: self.env.company.id,readonly=True)
    employee_id = fields.Many2one('hr.employee', 'Empleado',required=True, copy=False )
    turn_production = fields.Selection('Turno produccion', required=False, copy=False,readonly=True, related='production_id.turn')
    turn_justification = fields.Selection([
        ('Diurno','Diurno'),
        ('Nocturno','Nocturno')],'Turno justificacion', required=False,copy=False,readonly=False)
    date_justification=fields.Datetime('Fecha de justificacion',required=False,copy=False,readonly=False)
    qty_production=fields.Float('Cantidad producida',required=False,copy=False,readonly=True,related='production_id.product_qty')
    turn_report= fields.Char('Turno reportado', required=False, copy=False, readonly=True, compute="_report_turn")
    date_report= fields.Datetime('Fecha de reporte', required=False, copy=False, readonly=True, compute="_report_date")
    cost_report=fields.Monetary('Costo reporte', required=False, copy=False, readonly=True, compute="_cal_cost_report")
    maintenance_request_id=fields.Many2one('maintenance.request', 'Peticion de mantenimiento',  required=False, copy=False, readonly=False)
    maintenance_equipment_id=fields.Many2one('maintenance.equipment',"Equipo mantenimiento",related='maintenance_request_id.equipment_id', required=False, copy=False, readonly=True)

    justification = fields.Boolean('Justificacion', readonly=False, copy=False, required=False, help="Cuando el empleado falte este campo habilitara deplegable de algun tipo de justificacion")
    hours_report = fields.Float('Horas reportadas', readonly=False, copy=False, required=True)
    reference= fields.Char('Referencia',readonly=True,copy=False, required=False,compute="_reference_justification")

    job_employ = fields.Char('Puesto', readonly=True, copy=False, required=False, related='employee_id.job_id.display_name')
    currency_id = fields.Many2one('res.currency', 'Moneda',default= _default_currency_id,readonly=True)
    salary = fields.Monetary('Salario', readonly=True, copy=False, required=False, related='employee_id.contract_id.wage')
    hour_salary = fields.Monetary('Valor hora', readonly=True,copy=False, required=False, compute="_cal_hour_salary")

    type_justifica = fields.Selection([
        ('Cita IGSS', 'Cita IGSS'),
        ('Enfermedad', 'Enfermedad'),
        ('Permiso con goce de Salario', 'Permiso CON goce de Salario'),
        ('Día a cuenta de vacaciones', 'Vacaciones'),
        ('Ausencia Injustificada', 'Ausencia Injustificada'),
        ('Paro de maquina', 'Paro de maquina'),
        ('Reproceso','Reproceso'),
        ('Feriado / cumpleaños', 'Feriado / cumpleaños'),
        ('Mantenimiento general', 'Mantenimiento general'),
        ('Mantenimiento maquina', 'Mantenimiento maquina')],'Tipo de justificacion', required=False,readonly=False, copy=False)


    @api.depends("production_id")
    def _copy_production_id(self):
        for record in self:
            record['name'] = record.reference


    @api.depends("justification")
    def _reference_justification(self):
        for record in self:
            if record.justification == True:
                record['reference'] = record.type_justifica
            elif record.justification == False:
                record['reference'] = record.production_id.name
            else:
                record['reference']=False

    @api.depends("salary")
    def _cal_hour_salary(self):
        for record in self:
            record['hour_salary'] = record.salary * 1.4185 / 30 /8


    @api.depends("justification", "turn_justification", "turn_production")
    def _report_turn(self):
        for record in self:
            if record.justification == True:
                record['turn_report'] = record.turn_justification
            elif record.justification == False:
                record['turn_report'] = record.turn_production
            else:
                record['turn_report']=False


    @api.depends("justification", "date_justification", "date_production")
    def _report_date(self):
        for record in self:
            if record.justification == True:
                record['date_report'] = record.date_justification
            elif record.justification == False:
                record['date_report'] = record.date_production
            else:
                record['date_report']=False

    @api.depends("hours_report")
    def _cal_cost_report (self):
        for record in self:
            record['cost_report'] = record.hours_report * 38.25

MrpWorkforce()
