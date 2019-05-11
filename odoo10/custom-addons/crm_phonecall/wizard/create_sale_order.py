# -*- Coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError, UserError
import time
from datetime import datetime

class CreateSaleOrder(models.TransientModel):
    _name = 'create.saleorder'
    _description = 'Create Sales Order from Schedule Call'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    date_order = fields.Datetime(string='Order Date', required=True, copy=False, default=fields.Datetime.now)
    delivery_agency_id = fields.Many2one('delivery.agency', string='Delivery Agency', required=True)

    @api.model
    def default_get(self,  default_fields):
        res = super(CreateSaleOrder, self).default_get(default_fields)
        for phonecall in self.env['crm.phonecall'].browse(self.env.context.get('active_id')):
            if 'partner_id' in default_fields:
                res.update({'partner_id': phonecall.partner_id.id})
                for getpartner in self.env['res.partner'].search([('id', '=', phonecall.partner_id.id)]):
                    res.update({'delivery_agency_id': getpartner.delivery_agency_id.id})
        return res

    @api.multi
    def action_create_sale_order(self):
        self.ensure_one()
        
        return 
