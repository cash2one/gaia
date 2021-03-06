# -*- coding: utf-8 -*-

from eaglet.core import api_resource
from eaglet.decorator import param_required


class APaidOrder(api_resource.ApiResource):
	"""
	已支付的订单
	"""
	app = 'order'
	resource = 'paid_order'

	@param_required(['id'])
	def put(args):
		"""
		支付订单
		@return:
		"""
		corp = args['corp']
		id = args['id']

		order_repository = corp.order_repository
		order = order_repository.get_order(id)
		if order:
			is_success, msg = order.pay(corp)
			if is_success:
				return {}
			else:
				return 500, {'msg': msg}
		else:
			return 500, {}
