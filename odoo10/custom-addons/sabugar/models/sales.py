
# -*- Coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    customertype_id = fields.Many2one('customer.type', string='Customer Type',help='Customer is new or existing')
    ordersource_id = fields.Many2one('order.source', string='Order Source', help='Where from order came')
    
class CustomerType(models.Model):
    _name = 'customer.type'
    _description = 'Customer Type for Sales Order'
    
    name = fields.Char('Customer Type', required=True)
    
class OrderSource(models.Model):
    _name = 'order.source'
    _description = 'Where from order came'
    
    name = fields.Char('Order Source', required=True)
