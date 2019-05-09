# -*- Coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class DeliveryRoute(models.Model):
    _name = 'delivery.route'
    _description = 'Set delivery route for Ahmedabad only'
    
    name = fields.Char('Route', required=True)
