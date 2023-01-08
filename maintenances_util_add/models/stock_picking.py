# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class StockPicking(models.Model):
    _inherit= "stock.picking"

    maintenance_equipment_id=fields.Many2one('maintenance.equipment', 'Equipo de mantenimiento', required=False, copy=False, readonly=True)
    maintenance_request_id=fields.Many2one('maintenance.request', 'Peticion de mantenimiento',  required=False, copy=False, readonly=True)
    
    @api.onchange('maintenance_equipment_id') # ESTA FUNCION ES PARA QUE MUESTRE UN LISTADO DESDE EL TREE DE OTRO MODULO
    def _onchange_equipment_products(self):
        if self.maintenance_equipment_id and self.maintenance_equipment_id.bom_lines:
            items_res = []
            if self.maintenance_request_id and self.maintenance_request_id.prev_cosul == 'mayor' and self.maintenance_request_id.maintenance_type == 'preventive':
                for bline in self.maintenance_equipment_id.bom_lines.filtered(lambda x: x.maintenance_mayor == True):
                    item = {
                        'product_id': bline.product_id.id or False,
                        'name': bline.details or '',
                        'description_picking': bline.details or '', #cambio a aplicar aun falta en los otros campos
                        'product_uom_qty': bline.product_qty or 0.00,
                        'product_uom': bline.product_uom_id.id or False,
                    }
                    items_res.append((0, 0, item))
            elif self.maintenance_request_id and self.maintenance_request_id.prev_cosul == 'menor' and self.maintenance_request_id.maintenance_type == 'preventive':
                for bline in self.maintenance_equipment_id.bom_lines.filtered(lambda x: x.maintenance_menor == True):
                    item = {
                        'product_id': bline.product_id.id or False,
                        'name': bline.details or '',
                        'description_picking': bline.details or '', 
                        'product_uom_qty': bline.product_qty or 0.00,
                        'product_uom': bline.product_uom_id.id or False,
                    }
                    items_res.append((0, 0, item))
            elif self.maintenance_request_id and self.maintenance_request_id.maintenance_type == 'corrective':
                for bline in self.maintenance_equipment_id.bom_lines.filtered(lambda x: x.maintenance_ct == True):
                    item = {
                        'product_id': bline.product_id.id or False,
                        'name': bline.details or '',
                        'description_picking': bline.details or '', 
                        'product_uom_qty': bline.product_qty or 0.00,
                        'product_uom': bline.product_uom_id.id or False,
                    }
                    items_res.append((0, 0, item))
            elif self.maintenance_request_id and self.maintenance_request_id.maintenance_type == 'predictive':# ACA MUESTRA EL LISTADO COMPLETO PORQUE EL TREE NO ESPECIFICA SI HAY UNA SECCION PARA ESTE
                for bline in self.maintenance_equipment_id.bom_lines:
                    item = {
                        'product_id': bline.product_id.id or False,
                        'name': bline.details or '',
                        'description_picking': bline.details or '', 
                        'product_uom_qty': bline.product_qty or 0.00,
                        'product_uom': bline.product_uom_id.id or False,
                    }
                    items_res.append((0, 0, item))
            
            self.update({
                'move_ids_without_package': items_res,
            })
    
StockPicking()