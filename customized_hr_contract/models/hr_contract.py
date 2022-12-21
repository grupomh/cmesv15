# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo import api, fields, models, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class Contract(models.Model):
    _inherit= "hr.contract"

    parking = fields.Monetary('Parqueo', required=False, copy=False, tracking=True, help="Descuento relacionado a estacionamiento o parqueo")
    rent = fields.Monetary('Renta', required=False, copy=False, tracking=True, help="Descuento relacionado a Renta o alquileres")
    insured = fields.Monetary('Seguro', required=False, copy=False, tracking=True, help="Descuento relacionado a Seguros")
    telephony = fields.Monetary('Telefono', required=False, copy=False, tracking=True, help="Descuento relacionado a telefonia")
    other_wage = fields.Monetary('Otros salarios',required=False, copy=False, tracking=True, help="Otros salarios aplicados")
    other_desc = fields.Monetary('Otros descuentos', required=False, copy=False, tracking=True,help="Otros tipo de descuentos que se deseen aplicar")

    date_parking_end = fields.Date('Expiracion parqueo', required=False, tracking=True, help="Fecha de expiracion de descuento")
    date_rent_end = fields.Date('Expiracion renta', required=False, tracking=True, help="Fecha de expiracion de descuento")
    date_insured_end = fields.Date('Expiracion seguro', required=False, tracking=True, help="Fecha de expiracion de descuento")
    date_telephony_end = fields.Date('Expiracion telefono', required=False, tracking=True, help="Fecha de expiracion de descuento")
    date_other_desc_end = fields.Date('Expiracion otros desc.', required=False, tracking=True, help="Fecha de expiracion de otros descuentos")

    comment_desc = fields.Text('Comentarios', required=False, tracking=True, help="Comentarios para los distintos tipos de descuentos")


    @api.model
    def automata_desc_contrac(self):
        self.search([
            ('date_parking_end', '<=', fields.Date.to_string(date.today() + relativedelta(days=0))),
        ]).write({
            'parking': '0.0'
        })

        self.search([
            ('date_rent_end', '<=', fields.Date.to_string(date.today() + relativedelta(days=0))),
        ]).write({
            'rent': '0.0'
        })

        self.search([
            ('date_insured_end', '<=', fields.Date.to_string(date.today() + relativedelta(days=0))),
        ]).write({
            'insured': '0.0'
        })

        self.search([
            ('date_telephony_end', '<=', fields.Date.to_string(date.today() + relativedelta(days=0))),
        ]).write({
            'telephony': '0.0'
        })

        self.search([
            ('date_other_desc_end', '<=', fields.Date.to_string(date.today() + relativedelta(days=0))),
        ]).write({
            'other_desc': '0.0'
        })

        

Contract()