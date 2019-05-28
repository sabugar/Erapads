
# -*- Coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    customertype_id = fields.Many2one('customer.type', string='Customer Type',help='Customer is new or existing')
    ordersource_id = fields.Many2one('order.source', string='Order Source', help='Where from order came')
    delivery_agency_id = fields.Many2one('delivery.agency', string='Delivery Agency', required=True)
    route_id = fields.Many2one('delivery.route', string='Delivery Route')

    @api.multi
    def action_confirm(self):
        for order in self:
            order.state = 'sale'
            order.confirmation_date = fields.Datetime.now()
            if self.env.context.get('send_email'):
                self.force_quotation_send()
            order.order_line._action_procurement_create()
            order.partner_id.last_saleorder_date = order.date_order
        if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
            self.action_done()
        return True
            
    
class CustomerType(models.Model):
    _name = 'customer.type'
    _description = 'Customer Type for Sales Order'
    
    name = fields.Char('Customer Type', required=True)
    
class OrderSource(models.Model):
    _name = 'order.source'
    _description = 'Where from order came'
    
    name = fields.Char('Order Source', required=True)
