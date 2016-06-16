# -*- coding: utf-8 -*-

from business.mall.express.express_request_params import *
from eaglet.core import watchdog
from eaglet.core.exceptionutil import unicode_full_stack
import urllib, urllib2
import json
import settings
from hashlib import md5
import base64
#from tools.express.models import *
from db.express.models import *
from business.mall.express.kdniao_express_config import *

def post(url, data): 
    req = urllib2.Request(url) 
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor()) 
    response = opener.open(req, data) 
    return response.read() 
express2kdniaocode = {'quanfengkuaidi': 'QFKD', 'shentong': 'STO', 'zhaijisong': 'ZJS', 'rufengda': 'RFD', 
	'debangwuliu': 'DBL', 'shunfeng': 'SF', 'yunda': 'YD', 'bpost': 'BEL', 'tiantian': 'HHTT', 
	'suer': 'SURE', 'ems': 'EMS', 'zhongtong': 'ZTO', 'kuaijiesudi': 'FAST', 'yuantong': 'YTO', 
	'huitongkuaidi': 'HTKY', 'guotongkuaidi': 'GTO', 'youzhengguonei': 'YZPY'}

class KdniaoExpressPoll(object):
	'''
	快递鸟 订阅请求
		通信协议:HTTP
		请求类型:POST
		字符集:utf-8
	参数说明：

		RequestData	String	R	请求内容，JSON或XML格式,须和DataType一致
		EBusinessID	String	R	电商ID
		RequestType	String	R	请求指令类型：1005
		DataSign	String	R	数据内容签名
		DataType	String	O	请求、返回数据类型：1-xml,2-json；默认为xml格式
		Code	String	R	快递公司编码
		Item	String	R	物流单号集合
		No	String	R	快递物流单号
		Bk	String	O	用户标识
		O代表必须，R代表非必须
	注意：'Bk': str(self.express.id)，通过bk标记ExpressHasOrderPushStatus中的id,
		订阅后在快递鸟服务器向weapp推送中变成了CallBack。

	测试url:"http://api.kdniao.cc/Ebusiness/EbusinessOrderHandle.aspx"
	data格式：RequestData=xxx&DataType=xxx
	data：RequestData={'Item': [{'Bk': '', 'No': '1060515954609'}], 'Code': 'EMS'}&
			RequestType=1005&DataSign=OWJlYTIxZmI5Zjk3OTZmZTYwYWI4NGZjNWI0MGJhOTM=&
			DataType=2&EBusinessID=1256042

	return:
		{
		"EBusinessID": "1256042",
		"UpdateTime": "2016/2/24 12:17:13",
		"Success": true,
		"Reason": ""
		}

	result: "true"表示成功，false表示失败
	'''
	
	def __init__(self, order):
		self.Business_id = KdniaoExpressConfig.EBusiness_id
		self.api_key = KdniaoExpressConfig.api_key
		self.express_company_name = order.express_company_name if order.express_company_name else ''
		self.express_company_name_kdniao = express2kdniaocode[self.express_company_name]
		self.express_number = order.express_number if order.express_number else ''
		self.order = order
		self.order_id = order.id
		self.area = order.ship_area
		self.express = None
		self.express_config = KdniaoExpressConfig()
		self.webapp_id = order.webapp_id

		# 伪造
		# self.express_company_name = 'EMS'
		# self.express_number = 1060515954609

	def _encrypt(self, param_json_data):
		return base64.b64encode(md5(param_json_data + self.api_key).hexdigest())


	def _poll_response(self):
		"""
		发送快递100 订阅请求，返回成功与否信息
		"""
		# post中的param的json

		param_json_data = {'Code': self.express_company_name_kdniao,'Item': [
                           {'No': str(self.express_number),'Bk': str(self.express.id)},
                           ]}
		DataSign= self._encrypt(str(param_json_data))
		params = {
		"RequestData": param_json_data,
		"EBusinessID": self.Business_id ,
		"RequestType": "1005",
		"DataSign": DataSign,
		"DataType": "2"
		}

		#将数据处理为RequestData=xxx&DataType=xxx这种格式的
		param_str = urllib.urlencode(params)
		
		verified_result = ''
		try:
			verified_result = post(KdniaoExpressConfig.req_url, param_str)
			watchdog.info(u"发送快递鸟 订阅请求 url: {},/n param_data: {}, /n response: {}".format(
				KdniaoExpressConfig.req_url, 
				param_str,
				verified_result.decode('utf-8')), self.express_config.watchdog_type)
		except:
			watchdog.error(u'发送快递鸟 订阅请求 失败，url:{},data:{},原因:{}'.format(KdniaoExpressConfig.req_url,
				param_str,
				unicode_full_stack()), self.express_config.watchdog_type)

		return verified_result

	def _is_poll_by_order(self):
		try:
			pushs = ExpressHasOrderPushStatus.select().dj_where(
					# order_id = self.order_id,
					express_company_name = self.order.express_company_name,
					express_number = self.order.express_number
					)
			if pushs.count() > 0:
				push = pushs[0]

				# 不需要重新发送订阅请求的状态
				if push.status in EXPRESS_NOT_PULL_STATUSES:
					return True

				# 超过4次发送就不再发送次快递
				if push.send_count >= 4:
					return True
					
				# 关闭，重发订阅,由于某种原因订阅失败
				if push.abort_receive_message and len(push.abort_receive_message) > 0:
					return False

				# 第一次发送订阅
				if push.status == EXPRESS_PULL_SUCCESS_STATUS and push.send_count > 0:
					return True

			return False
		except:
			watchdog.error(u'快递鸟tool_express_has_order_push_status表异常，获取订单信息，express_company_name:{}，express_number:{}'.format(self.order.express_company_name, self.order.express_number))
			return False

	def _save_poll_order_id(self):
		pushs = ExpressHasOrderPushStatus.select().dj_where(
			express_company_name = self.order.express_company_name,
			express_number = self.order.express_number
		)

		if pushs.count() > 0:
			return pushs[0]

		else:
			express = ExpressHasOrderPushStatus.create(
				order_id = -1,
				status = EXPRESS_PULL_NOT_STATUS,
				express_company_name = self.order.express_company_name,
				express_number = self.order.express_number,
				service_type = KDNIAO,
				webapp_id = self.webapp_id,
				abort_receive_message = ""

			)
			return express

	def get_express_poll(self):
		# 如果是空不处理
		if self.express_company_name_kdniao is '' or self.express_number is '':
			return False

		# 是否已经订阅过该订单，并且成功
		status = self._is_poll_by_order()
		if status:
			return True

		# 保存快递信息	
		self.express = self._save_poll_order_id()

		# 发送订阅请求
		data = self._poll_response()
		data = json.loads(data)
		result = True if data.get('Success') == "true" or data.get('Success') is True else False

		if result:
			# 修改快递信息状态,self.express.status = 200订阅成功，0未订阅
			self.express.status = 200
			self.express.send_count = self.express.send_count + 1
			self.express.abort_receive_message = ""
			self.express.save()
			return True
		else:
			if data and data.get('Reason'):
				print "Reason:",data.get('Reason')
				self.express.status = 0
				self.express.abort_receive_message = data.get('Reason')
				self.express.save()
				watchdog.error(u'发送快递鸟 订阅请求存在问题，url:{},订单id:{},原因:{}'.format(KdniaoExpressConfig.req_url,
					self.order_id,
					data.get('Reason')))
			return False
