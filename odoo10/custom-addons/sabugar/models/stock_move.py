# -*- Coding: utf-8 -*-

from odoo import fields, api, models

class StockMoves(models.Model):
    _inherit = 'stock.move'
    
    @api.multi
    def action_done(self):
        pickings = self.env['stock.picking'].search([('partner_id', '=', self.partner_id.id)], order='date_done desc', limit=1)
        print type(pickings)
        for picking in pickings:
            print (picking.partner_id.last_delivery_date)
            picking.partner_id.write({'last_delivery_date': fields.Datetime.now()})
        res = super(StockMoves, self).action_done()
        return res
