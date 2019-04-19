# -*- coding: utf-8 -*-

from osv import osv
from osv import fields
import base64
import tempfile
import csv
import datetime
from tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT

class import_csv(osv.osv_memory):
    _name = 'import.csv'
    _columns = {
        "file_1": fields.binary("File Name", required=True),
    }

    def action_ok(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        partner_obj = self.pool.get('res.partner')
        lead_obj = self.pool.get('crm.lead')
        address_obj = self.pool.get('res.partner.address')
        city_obj = self.pool.get('sabugar.city')
        area_obj = self.pool.get('sabugar.city.area')
        log_false = []
        summary = ""
        for imp_csv in self.browse(cr, uid, ids, context):
            file_1 = base64.decodestring(imp_csv.file_1)
            (fileno, fp_name) = tempfile.mkstemp('.csv', 'openerp_')
            file = open(fp_name, "w")
            file.write(file_1)
            file.close()
            file = open(fp_name, "r")
            reader = csv.DictReader(file)
            for row in reader:
                print row
                if row.get('phone1',False) or row.get('phone2',False) or row.get('mobile1',False) or row.get('mobile2',False):
                    partner_id = self.create_partner(cr, uid, row, context=context)
                    self.create_opportunities(cr, uid, partner_id, row, context)
        return {}

    def create_opportunities(self, cr, uid, partner_id, row, context=None):
        lead_obj = self.pool.get('crm.lead')
        partner_obj = self.pool.get('res.partner')
        partner_data = partner_obj.browse(cr, uid, partner_id, context)
        
        date_action = False
        if row.get('conf_date', False):
            try:
                date_action = datetime.datetime.strptime(row.get('conf_date'), '%d/%m/%Y') 
                date_action = date_action.strftime(DEFAULT_SERVER_DATE_FORMAT)
            except:
                date_action = False
        date_create = False
        if row.get('call_date', False):
            try:
                date_create = datetime.datetime.strptime(row.get('call_date'), '%d/%m/%Y') 
                date_create = date_create.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            except:
                date_create = False                
        date_deadline = False
        if row.get('del_date', False):
            try:
                date_deadline = datetime.datetime.strptime(row.get('del_date'), '%d/%m/%Y') 
                date_deadline = date_deadline.strftime(DEFAULT_SERVER_DATE_FORMAT)
            except:
                date_deadline = False
        stage = row.get('status',False)
        if stage=='DELIVERED':
            stage_id=6
        else:
            stage_id=1
            
        user_id = self.create_user(cr, uid, row, context=context)
        agency_id = self.create_partner(cr, uid, row, agency=True, context=context)
        opportunity_type = row.get('Type',False)
        if opportunity_type == 'EXISTING':
            otype=1
        else:
            otype=2
        
        vals = {
            'type':'opportunity',
            'name': row.get('cust_name', 'Abc'),
            'partner_id': partner_id,
            'partner_address_id': partner_data.address and partner_data.address[0].id or False,
            'phone': row.get('phone1'),
            'partner_name' : row.get('cust_name','Abc'),
            'phone': row.get('phone'),
            'mobile': row.get('mobile1'),
            'phone2': row.get('phone2'),
            'mobile2': row.get('mobile2'),            
            'street': row.get('Address'),
            'street2': row.get('Landmark'),
            'date_action': date_action,
            'description': row.get('Remark'),
            'planned_revenue': row.get('del_rs'),
            'date_deadline': date_deadline,
            'date_closed': date_deadline,
            'stage_id': stage_id,
            'user_id': user_id,
            'call_center_id':agency_id,
            'opportunity_type':otype,
#            'state':'pending',
            'city_id': partner_data.address and partner_data.address[0].city_id.id,
            'area_id': partner_data.address and partner_data.address[0].area_id.id,
        }
        lead_id = lead_obj.create(cr, uid, vals, context)
        if date_create:
            cr.execute("update crm_lead set create_date='%s' where id=%d"%(date_create,lead_id))

    def create_partner(self, cr, uid, row, agency=False, context=None):
        partner_obj = self.pool.get('res.partner')
        if agency:
            partner_ids = partner_obj.search(cr, uid, [('name', '=', row.get('cust_name','Abc'))])
        else:
            partner_ids = partner_obj.search(cr, uid, [('name', '=', row.get('cust_name','Abc')),('phone', '=', row.get('phone1'))])
        if partner_ids:
            return partner_ids[0]
        area_id,city_id = self.create_area(cr, uid, row, context)
        
        if agency:
            vals = {
            'name' : row.get('branchname', 'Abc'),
            'is_customer':False
            }
        else:
            vals = {
                'name' : agency and row.get('branchname', 'Abc') or row.get('cust_name', 'Abc'),
                'address' : [(0, 0, {'name' : agency and row.get('branchname', 'Abc') or row.get('cust_name', 'Abc'),
                                     'phone': row.get('phone1'),
                                     'mobile': row.get('mobile1'),
                                     'phone2': row.get('phone2'),
                                     'mobile2': row.get('mobile2'),
                                     'street': row.get('Address'),
                                     'street2': row.get('Landmark'),
                                     'city_id': city_id,
                                     'area_id':area_id,
                                     })]
            }
        return partner_obj.create(cr, uid, vals, context)
    
    def create_area(self, cr, uid, row, context=None):
        area_obj = self.pool.get('sabugar.city.area')
        city_id = self.create_city(cr, uid, row, context)
               
        area_ids = area_obj.search(cr, uid, [('name','=',row.get('Area','Unknown')),('city_id','=',int(city_id))])
        if area_ids:
            return (area_ids[0],city_id)
        else:
            vals = {
                'name' : row.get('Area','Unknown'),
                'city_id' : city_id,
            }
            area_id = area_obj.create(cr, uid, vals, context=context)
            return (area_id,city_id)
            
        
        
    def create_city(self, cr, uid, row, context=None):
        city_obj = self.pool.get('sabugar.city')
        city_ids = city_obj.search(cr, uid, [('name','=',row.get('City','Unknown'))])
        if city_ids:
            return city_ids[0]
        else:
            vals = {
                'name' : row.get('City','Unknown')
            }
            return city_obj.create(cr, uid, vals, context=context)
        
    def create_user(self, cr, uid, row, context=None):
        if context==None:
            context={}
        user_obj = self.pool.get('res.users')
        user_ids = user_obj.search(cr, uid, [('name','=',row.get('callername','Unknown'))])
        if user_ids:
            return user_ids[0]
        else:
            vals={
              'name':row.get('callername','Unknown'),
              'login':row.get('callername','Unknown'),
              'password':row.get('callername','Unknown'),
              }
            return user_obj.create(cr, uid, vals, context=context)
import_csv()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
