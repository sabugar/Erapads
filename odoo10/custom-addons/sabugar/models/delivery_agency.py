# -*- Coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError

class DeliveryAgency(models.Model):
    _name = 'delivery.agency'
    _description = 'Name of the delivery agency who gives the delivery service.'
    
    name = fields.Char('Delivery Agency', required=True)
    active = fields.Boolean(default=True)