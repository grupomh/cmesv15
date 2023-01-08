# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime

class WizardCancelInvoice(models.TransientModel):
    _name = 'wizard.invoice.cancel'
    _description = "Cancel invoice on batch"

    apply_invisible = fields.Boolean('Ocultar transacciones', default=False)

    def action_batch_cancel(self):
        active_ids = self.env.context.get('active_ids')
        move_obj = self.env['account.move']
        for inv in move_obj.browse(active_ids):
            inv.button_draft()
            inv.button_cancel()
            if self.apply_invisible == True:
                inv.write({'invisible': True})
        return True

WizardCancelInvoice()