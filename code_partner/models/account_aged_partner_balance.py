# -*- coding: utf-8 -*-

import logging

from odoo import models, api, fields, _

_logger = logging.getLogger( __name__ )

class report_account_aged_partner(models.AbstractModel):
    _inherit = "account.aged.partner"

    @api.model
    def _get_lines(self, options, line_id=None):
        lines = super(report_account_aged_partner, self)._get_lines(options, line_id)
        #_logger.info( lines )
        for line in lines:
            if ( line.get('level') == 2 and line.get('partner_id') ):
                code = self.env['res.partner'].browse( line.get('partner_id') ).code
                line['name'] = '[%s] %s'%(code, line.get('name')) if code else line.get('name')
        return lines