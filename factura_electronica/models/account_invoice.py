# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from suds.client import Client
from odoo.addons.factura_electronica.models.numero_a_texto import Numero_a_Texto
#from odoo.addons.factura_electronica.models.ws import ws_eface
from suds.client import Client
#from suds.xsd.doctor import Import, ImportDoctor
from datetime import datetime
import xml.etree.cElementTree as ET
from lxml import etree
import glob
import os
import base64
#import sys
#reload(sys)  
#sys.setdefaultencoding('utf8')

#Variables del XML
xmlns = "http://www.fact.com.mx/schema/gt"
xsi = "http://www.w3.org/2001/XMLSchema-instance"
schemaLocation = "http://www.fact.com.mx/schema/gt http://www.mysuitemex.com/fact/schema/fx_2013_gt_3.xsd"
version = "1.1"
ns = "{xsi}"


class AccountMove(models.Model):
	_inherit = "account.move"
	
	consumido_eface = fields.Boolean('Consumido', required=False, readonly=True, help="Parametro para indentificar el consumo en el WS")
	id_sat = fields.Char("Id SAT", readonly=True, required=False, help="Identificador asignado en el consumo de la factura en el WS")
	id_serie_sat = fields.Char("Id Serie SAT", readonly=True, required=False, help="Identificador de la serie de la factura electronica")
	cae = fields.Text("CAE", readonly=True, required=False, help="Firma electronica")
	serie = fields.Char("Serie", readonly=True, required=False, help="Serie del documento")
	no_documento = fields.Char("No Documento", readonly=True, required=False, help="Numero del documento")
	txt_filename = fields.Char('Archivo', required=False, readonly=True)
	file = fields.Binary('Archivo', required=False, readonly=True)
	notas = fields.Text("Notas", readonly=False, required=False, help="Notas")
	is_eface = fields.Boolean('EFACE', related="journal_id.is_eface")
	
	
	def action_post(self):
		self.action_eface()
		res = super(AccountMove, self).action_post()
		if self.serie:
			self.write({'name': self.serie})
			#self.action_download_eface()
		return res
	
	def action_eface(self):
		xml = ""
		for invoice in self:
			if (invoice.journal_id.is_eface == True) and (invoice.journal_id.type == 'sale'):
				try:
					#ws = ws_eface(str(invoice.journal_id.sequence_id.url_ws))
					RetPDF = 1
					pdf_file = False
					url = invoice.journal_id.sequence_id.url_ws
					codcliente = invoice.journal_id.sequence_id.cod_cliente
					codusuario = invoice.journal_id.sequence_id.user_eface
					nitemisor = invoice.journal_id.sequence_id.llave_eface
					resoluciono = invoice.journal_id.sequence_id.resolucion
					establecimiento = invoice.journal_id.sequence_id.establecimiento
					doc = invoice.journal_id.sequence_id.tipo
					xml = self.create_xml()
					##raise UserError(('%s')%(xml))
					ws = Client(url)
					response = ws.service.Execute(codcliente, codusuario, nitemisor, establecimiento, resoluciono, xml, RetPDF)
					#raise UserError(('%s')%(response))
					if response:
						if response.Respuesta:
							tree_res = ET.fromstring(response.Respuesta)
							resulta_codigo = tree_res.find('ERROR').attrib['Codigo']
							resulta_descripcion = tree_res.find('ERROR').text
							if not (resulta_codigo=="0"):
								raise UserError(_("No se Puede validad la Factura Electronica\n Error Code:%s\n %s."% (resulta_codigo,response.Respuesta)))
							if response.Dte:
								tree_dte = ET.fromstring(response.Dte)
								mitree = tree_dte.attrib
								#raise UserError(('%s')%(response.Dte))
								NoDocto = mitree['NoDocto']
								NombreDTE = mitree['NombreDTE']
								Fecha =mitree['Fecha']
								uno = response.Dte
								ab = uno.find('Archivo="')
								bc = uno.find('"/>')
								ab = ab+9
								tres= uno[ab:bc]
								res = base64.standard_b64decode(tres)
								res = res.decode(encoding='utf-8', errors='strict')
								ini = res.find("<ds:SignatureValue>")
								fin = res.find("</ds:SignatureValue>")
								ini = ini+19
								Cae = res[ini:fin]
								for child in tree_dte:
									if child.attrib['Tipo'] == 'PDF':
										pdf_file = child.attrib['Archivo']
								self.write({
									'cae': Cae,
									'consumido_eface': True,
									'serie': NombreDTE,
									'no_documento': NoDocto,
									'txt_filename': '%s.pdf' %(NombreDTE),
									'file': base64.encodestring(base64.standard_b64decode(pdf_file)),
								})
						else:
							raise UserError(('%s')%(res.Respuesta))
				except Exception as e:
					raise UserError(('Error al genera Factura Electronica: %s')%(e))

	def get_delivery_address_old(self, partner_id=False):
		partner_obj = self.env['res.partner']
		address = ""
		sep = ","
		if partner_id:
			delivery = partner_obj.search([('id', '=', partner_id)], limit=1)
			if delivery.street:
				address += delivery.street + sep
			if delivery.street2:
				address += delivery.street2 + sep
			if delivery.city:
				address += delivery.city + sep
			if delivery.state_id:
				address += delivery.state_id.name + sep
			if delivery.country_id:
				address += delivery.country_id.name
		return address
		
	def create_xml(self):
		#print ("self invoice", self.number)
		# year = datetime.strptime(self.date_invoice, "%Y-%m-%d").strftime('%Y')
		numero = str(self.name).split('-')
		#serie = self.invoice_sequence_number_next_prefix
		#numero = self.invoice_sequence_number_next
		lote = 0
		root = ET.Element("stdTWS", xmlns="GFACE_Web")
		doc = ET.SubElement(root, "stdTWS.stdTWSCIt")
		#ET.SubElement(doc, "TrnLotNum").text = lote
		ET.SubElement(doc, "TipTrnCod").text = self.journal_id.sequence_id.tipo
		#ET.SubElement(doc, "TrnNum").text = str(self.journal_id.sequence_id.number_next_actual - 1)
		ET.SubElement(doc, "TrnNum").text = str(self.journal_id.sequence_number_next)
		ET.SubElement(doc, "TrnFec").text = str(self.invoice_date) or str(fields.date.now())
		ET.SubElement(doc, "TrnBenConNIT").text = self.partner_id.vat
		if self.partner_id.country_id.id != self.company_id.country_id.id:
			ET.SubElement(doc, "TrnEFACECliCod").text = "EXPO"
			ET.SubElement(doc, "TrnEFACECliNom").text = self.partner_id.name
			ET.SubElement(doc, "TrnEFACECliDir").text = self.partner_id.street
		elif not self.partner_id.vat:  # ( not NIT)
			ET.SubElement(doc, "TrnEFACECliCod").text = "CF"
			ET.SubElement(doc, "TrnEFACECliNom").text = self.partner_id.name
			ET.SubElement(doc, "TrnEFACECliDir").text = "Ciudad"
		else:
			ET.SubElement(doc, "TrnEFACECliCod").text = ""
			ET.SubElement(doc, "TrnEFACECliNom").text = ""
			ET.SubElement(doc, "TrnEFACECliDir").text = ""
		partner_address = self.partner_id.address_get(['delivery', 'invoice'])
		delivery_address = self.get_delivery_address(partner_id=partner_address['delivery'])
		ET.SubElement(doc, "TrnObs").text = str(delivery_address) or ""
		ET.SubElement(doc, "TrnEMail").text = self.partner_id.email
		#Nota de credito
		if self.type == 'out_refund':
			inv_num = self.reversed_entry_id.name.split('_')
			ET.SubElement(doc, "TDFEPAutResNum").text = str(self.reversed_entry_id.journal_id.sequence_id.resolucion)
			ET.SubElement(doc, "TDFEPTipTrnCod").text = str(self.reversed_entry_id.journal_id.sequence_id.tipo)
			ET.SubElement(doc, "TDFEPSerie").text = str(inv_num[2])
			ET.SubElement(doc, "TDFEPDispElec").text = str(self.reversed_entry_id.journal_id.sequence_id.dispositivo)
			ET.SubElement(doc, "TDFEPYear").text = str(self.reversed_entry_id.invoice_date.year)
			ET.SubElement(doc, "TDFEPNum").text = str(self.reversed_entry_id.no_documento)
		else:
			ET.SubElement(doc, "TDFEPAutResNum").text = ""		
			ET.SubElement(doc, "TDFEPTipTrnCod").text = ""
			ET.SubElement(doc, "TDFEPSerie").text = ""
			ET.SubElement(doc, "TDFEPDispElec").text = ""
			ET.SubElement(doc, "TDFEPYear").text = "0"
			ET.SubElement(doc, "TDFEPNum").text = "0"
		#Fin Nota de credito
		rate = (1 / self.currency_id.rate if self.currency_id.rate else 1.00)
		ET.SubElement(doc, "MonCod").text = self.currency_id.name
		ET.SubElement(doc, "TrnTasCam").text = str(round(rate, 2))
		ET.SubElement(doc, "TrnCampAd01").text = self.partner_id.code or ""
		ET.SubElement(doc, "TrnCampAd02").text = self.partner_id.name or ""
		ET.SubElement(doc, "TrnCampAd03").text = self.invoice_payment_term_id.name or ""
		ET.SubElement(doc, "TrnCampAd04").text = ""
		ET.SubElement(doc, "TrnCampAd05").text = ""
		ET.SubElement(doc, "TrnCampAd06").text = ""
		ET.SubElement(doc, "TrnCampAd07").text = ""
		ET.SubElement(doc, "TrnCampAd08").text = ""
		ET.SubElement(doc, "TrnCampAd09").text = ""
		ET.SubElement(doc, "TrnCampAd10").text = ""
		ET.SubElement(doc, "TrnCampAd11").text = ""
		ET.SubElement(doc, "TrnCampAd12").text = ""
		ET.SubElement(doc, "TrnCampAd13").text = ""
		ET.SubElement(doc, "TrnCampAd14").text = ""
		ET.SubElement(doc, "TrnCampAd15").text = ""
		ET.SubElement(doc, "TrnCampAd16").text = ""
		ET.SubElement(doc, "TrnCampAd17").text = ""
		ET.SubElement(doc, "TrnCampAd18").text = ""
		ET.SubElement(doc, "TrnCampAd19").text = ""
		ET.SubElement(doc, "TrnCampAd20").text = ""
		ET.SubElement(doc, "TrnCampAd21").text = ""
		ET.SubElement(doc, "TrnCampAd22").text = ""
		ET.SubElement(doc, "TrnCampAd23").text = ""
		ET.SubElement(doc, "TrnCampAd24").text = ""
		ET.SubElement(doc, "TrnCampAd25").text = ""
		ET.SubElement(doc, "TrnCampAd26").text = ""
		ET.SubElement(doc, "TrnCampAd27").text = ""
		ET.SubElement(doc, "TrnCampAd28").text = ""
		ET.SubElement(doc, "TrnCampAd29").text = ""
		ET.SubElement(doc, "TrnCampAd30").text = ""
		ET.SubElement(doc, "TrnPaisCod").text = self.partner_id.country_id.code and self.partner_id.country_id.code.upper() or ''
		invoice_line = self.invoice_line_ids
		ET.SubElement(doc, "TrnUltLinD").text = str(len(invoice_line.ids))
		line_doc = ET.SubElement(doc, "stdTWSD")
		print (">>>>>>>>", len(invoice_line.ids))
		tax_in_ex = 1
		cnt = 0
		for line in invoice_line:
			cnt += 1
			p_type = 0
			desc=0
			if line.product_id.type == 'service':
				p_type = 1
			if line.discount > 0:
				desc= ((line.quantity * line.price_unit) * line.discount) / 100.00
			for tax in line.tax_ids:
				if tax.price_include:
					tax_in_ex = 0
			# product tag -- <stdTWS.stdTWSCIt.stdTWSDIt>
			product_doc = ET.SubElement(line_doc, "stdTWS.stdTWSCIt.stdTWSDIt")
			ET.SubElement(product_doc, "TrnLiNum").text = str(cnt)
			ET.SubElement(product_doc, "TrnArtCod").text = line.product_id.default_code or "0"
			ET.SubElement(product_doc, "TrnArtNom").text = line.name or " "
			ET.SubElement(product_doc, "TrnCan").text = str(line.quantity)
			ET.SubElement(product_doc, "TrnVUn").text = str(line.price_unit)
			ET.SubElement(product_doc, "TrnUniMed").text = line.product_uom_id.name or " "
			ET.SubElement(product_doc, "TrnVDes").text = str(desc) or "0"
			ET.SubElement(product_doc, "TrnArtBienSer").text = str(p_type)
			ET.SubElement(product_doc, "TrnArtExcento").text = str(tax_in_ex)
			ET.SubElement(product_doc, "TrnDetCampAd01").text = ""
			ET.SubElement(product_doc, "TrnDetCampAd02").text = ""
			ET.SubElement(product_doc, "TrnDetCampAd03").text = ""
			ET.SubElement(product_doc, "TrnDetCampAd04").text = ""
			ET.SubElement(product_doc, "TrnDetCampAd05").text = ""
		tax_doc = ET.SubElement(doc, "stdTWSIA")
		#sub_tax_doc = ET.SubElement(tax_doc, "stdTWS.stdTWSCIt.stdTWSIAIt")
		#ET.SubElement(sub_tax_doc, "TrnImpCod").text = ""
		#ET.SubElement(sub_tax_doc, "TrnImpValor").text = ""
		final_data = ET.tostring(root,encoding='UTF-8',  method='xml')
		declare_str = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
		f_str = "%s %s" % (declare_str, final_data.decode("utf-8"))
		# print (f_str)
		return f_str


	def button_cancel(self):
		res = super(AccountMove, self).button_cancel()
		self.action_cancel_eface()
		return res
	
	def action_cancel_eface(self):
		url = ""
		#url = "https://gface.ecofactura.com.gt/gface/servlet/ar_anu_fac?wsdl"
		for invoice in self:
			#if not invoice.journal_id.sequence_id.url_ws_anulacion:
			#	raise UserError(('Debe configurar un URL para anular documentos'))
			url = invoice.journal_id.sequence_id.url_ws_anulacion
			if invoice.state != 'draft':
				if (invoice.journal_id.is_eface == True) and (invoice.journal_id.type == 'sale'):
					if not invoice.journal_id.sequence_id.url_ws_anulacion:
						raise UserError(('Debe configurar un URL para anular documentos'))
					try:
						codcliente = invoice.journal_id.sequence_id.cod_cliente
						codusuario = invoice.journal_id.sequence_id.user_eface
						nitemisor = invoice.journal_id.sequence_id.llave_eface
						resolucion = invoice.journal_id.sequence_id.resolucion
						establecimiento = invoice.journal_id.sequence_id.establecimiento
						doc = invoice.journal_id.sequence_id.tipo
						dispositivo = invoice.journal_id.sequence_id.dispositivo
						no_eface = invoice.serie.split('_')
						ws = Client(url)
						response = ws.service.Execute(codcliente, codusuario, nitemisor, establecimiento, resolucion, doc, no_eface[2], dispositivo, datetime.strptime(str(invoice.invoice_date), '%Y-%m-%d').year, invoice.no_documento)
						#raise except_orm(_('Error!'),_("%s." % (response)))
						if response:
							#raise except_orm(_('Error!'),_("%s." % (response)))
							print(response)
							invoice.write({'notas': response})
							return True
					except Exception as e:
						raise UserError(('Error al genera Factura Electronica: %s')%(e))

	def action_download_eface(self):
		#order_id = self.env['pos.order'].search([('id', '=', int(order['order_id']))])
		return {
			'type': 'ir.actions.act_url',
			'name': 'Factura' + self.txt_filename,
			'url':"web/content/?model=" + "account.move" +"&id=" + str(self.id) + "&filename_field=file_name&field=file&download=true&filename=" + self.txt_filename,
			'target': 'self',
		}

AccountMove()
