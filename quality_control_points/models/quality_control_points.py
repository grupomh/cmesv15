# -*- coding: utf-8 -*-

from copy import copy
from email.policy import default
#from importlib.metadata import requires
from unicodedata import name
from odoo import api, fields, models, _

class QualityControlPoints(models.Model):
    _name = "quality.control.points"
    _description = "Puntos de control calidad"
    _rec_order = "id desc"
    _rec_name = "name"

    #Campos del modelo
    #seccion relacionado con modulo fabricacion
    name = fields.Char(required=True, compute="_copy_production_id", readonly=True)
    product_id = fields.Many2one('product.product','Producto', required=False, store=True, related='production_id.product_id')        
    cat_process = fields.Selection(string='Proceso',store=True,readonly=True,related='production_id.cat_process')
    company_id = fields.Many2one('res.company', 'Company', required=False, default=lambda self: self.env.company.id,readonly=True)
    turn = fields.Selection(string='Turno', store=True, readonly=True, related='production_id.turn')


    move_id = fields.Integer(string='production', required=False, store=True, related='production_id.id')

    production_id = fields.Many2one('mrp.production',string="Orden de produccion",required=False, ondelete="cascade", index=True, readonly=True)

    maintance_equipment_ids=fields.Many2many('maintenance.equipment','maintance_equip_rel','quality_control_points_id','maintenance_equipment_id',string='Equipo',copy=False)

    employee_id = fields.Many2many('hr.employee','hr_employe_rel','quality_control_points_id','hr_employe_id',string='Empleados',required=True,copy=False,readonly=False)

        #seccion de Envasado
    grams_weights_qty = fields.Float('Peso gramos', required=False, readonly=False, copy=False, help="Introduce peso en gramos", default=0.00)
    meets_weight = fields.Boolean('Cumple peso', required=False, readonly=False, copy=False, help="cumple con el peso", default=False)
    horizontal_seal = fields.Boolean('Sello horizontal', required=False, readonly=False, copy=False, help="Cumple el sello horizontal", default=False)
    vertical_seal = fields.Boolean('Sello vertical', required=False, readonly=False, copy=False, help="Cumple el sello vertical", default=False)
    centered_art = fields.Boolean('Arte centrado', required=False, readonly=False, copy=False, help="Cumple con el arte centrado", default=False)
    batch_printing = fields.Boolean('Impresion lote', required=False, readonly=False, copy=False, help="Cumple con la impresion de lote", default=False)
    date_printing = fields.Boolean('Impresion fecha', required=False, readonly=False, copy=False, help="Cumple con la impresion de la fecha", default=False)
    #seccion de galletas Extrusion
    rpm_ex_qty = fields.Float('RPM / Extrusion', required=False, readonly=False, copy=False, help="introducir revoluciones de extrusor", default=0.00)
    rpm_dos_qty = fields.Float('RPM / Dosificador', required=False, readonly=False, copy=False, help="introducir revoluciones de dosificador", default=0.00)
    rpm_rodihal_qty = fields.Float('RPM / Rodillo Halador', required=False, readonly=False, copy=False, help="introducir revoluciones de rodillo halador", default=0.00)
    rpm_rodicu_qty = fields.Float('RPM / Rodillo de Cuchilla', required=False, readonly=False, copy=False, help="introducir revoluciones de rodillo de cuchilla", default=0.00)
    rpm_bomb_qty = fields.Float('RPM / Bomba de relleno', required=False, readonly=False, copy=False, help="introducir revoluciones de bomba de relleno", default=0.00)
    rpm_band_qty = fields.Float('RPM / Banda de horno', required=False, readonly=False, copy=False, help="introducir revoluciones de banda de horno", default=0.00)
    #seccion de Bases de Extrusion
    diametro_qty = fields.Float('Diametro de base', required=False, readonly=False, copy=False, help="Diametro de base", default=0.00)
    weight_bag = fields.Boolean('Peso de bolsa', required=False, readonly=False, copy=False, help="Cumple con el peso de bolsa final", default=False)
    #seccion de FirstClass
    clean_jar = fields.Boolean('Frasco limpio', required=False, readonly=False, copy=False, help="Cumple con la limpieza del frasco", default=False)
    correct_sleeve = fields.Boolean('Manga derecha', required=False, readonly=False, copy=False, help="Cumple con la posicion correcta al frasco", default=False)
    add_sleeve = fields.Boolean('Manga adherida al frasco', required=False, readonly=False, copy=False, help="Cumple la manga con adherencia al frasco", default=False)
    sealing_margin = fields.Boolean('Margen de sellado', required=False, readonly=False, copy=False, help="Cumple con el margen de sellado", default=False)
    security_seal = fields.Boolean('Sello de seguridad', required=False, readonly=False, copy=False, help="Cumple con el sello de seguridad", default=False)
    #seccion de Encajado
    box_weight = fields.Boolean('Cumple peso de caja', required=False, readonly=False, copy=False, help="Cumple con el peso de caja terminada", default=False)
    armed_box = fields.Boolean('Armado de caja', required=False, readonly=False, copy=False, help="Cumple con armado de caja terminado", default=False)
    box_sealing = fields.Boolean('Sellado de caja', required=False, readonly=False, copy=False, help="Cumple con el sellado de caja", default=False)
    bag_sealing = fields.Boolean('Sellado de bolsa', required=False, readonly=False, copy=False, help="Cumple con el sellaod de bolsas de caja terminada", default=False)
    labelled = fields.Boolean('Etiquetado', required=False, readonly=False, copy=False, help="Cumple con el etiquetado del producto terminado", default=False)
    parquet = fields.Boolean('Entarimado', required=False, readonly=False, copy=False, help="Cumple el entarimado de producto terminado", default=False)
    #seccion de Chocotaza
    vibrated_time = fields.Boolean('Tiempo vibrado', required=False, readonly=False, copy=False, help="Cumple con el tiempo de vibrado", default=False)
    bar_length_qty = fields.Float('Largo de barra', required=False, readonly=False, copy=False, help="introducir largo de la barra", default=0.00)
    bar_width_qty = fields.Float('Ancho de barra', required=False, readonly=False, copy=False, help="introducir ancho de la barra", default=0.00)
    bar_height_qty = fields.Float('Alto de barra', required=False, readonly=False, copy=False, help="introducir alto de la barra", default=0.00)
    temp_room_qty = fields.Float('Temp C. cuarto frio', required=False, readonly=False, copy=False, help="introducir temperatura de cuarto frio", default=0.00)
    #Confiteria
    terminated_granel = fields.Boolean('Terminado', required=False, readonly=False, copy=False, help="Cumple con el terminado", default=False)
    #seccion de seleccion compartida
    seleccion = fields.Selection([
        ('Grasa', 'Grasa'),
        ('Palsgaar', 'Palsgaar'),
        ('Lecitina de soya', 'Lecitina de soya'),
        ('Mezcla liquida', 'Mezcla liquida'),
        ('Cubierta en polvo', 'Cubierta en polvo'),
        ('Galleta rellena1', 'Galleta rellena'),
        ('Chocolate liquido galleta', 'Chocolate liquido galleta'),
        ('Chocotaza masa', 'Chocotaza masa'),
        ('Jarabe de brillo', 'Jarabe de brillo')], 'Seleccion', required=False, readonly=False, copy=False, help="Seleccione una opcion", default="")
    temp_qty = fields.Float('Temp C.', required=False, readonly=False, copy=False, help="introducir temperatura a medir", default=0.00)
    color_s = fields.Boolean('Color', required=False, readonly=False, copy=False, help="Cumple con el color", default=False)
    sabor_s = fields.Boolean('Sabor', required=False, readonly=False, copy=False, help="Cumple con el sabor", default=False)
    olor_s = fields.Boolean('Olor', required=False, readonly=False, copy=False, help="Cumple con el olor", default=False)
    apariencia_s = fields.Boolean('Apariencia', required=False, readonly=False, copy=False, help="Cumple con el color", default=False)
    textura_s = fields.Boolean('textura', required=False, readonly=False, copy=False, help="Cumple con la textura", default=False)

    employee_id_user = fields.Many2one('hr.employee',string="Monitor",required=True, copy=False, readonly=False)

    @api.depends("production_id")
    def _copy_production_id(self):
        for record in self:
            record['name'] = record.production_id.name
    


QualityControlPoints()