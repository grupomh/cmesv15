# -*- coding: utf-8 -*-

import random

import datetime
import uuid

from odoo import fields, models, api
from odoo.exceptions import UserError, Warning

import requests
import json
from xml.dom import minidom
import xml.etree.ElementTree as ET
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
import base64
from odoo.tools.translate import _

import os


class AccountInvoice(models.Model):
    _inherit = 'account.move'
    serie_factura = fields.Char(string="Serie Factura", required=False, help="Serie de la factura de proveedor")
    num_factura = fields.Char(string="Numero Factura", required=False, help="Numero de la factura de proveedor")
AccountInvoice()