# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models,fields,api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def create_recompute_commision(self, analysis_vals,inv):
        sale_commission_analysis = self.env['sale.commission.analysis']
        analysis_vals.update({'date': self.payment_date, 'sales_person_id': self.vendedor_id.id, 'move_id': inv.id})
        sale_commission_analysis.create(analysis_vals)


    def recompute_sale_commission(self):
        if self.payment_difference == 0.0 and self.invoice_ids and self.env.company.commission_based_on_payment:
            for inv in self.invoice_ids:
                if inv.type == 'out_invoice':
                    sale_commission = self.env['sale.commission']
                    analysis_vals = {}
                    related_sale_commissions = sale_commission.search([('user_ids.id','=', self.vendedor_id.id)])
                    if related_sale_commissions:
                        for related_sale_commission in related_sale_commissions:
                            commission_per = 0.0
                            commission_amount = 0.0
                            if related_sale_commission.type == 'standard':
                                if inv.invoice_payment_state == 'paid':
                                    analysis_vals.update({'type':'standard','commission_name':related_sale_commission.id})
                                    commission_per = related_sale_commission.standard_commission_per
                                    if commission_per >0.0:
                                        commission_amount = inv.amount_untaxed * (commission_per/100)
                                        analysis_vals.update({'amount':commission_amount,
                                                            'name':related_sale_commission.type +' * '+ related_sale_commission.name + ' ( '+ str(commission_per) +' % )'})
                                        
                                        self.create_recompute_commision(analysis_vals,inv)
                                        analysis_vals = {}                                    
                            elif related_sale_commission.type == 'partner':
                                analysis_vals.update({'type':'partner','commission_name':related_sale_commission.id})
                                if inv.partner_id and inv.partner_id.affiliated:
                                    commission_per = related_sale_commission.affiliated_commission_per
                                    analysis_vals.update({'partner_type':'Affiliated'})
                                else:
                                    commission_per = related_sale_commission.non_affiliated_commission_per
                                    analysis_vals.update({'partner_type':'Non-Affiliated'})
                                if commission_per >0.0:
                                    commission_amount = inv.amount_total * (commission_per/100)
                                    analysis_vals.update({'amount':commission_amount,
                                                          'partner_id':inv.partner_id.id,
                                                          'name':related_sale_commission.type +' * '+ related_sale_commission.name + ' ( '+ str(commission_per) +' % )'})
                                self.create_recompute_commision(analysis_vals,inv)
                                analysis_vals = {}
                                
                            elif related_sale_commission.type == 'product':
                                if related_sale_commission.product_commission_lines:
                                    for line in related_sale_commission.product_commission_lines:
                                        analysis_vals.update({'type':'product','commission_name':related_sale_commission.id})
                                        if line.with_commission == 'fix':
                                            if line.based_on =='product' and line.product_id and inv.invoice_line_ids.filtered(lambda x:x.product_id==line.product_id):
                                                commission_per = 0.0
                                                commission_amount =0.0
                                                for order_line in inv.invoice_line_ids.filtered(lambda x:x.product_id==line.product_id):
                                                    if order_line.price_unit>0.0:
                                                        product_price_diff = (order_line.price_unit)-(order_line.product_id.standard_price)
                                                            
                                                        if line.target_price < product_price_diff:
                                                            commission_per = line.above_price_commission
                                                            commission_amount += (product_price_diff-line.target_price)*(commission_per/100)
                                                            analysis_vals.update({'amount':commission_amount,
                                                              'product_id':order_line.product_id.id,
                                                              'name':related_sale_commission.name + ' ( '+ str(commission_per) +' % )'
                                                              +' for Product '+ order_line.product_id.name})
                                                            
                                                self.create_recompute_commision(analysis_vals,inv)
                                                analysis_vals = {}
                                            elif line.based_on =='categories' and line.category_id and inv.invoice_line_ids.filtered(lambda x:x.product_id.categ_id==line.category_id):
                                                commission_per = 0.0
                                                commission_amount =0.0
                                                for order_line in inv.invoice_line_ids.filtered(lambda x:x.product_id.categ_id==line.category_id):
                                                    if order_line.price_unit>0.0:
                                                        product_price_diff = (order_line.price_unit)-(order_line.product_id.standard_price)
                                                            
                                                        if line.target_price < product_price_diff:
                                                            commission_per = line.above_price_commission
                                                            commission_amount += (product_price_diff-line.target_price)*(commission_per/100)
                                                            analysis_vals.update({'amount':commission_amount,
                                                                                  'category_id':line.category_id.id,
                                                              'name':related_sale_commission.name + ' ( '+ str(commission_per) +' % )'
                                                              +' for Product '+ order_line.product_id.name})
                                                self.create_recompute_commision(analysis_vals,inv)
                                                analysis_vals = {}
                                        elif line.with_commission == 'margin':
                                            if line.based_on =='product' and line.product_id and inv.invoice_line_ids.filtered(lambda x:x.product_id==line.product_id):
                                                commission_per = 0.0
                                                commission_amount =0.0
                                                for order_line in inv.invoice_line_ids.filtered(lambda x:x.product_id==line.product_id):
                                                    if order_line.price_unit>0.0:
                                                        product_price_diff = (order_line.price_unit)-(order_line.product_id.standard_price)
                                                        if product_price_diff >0.0:
                                                            product_margin = (100*product_price_diff)/(order_line.price_unit)
                                                            
                                                            if product_margin > line.target_margin:
                                                                commission_per = line.above_margin_commission
                                                            else:
                                                                commission_per = line.below_margin_commission
                                                                
                                                    
                                                            if commission_per >0.0:
                                                                commission_amount += product_price_diff*(commission_per/100)
                                                                analysis_vals.update({'amount':commission_amount,
                                                                   'product_id':order_line.product_id.id,
                                                                  'name':related_sale_commission.name + ' ( '+ str(commission_per) +' % )'
                                                                  +' for Product '+ order_line.product_id.name}) 
                                                self.create_recompute_commision(analysis_vals,inv)
                                                analysis_vals = {}
                                            elif line.based_on =='categories' and line.category_id and inv.invoice_line_ids.filtered(lambda x:x.product_id.categ_id==line.category_id):
                                                commission_per = 0.0
                                                commission_amount =0.0
                                                for order_line in inv.invoice_line_ids.filtered(lambda x:x.product_id.categ_id==line.category_id):
                                                    if order_line.price_unit>0.0:
                                                        product_price_diff = (order_line.price_unit)-(order_line.product_id.standard_price)
                                                        if product_price_diff >0.0:
                                                            product_margin = (100*product_price_diff)/(order_line.price_unit)
                                                            
                                                            if product_margin > line.target_margin:
                                                                commission_per = line.above_margin_commission
                                                            else:
                                                                commission_per = line.below_margin_commission
                                                                
                                                    
                                                            if commission_per >0.0:
                                                                commission_amount += product_price_diff*(commission_per/100)
                                                                analysis_vals.update({'amount':commission_amount,
                                                                                      'category_id':line.category_id.id,
                                                                  'name':related_sale_commission.name + ' ( '+ str(commission_per) +' % )'
                                                                  +' for Product '+ order_line.product_id.name})  
                                                self.create_recompute_commision(analysis_vals,inv)
                                                analysis_vals = {}
                                        elif line.with_commission == 'exception':
                                            if inv.invoice_payment_state == 'paid':
                                                if line.based_on =='product' and line.product_id and inv.invoice_line_ids.filtered(lambda x:x.product_id==line.product_id):
                                                    commission_per = 0.0
                                                    commission_amount =0.0
                                                    for order_line in inv.invoice_line_ids.filtered(lambda x:x.product_id==line.product_id):
                                                        if order_line.price_unit>0.0:
                                                            product_price_diff = order_line.price_subtotal
                                                            commission_per = line.exception_commission
                                                                
                                                    
                                                            if commission_per >0.0 and product_price_diff>0.0:
                                                                commission_amount += product_price_diff*(commission_per/100)
                                                                analysis_vals.update({'amount':commission_amount,
                                                                                    'product_id':order_line.product_id.id,
                                                                'name':related_sale_commission.name + ' ( '+ str(commission_per) +' % )'
                                                                +' Producto '+ order_line.product_id.name})  
                                                    self.create_recompute_commision(analysis_vals,inv)
                                                    analysis_vals = {}
                                                elif line.based_on =='categories' and line.category_id and inv.invoice_line_ids.filtered(lambda x:x.product_id.categ_id==line.category_id):
                                                    commission_per = 0.0
                                                    commission_amount =0.0
                                                    for order_line in inv.invoice_line_ids.filtered(lambda x:x.product_id.categ_id==line.category_id):
                                                        if order_line.price_unit>0.0:
                                                            product_price_diff = order_line.price_subtotal
                                                            commission_per = line.exception_commission
                                                    
                                                            if commission_per >0.0 and product_price_diff>0.0:
                                                                commission_amount += product_price_diff*(commission_per/100)
                                                                analysis_vals.update({
                                                                    'amount':commission_amount,
                                                                    'category_id':line.category_id.id,
                                                                    'name': ('Recalculo' + related_sale_commission.name + ' ( ' + str(commission_per) + ' % )' + ' Producto' + order_line.product_id.name),
                                                                    })  
                            
                                                    self.create_recompute_commision(analysis_vals,inv)
                                                    analysis_vals = {}

       
AccountPayment()