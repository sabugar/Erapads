
# -*- Coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.osv.expression import get_unaccent_wrapper
from odoo.exceptions import ValidationError, UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    # New mobile field added
    mobile1 = fields.Char("Mobile 1")
    mobile2 = fields.Char("Mobile 2")
    whatsapp = fields.Char("Whatsapp")
    district_name = fields.Char(related="zip_id.district_name")
    customersource_id = fields.Many2one('customer.source', string='Customer Source', required=True)
    zip_id = fields.Many2one('res.better.zip', string='City/Location')
    agency = fields.Boolean(string='Is a Agency',
                            help="Check this box if this contact is a agency.")
    open_delivery = fields.Integer(string='Open Delivery', compute='_compute_open_delivery')
    cancelled_delivery = fields.Integer(string='Cancelled Delivery', compute='_compute_cancelled_delivery')
    done_delivery = fields.Integer(string='Done Delivery', compute='_compute_done_delivery')
    route = fields.Char('Route')
    delivery_agency = fields.Char('Delivery Agency')

    # // Makes the phone numbers unique
    @api.multi
    @api.constrains('phone', 'mobile', 'mobile1', 'mobile2', 'whatsapp')
    def check_phone_numbers(self):
        if self.phone:
            phone = self.env['res.partner'].search([('phone', '=', self.phone),('id', '!=', self.id)])
            phone1 = self.env['res.partner'].search([('mobile', '=', self.phone), ('id', '!=', self.id)])
            phone2 = self.env['res.partner'].search([('mobile1', '=', self.phone), ('id', '!=', self.id)])
            phone3 = self.env['res.partner'].search([('mobile2', '=', self.phone), ('id', '!=', self.id)])
            phone4 = self.env['res.partner'].search([('whatsapp', '=', self.phone), ('id', '!=', self.id)])
            if phone or phone1 or phone2 or phone3 or phone4:
                raise UserError(_('Phone number must be unique!'))

        if self.mobile:
            mobile = self.env['res.partner'].search([('phone', '=', self.mobile),('id', '!=', self.id)])
            mobile1 = self.env['res.partner'].search([('mobile', '=', self.mobile), ('id', '!=', self.id)])
            mobile2 = self.env['res.partner'].search([('mobile1', '=', self.mobile), ('id', '!=', self.id)])
            mobile3 = self.env['res.partner'].search([('mobile2', '=', self.mobile), ('id', '!=', self.id)])
            mobile4 = self.env['res.partner'].search([('whatsapp', '=', self.mobile), ('id', '!=', self.id)])
            if mobile or mobile1 or mobile2 or mobile3 or mobile4:
                raise UserError(_('Mobile number must be unique!'))

        if self.mobile1:
            mobile1 = self.env['res.partner'].search([('phone', '=', self.mobile1),('id', '!=', self.id)])
            mobile11 = self.env['res.partner'].search([('mobile', '=', self.mobile1), ('id', '!=', self.id)])
            mobile12 = self.env['res.partner'].search([('mobile1', '=', self.mobile1), ('id', '!=', self.id)])
            mobile13 = self.env['res.partner'].search([('mobile2', '=', self.mobile1), ('id', '!=', self.id)])
            mobile14 = self.env['res.partner'].search([('whatsapp', '=', self.mobile1), ('id', '!=', self.id)])
            if mobile1 or mobile11 or mobile12 or mobile13 or mobile14:
                raise UserError(_('Mobile1 number must be unique!'))

        if self.mobile2:
            mobile2 = self.env['res.partner'].search([('phone', '=', self.mobile2),('id', '!=', self.id)])
            mobile21 = self.env['res.partner'].search([('mobile', '=', self.mobile2), ('id', '!=', self.id)])
            mobile22 = self.env['res.partner'].search([('mobile1', '=', self.mobile2), ('id', '!=', self.id)])
            mobile23 = self.env['res.partner'].search([('mobile2', '=', self.mobile2), ('id', '!=', self.id)])
            mobile24 = self.env['res.partner'].search([('whatsapp', '=', self.mobile2), ('id', '!=', self.id)])
            if mobile2 or mobile21 or mobile22 or mobile23 or mobile24:
                raise UserError(_('Mobile2 number must be unique!'))

        if self.whatsapp:
            whatsapp = self.env['res.partner'].search([('phone', '=', self.whatsapp), ('id', '!=', self.id)])
            whatsapp1 = self.env['res.partner'].search([('mobile', '=', self.whatsapp), ('id', '!=', self.id)])
            whatsapp2 = self.env['res.partner'].search([('mobile1', '=', self.whatsapp), ('id', '!=', self.id)])
            whatsapp3 = self.env['res.partner'].search([('mobile2', '=', self.whatsapp), ('id', '!=', self.id)])
            whatsapp4 = self.env['res.partner'].search([('whatsapp', '=', self.whatsapp), ('id', '!=', self.id)])
            if whatsapp or whatsapp1 or whatsapp2 or whatsapp3 or whatsapp4:
                raise UserError(_('Whatsapp number must be unique!'))


    @api.one
    def _compute_open_delivery(self):
        for partner in self:
            open_delivery_count = self.env['stock.picking'].search(
                [('partner_id', '=', partner.id), ('state', '=', 'assigned')])
            self.open_delivery = len(open_delivery_count)

    @api.one
    def _compute_cancelled_delivery(self):
        for partner in self:
            cancelled_delivery_count = self.env['stock.picking'].search(
                [('partner_id', '=', partner.id), ('state', '=', 'cancel')])
            self.cancelled_delivery = len(cancelled_delivery_count)

    @api.one
    def _compute_done_delivery(self):
        for partner in self:
            done_delivery_count = self.env['stock.picking'].search(
                [('partner_id', '=', partner.id), ('state', '=', 'done')])
            self.done_delivery = len(done_delivery_count)

    @api.onchange('zip_id')
    def onchange_zip_id(self):
        if self.zip_id:
            self.zip = self.zip_id.name
            self.city = self.zip_id.city
            # self.district_name = self.district_name
            self.state_id = self.zip_id.state_id
            self.country_id = self.zip_id.country_id

    @api.onchange('state_id')
    def onchange_state_id(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id.id

    # Search the name by phone also.
    @api.depends('is_company', 'name', 'parent_id', 'phone', 'mobile')
    def _compute_display_name(self):
        diff = dict(show_address=None, show_address_only=None, show_email=None)
        names = dict(self.with_context(**diff).name_get())
        for partner in self:
            partner.display_name = names.get(partner.id)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        res = super(ResPartner, self).name_search(name, args, operator=operator, limit=limit)
        if args is None:
            args = []
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            self.check_access_rights('read')
            where_query = self._where_calc(args)
            self._apply_ir_rules(where_query, 'read')
            from_clause, where_clause, where_clause_params = where_query.get_sql()
            where_str = where_clause and (" WHERE %s AND " % where_clause) or ' WHERE '

            # search on the name of the contacts and of its company or search by phone also
            search_name = name
            if operator in ('ilike', 'like'):
                search_name = '%%%s%%' % name
            if operator in ('=ilike', '=like'):
                operator = operator[1:]

            unaccent = get_unaccent_wrapper(self.env.cr)

            query = """SELECT id
                         FROM res_partner
                      {where} ({email} {operator} {percent}
                           OR {display_name} {operator} {percent}
                           OR {reference} {operator} {percent})
                           -- don't panic, trust postgres bitmap
                     ORDER BY {display_name} {operator} {percent} desc,
                              {display_name}
                    """.format(where=where_str,
                               operator=operator,
                               email=unaccent('email'),
                               display_name=unaccent('display_name'),
                               reference=unaccent('ref'),
                               percent=unaccent('%s'))

            where_clause_params += [search_name] * 4
            if limit:
                query += ' limit %s'
                where_clause_params.append(limit)
            self.env.cr.execute(query, where_clause_params)
            partner_ids = map(lambda x: x[0], self.env.cr.fetchall())

            if partner_ids:
                return self.browse(partner_ids).name_get()
            if not partner_ids:
                partner_ids = self.search(
                    ['|', ('phone', operator, name), '|', ('mobile', operator, name), '|', ('mobile1', operator, name), '|', ('mobile2', operator, name),
                     ('whatsapp', operator, name)])
                return partner_ids.name_get()
            else:
                return []
        return res


class BetterZip(models.Model):
    '''City/locations completion object'''

    _name = "res.better.zip"
    _description = __doc__
    _order = "name asc"
    _rec_name = "display_name"

    display_name = fields.Char('Name', compute='_get_display_name', store=True)
    name = fields.Char('Pin Code')
    area = fields.Char('Area')
    district_name = fields.Char('District Name')
    city = fields.Char('City', required=True)
    state_id = fields.Many2one('res.country.state', 'State')
    country_id = fields.Many2one('res.country', 'Country')
    latitude = fields.Float()
    longitude = fields.Float()

    @api.constrains('name')
    def _check_name(self):
        if len(self.name) != 6:
            raise ValidationError(_('Error ! Pincode number must be in 6 digit.'))
        elif not (self.name.isdigit()):
            raise ValidationError(_('Error ! Pincode number must be in digit'))

    @api.one
    @api.depends(
        'name',
        'area',
        'city',
        'state_id',
        'country_id',
        'district_name',
    )
    def _get_display_name(self):
        if self.name or self.area or self.city or self.district_name:
            name = [self.area, self.city, self.district_name, self.name]
        if self.state_id:
            name.append(self.state_id.name)
        if self.country_id:
            name.append(self.country_id.name)
        self.display_name = ", ".join(name)

    @api.onchange('state_id')
    def onchange_state_id(self):
        if self.state_id:
            self.country_id = self.state_id.country_id


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.onchange('better_zip_id')
    def on_change_city(self):
        if self.better_zip_id:
            self.zip = self.better_zip_id.name
            self.city = self.better_zip_id.city
            self.district_name = self.district_name
            self.state_id = self.better_zip_id.state_id
            self.country_id = self.better_zip_id.country_id

    better_zip_id = fields.Many2one(
        'res.better.zip',
        string='Location',
        help='Use the city name or the zip code to search the location',
    )

    @api.onchange('state_id')
    def onchange_state_id(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id.id


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    better_zip_ids = fields.One2many('res.better.zip', 'state_id', 'Cities')
    
class CustomerSource(models.Model):
    _name = 'customer.source'
    _description = 'where from customer came'
    
    name = fields.Char('Customer Source')
    