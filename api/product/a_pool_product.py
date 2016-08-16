# -*- coding: utf-8 -*-


from eaglet.core import api_resource
from eaglet.decorator import param_required

from business.mall.product import Product
from business.mall.product_pool import ProductPool


class AProduct(api_resource.ApiResource):
	"""
	商品
	"""
	app = "product"
	resource = "pool_product"

	@param_required(['owner_id', 'product_id'])
	def put(args):
		pool = ProductPool.get({'owner_id': args['owner_id']})
		product = Product.from_id({'product_id': args['product_id']})
		is_success, msg = pool.push(product)
		if is_success:
			return {}
		else:
			return 500, {'msg': msg}

	@param_required(['owner_id', 'product_id'])
	def delete(args):
		pool = ProductPool.get({'owner_id': args['owner_id']})
		product = Product.from_id({'product_id': args['product_id']})
		is_success = pool.pop(product)
		if is_success:
			return {}
		else:
			return 500, {}
