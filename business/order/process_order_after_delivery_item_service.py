# -*- coding: utf-8 -*-
from bdem import msgutil
from eaglet.decorator import param_required

from business import model as business_model
from business.mall.supplier import Supplier
from business.order.delivery_item_product_repository import DeliveryItemProductRepository
from db.express import models as express_models
from db.mall import models as mall_models
from zeus_conf import TOPIC


class ProcessOrderAfterDeliveryItemService(business_model.Service):
	def process_order(self, delivery_item):
		"""
		当处理的是出货单时，需要决策是否处理以及如何处理订单
		@param delivery_item:
		@param from_status:
		@param to_status:
		@return:
		"""

		if delivery_item.is_use_delivery_item_db_model:

			order_id = delivery_item.origin_order_id

			delivery_item_repository = self.corp.delivery_item_repository
			delivery_items = delivery_item_repository.get_delivery_items_by_order_id(order_id)
			delivery_items_status_list = [o.status for o in delivery_items]

			# 获取出货单权重集合
			delivery_item_weights = [mall_models.ORDER_STATUS2DELIVERY_ITEM_WEIGHT[status] for status in
			                         delivery_items_status_list]

			to_status = mall_models.DELIVERY_ITEM_WEIGHT2ORDER_STATUS[min(delivery_item_weights)]

			order = self.corp.order_repository.get_order(order_id)

			if order.status != to_status:
				if to_status == mall_models.ORDER_STATUS_SUCCESSED:
					order.finish(self.corp)
