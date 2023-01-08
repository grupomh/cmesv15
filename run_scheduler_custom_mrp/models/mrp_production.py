# -*- coding: utf-8 -*-

from odoo import api, models, tools,fields,_

import logging
import threading
import time


_logger = logging.getLogger(__name__)

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    _description = 'Run Scheduler Manualli'

    view_button=fields.Boolean(compute="compute_your_method")

    
    def compute_your_method(self):
        for rec in self:
            rec.view_button = False
            if self.env.user.has_group('mrp.group_mrp_manager'):
                rec.view_button = True

    def _procure_calculation_orderpoint2(self):
        with api.Environment.manage():
            # As this function is in a new thread, I need to open a new cursor, because the old one may be closed
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            scheduler_cron = self.sudo().env.ref('stock.ir_cron_scheduler_action')
            # Avoid to run the scheduler multiple times in the same time
            try:
                with tools.mute_logger('odoo.sql_db'):
                    self._cr.execute("SELECT id FROM ir_cron WHERE id = %s FOR UPDATE NOWAIT", (scheduler_cron.id,))
            except Exception:
                _logger.info('Attempt to run procurement scheduler aborted, as already running')
                self._cr.rollback()
                self._cr.close()
                return {}

            for company in self.env.user.company_ids:
                cids = (self.env.user.company_id | self.env.user.company_ids).ids
                self.env['procurement.group'].with_context(allowed_company_ids=cids).run_scheduler(
                    use_new_cursor=self._cr.dbname,
                    company_id=company.id)
            new_cr.close()
            return {}



    def procure_calculation2(self):
        threaded_calculation = threading.Thread(target=self._procure_calculation_orderpoint2, args=())
        threaded_calculation.start() 
        
        time.sleep(15)
        threaded_calculation1 = threading.Thread(target=self._procure_calculation_orderpoint2, args=())
        threaded_calculation1.start() 
        
        time.sleep(15)
        threaded_calculation2 = threading.Thread(target=self._procure_calculation_orderpoint2, args=())
        threaded_calculation2.start() 
        
        time.sleep(10)
        threaded_calculation3 = threading.Thread(target=self._procure_calculation_orderpoint2, args=())
        threaded_calculation3.start() 
        
        time.sleep(10)
        threaded_calculation4 = threading.Thread(target=self._procure_calculation_orderpoint2, args=())
        threaded_calculation4.start() 
        
        time.sleep(15)
        threaded_calculation5 = threading.Thread(target=self._procure_calculation_orderpoint2, args=())
        threaded_calculation5.start() 
        
        time.sleep(15)
        threaded_calculation6 = threading.Thread(target=self._procure_calculation_orderpoint2, args=())
        threaded_calculation6.start() 
        
        return {}