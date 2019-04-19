from osv import osv, fields


class stock_balance(osv.osv_memory):
    
    _name = 'stock.balance'
    
    _columns = {

        'start_date':fields.date('From Date'), 
        'end_date':fields.date('To Date'), 
        'location_ids':fields.many2many('stock.location', 'stock_id', 'location_id','stock_location_rel'), 
    }
    
    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids' : data.get('location_ids'), 
             'model': 'stock.location', 
             'form': data,
             'new_ids' : data.get('location_ids'),
           
                 }
        return {
            'type': 'ir.actions.report.xml', 
            'report_name': 'stock.balance.new', 
            'datas': datas, 
            }
    
stock_balance()
    
    