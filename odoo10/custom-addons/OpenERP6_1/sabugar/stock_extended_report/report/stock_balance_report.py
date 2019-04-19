from report import report_sxw
from datetime import date, timedelta
import time
import datetime

class stock_balance(report_sxw.rml_parse):

     def _get_product(self, location_id, start_date, end_date):
         context = {}
         
         product_obj = self.pool.get('product.product')
         stock_move_obj = self.pool.get('stock.move')
         account_fiscal_obj = self.pool.get('account.fiscalyear')
         
         
         #searched stock move ids by its location from stock move
         stock_move_ids = stock_move_obj.search(self.cr, self.uid, [('location_id', '=', location_id)])

         get_product_data_in = {}
         get_product_data_out = {}
         get_product_data = {}
         product_id_list = []
         final_product_id_list = []
         #globlal list which contaion all the data
         product_data_list= []
         #listed product ids from stock_move id's list
         for stock_move_id in stock_move_ids:
             
             product_id = stock_move_obj.browse(self.cr, self.uid, stock_move_id)
             product_id_list.append(product_id.product_id.id)
         
         for id in product_id_list:
             if id not in final_product_id_list:
                  final_product_id_list.append(id)
         
         context.update({'from_date':start_date, 'to_date':end_date, 'states':['done'], 'what':('in'), 'location':location_id})
         get_product_data_in = product_obj.get_product_available(self.cr, self.uid, final_product_id_list, context)
         
         context.update({'what':('out')})
         get_product_data_out = product_obj.get_product_available(self.cr, self.uid, final_product_id_list, context)

         #for getting opening balance of product
         fiscal_id = account_fiscal_obj.browse(self.cr,self.uid,1)
         fiscal_start_date = fiscal_id.date_start
         fiscal_end_date = start_date
         fiscal_end_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
         fiscal_end_date = fiscal_end_date.date() - timedelta(days=1)
         new_end_date = datetime.datetime.strftime(fiscal_end_date,'%Y-%m-%d')
         context.update({'from_date':fiscal_start_date,'to_date':new_end_date,'what':('in','out')})
         get_product_data = product_obj.get_product_available(self.cr, self.uid, final_product_id_list, context)
         #listing prodcut name in dictionary
         
         p_data = product_obj.browse(self.cr, self.uid, final_product_id_list)
         
         #appened all the data by its category into the product_data_list
         for data in p_data:
             product_data_list.append({'name':data.name, 'in':get_product_data_in.get(data.id), 
                                       'out':get_product_data_out.get(data.id), 
                                       'opening':get_product_data.get(data.id)})
         return product_data_list
     
     def __init__(self, cr, uid, name, context):
        super(stock_balance, self).__init__(cr, uid, name, context=context)
        
        self.localcontext.update({
            'get_product':self._get_product, 
         
        })
    
    
report_sxw.report_sxw('report.stock.balance.new', 'stock.location', 'addons/stock_extended_report/report/stock_extended_report_view.rml', parser=stock_balance, header=False)
