# -*- Coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking.type'

    @api.multi
    def _last_delivery_date_change(self):
        pickings = self.env['stock.picking'].search([('partner_id', '=', self.partner_id.id)], order='date_done desc', limit=1)
        for picking in pickings:
            if picking.last_delivery_date:
                picking.partner_id.last_delivery_date = picking.date_done
                picking.partner_id.write({'last_delivery_date': picking.date_done})
        return 'Sueb Sabugar'
    
