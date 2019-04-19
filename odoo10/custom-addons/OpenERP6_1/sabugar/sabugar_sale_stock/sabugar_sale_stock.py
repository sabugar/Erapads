# -*- coding: utf-8 -*-

from osv import fields, osv
from tools.translate import _

class sale_shop(osv.osv):
    _inherit = "sale.shop"

    _columns = {
        'agencies_id' : fields.many2one('res.partner', 'Agency Name'),
    }

sale_shop()

class call_center(osv.osv):
    _name = "call.center"

    _columns = {
        'name': fields.char('Name', required=True, size=256, select=1),
        'code': fields.char('Code', size=256, select=1)
    }

call_center()

class sale_order(osv.osv):
    _inherit = "sale.order"

    _columns = {
        'delivery_id' : fields.many2one("res.users", 'Delivery User', readonly=True, states={'draft': [('readonly', False)]}),
        'call_center_id' : fields.many2one('call.center', 'Call Center', readonly=True, states={'draft': [('readonly', False)]}),
    }

    def action_ship_create(self, cr, uid, ids, context=None):
        picking_obj = self.pool.get('stock.picking')
        super(sale_order, self).action_ship_create(cr, uid, ids, context=context)
        for order in self.browse(cr, uid, ids, context=context):
            picking_ids= [picking.id for picking in order.picking_ids]
            picking_obj.write(cr, uid, picking_ids, {'delivery_id' : order.delivery_id and order.delivery_id.id or False, 'call_center_id': order.call_center_id and order.call_center_id.id or False,'landmark': order.landmark or False,'city_id': order.city_id and order.city_id.id or False,'area_id': order.area_id and order.area_id.id or False,'shop_id': order.shop_id and order.shop_id.id or False,'rm':order.remark_so or False }, context)
        return True

sale_order()

class stock_picking(osv.osv):
    _inherit = "stock.picking"

    _columns = {
        'delivery_id' : fields.many2one("res.users", 'Delivery User', readonly=True, states={'draft': [('readonly', False)]}),
        'call_center_id' : fields.many2one('call.center', 'Call Center', readonly=True, states={'draft': [('readonly', False)]}),
    }

    def action_done(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        super(stock_picking, self).action_done(cr, uid, ids, context=context)
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        journal_obj = self.pool.get('account.journal')
        period_obj = self.pool.get("account.period")
        for picking in self.browse(cr, uid, ids, context=context):
            if picking.sale_id and picking.type == "out":
                journal_ids = journal_obj.search(cr, uid, [('type', '=','sale'),('company_id', '=', picking.company_id and picking.company_id.id or False)], limit=1)
                if not journal_ids:
                    raise osv.except_osv(_('Configuration Error !'), _('Sale type journal not created. '))

                if not picking.sale_id.shop_id.agencies_id:
                    raise osv.except_osv(_('Configuration Error !'), _('Agnecy Name not define in %s shop.') % picking.sale_id.shop_id.name)
                period_ids = period_obj.find(cr, uid, picking.date)
                if not period_ids:
                    raise osv.except_osv(_('Configuration Error !'), _('Period not define for %s date ! ') % picking.date)
                vals = {
                    'journal_id': journal_ids[0],
                    'date': picking.date,
                    'period_id': period_ids[0],
                    'ref': picking.sale_id and picking.sale_id.menifest_id and picking.sale_id.menifest_id.name + ':'+ picking.origin,
                    'company_id' : picking.company_id.id
                }
                move_id = move_obj.create(cr, uid, vals, context)

                move_line = {
                    'journal_id': journal_ids[0],
                    'period_id': period_ids[0],
                    'ref': picking.sale_id and picking.sale_id.menifest_id and picking.sale_id.menifest_id.name + ':'+ picking.origin,
                    'name': '/',
                    'account_id': picking.sale_id.shop_id.agencies_id.property_account_receivable.id,
                    'move_id': move_id,
                    'partner_id': picking.sale_id.shop_id.agencies_id.id,
                    'quantity': 1,
                    'date': picking.date
                }
                total = 0.0
                for move in picking.move_lines:
                    if move.state == 'cancel':
                        continue
                    account_id = move.product_id.product_tmpl_id.property_account_income.id
                    if not account_id:
                        account_id = move.product_id.categ_id.property_account_income_categ.id
                    move_line.update({
                        'name': move.product_id and move.product_id.name or '/',
                        'account_id': account_id,
                        'quantity': move.product_qty,
                        'debit': 0.0,
                        'credit': move.sale_line_id.price_subtotal,
                    })
                    total += move.sale_line_id and move.sale_line_id.price_subtotal or 0
                    move_line_obj.create(cr, uid, move_line, context)

                move_line.update({
                    'name': '/',
                    'account_id': picking.sale_id.shop_id.agencies_id.property_account_receivable.id,
                    'quantity': 1,
                    'debit': total,
                    'credit': 0.0,
                    'date': picking.date
                })
                move_line_obj.create(cr, uid, move_line, context)
                move_obj.post(cr, uid, [move_id], context=context)

        return True

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial pickings and moves done.
        @param partial_datas: Dictionary containing details of partial picking
                          like partner_id, address_id, delivery_date, delivery
                          moves with product_id, product_qty, uom
        """
        result = super(stock_picking, self).do_partial(cr, uid, ids, partial_datas, context)
        picking_ids = []
        product_ids = []
        move_obj = self.pool.get('stock.move')
        for picking in self.browse(cr, uid, ids, context):
            if picking.type == 'in':
                product_ids.extend([move.product_id.id for move in picking.move_lines])
        if product_ids:
            move_ids = move_obj.search(cr, uid, [('product_id' ,'in', product_ids), ('state' ,'=', 'confirmed')], context=context)
            for move in move_obj.browse(cr, uid, move_ids, context):
                if move.picking_id and move.picking_id.id not in picking_ids:
                    picking_ids.append(move.picking_id.id)
        if picking_ids: 
            self.action_assign(cr, uid, picking_ids, context)
        return result
    
    def write(self, cr, uid, ids, vals, context=None):
        sale_vals = {}
        move_line_vals = {}
        sale_line_vals = {}
        for pick in self.browse(cr, uid, ids, context=context):
            if pick.sale_id:
                if 'date' in vals:
                    sale_vals.update(date_order=vals['date'])
                if 'address_id' in vals:
                    sale_vals.update(partner_shipping_id=vals['address_id'])
                if 'landmark' in vals:
                    sale_vals.update(landmark=vals['landmark'])
                if 'area_id' in vals:
                    sale_vals.update(area_id=vals['area_id'])
                if 'city_id' in vals:
                    sale_vals.update(city_id=vals['city_id'])
                if 'shop_id' in vals:
                    sale_vals.update(shop_id=vals['shop_id'])
                if 'salesman_name' in vals:
                    sale_vals.update(salesman_name=vals['salesman_name'])
                if 'delivery_id' in vals:
                    sale_vals.update(delivery_id=vals['delivery_id'])
                if 'group_id' in vals:
                    sale_vals.update(group_id=vals['group_id'])
                if 'move_lines' in vals:
                    data = vals['move_lines']
                    for line in data:
                        if line[0] == 1:
                            move_id = line[1]
                            stock_move = self.pool.get('stock.move').browse(cr, uid, move_id)
                            move_line_vals = line[2]
                            if 'product_qty' in move_line_vals:
                                sale_line_vals.update(product_uom_qty=move_line_vals['product_qty'])
                            if 'product_uom' in move_line_vals:
                                sale_line_vals.update(product_uom=move_line_vals['product_uom'])
                            if 'product_id' in move_line_vals:
                                sale_line_vals.update(product_id=move_line_vals['product_id'])
                            if stock_move.sale_line_id:
                                self.pool.get('sale.order.line').write(cr, uid, [stock_move.sale_line_id.id], sale_line_vals)
                        if line[0] == 0:
                            move_id = line[1]
                            stock_move = self.pool.get('stock.move').browse(cr, uid, move_id)
                            move_line_vals = line[2]
                            price = self.pool.get('product.product').browse(cr, uid, move_line_vals['product_id']).list_price
                            sale_line_vals = {'price_unit': price, 'order_id':pick.sale_id.id, 'product_id':move_line_vals['product_id'], 'product_uom_qty':move_line_vals['product_qty'] ,'product_uom':move_line_vals['product_uom'], 'name':move_line_vals['name']}
                            self.pool.get('sale.order.line').create(cr, uid, sale_line_vals)
                self.pool.get('sale.order').write(cr, uid, [pick.sale_id.id], sale_vals)
        return super(stock_picking, self).write(cr, uid, ids, vals, context=context)

stock_picking()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
