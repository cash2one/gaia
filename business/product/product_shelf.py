# -*- utf-8 -*-
from datetime import datetime
from bdem import msgutil
from eaglet.utils.resource_client import Resource
from eaglet.decorator import param_required

from db.mall import models as mall_models
from business import model as business_model


class ProductShelfError(Exception):
	def __init__(self, err_msg):
		self.err_msg = err_msg


class ProductShelf(business_model.Model):
	__slots__ = (
		'owner_id',
		'topic_name',
		'type',
		'msg_name'
	)

	def __init__(self, owner_id, type):
		self.owner_id = owner_id
		self.type = type
		self.topic_name = "zeus-product"

	@staticmethod
	@param_required(['owner_id', 'type'])
	def get(args):
		owner_id = args['owner_id']
		type = args['type']
		if type in ('onsell', 'outsell'):
			return ProductShelf(owner_id, type)
		else:
			raise ProductShelfError('Product Shelf Type Error!')

	def add_products(self, product_ids):
		if product_ids:
			if self.type == 'onsell':
				self.msg_name = 'msg_onsell_product'
				product_shelf_type = mall_models.PP_STATUS_ON
			elif self.type == 'outsell':
				self.msg_name = 'msg_outsell_product'
				product_shelf_type = mall_models.PP_STATUS_OFF
			mall_models.ProductPool.update(
				status=product_shelf_type,
				display_index=0
			).dj_where(id__in=product_ids, woid=self.owner_id, status__gt=mall_models.PP_STATUS_DELETE).execute()

			self.__send_msg_to_topic(product_ids)
		return product_ids

	def move_products(self, product_ids):
		product_ids = self.__exclude_group_product_id(product_ids)
		if product_ids:
			product_ids = self.add_products(product_ids)
		return product_ids

	def __exclude_not_move_product_id(self, product_ids):
		params = {'woid': self.owner_id, 'pids': '_'.join([str(id) for id in product_ids])}

		resp = Resource.use('marketapp_apiserver').get({
			'resource': 'group.group_buy_products',
			'data': params
		})
		if resp and resp['code'] == 200:
			data = resp['data']
			product_groups = data['pid2is_in_group_buy']
			group_product_ids = []
			for product_group in product_groups:
				if product_group['pid'] in product_ids and product_group["is_in_group_buy"]:
					product_ids.remove(product_group['pid'])
					group_product_ids.append(product_group['pid'])
		return product_ids

	def __send_msg_to_topic(self, product_ids):
		data = {
			"product_ids": product_ids
		}
		msgutil.send_message(self.topic_name, self.msg_name, data)
