# -*- coding: utf-8 -*-


from eaglet.core import api_resource
from eaglet.decorator import param_required

from business.mall.product import Product


class AProductOffshelf(api_resource.ApiResource):
	"""
	待售商品管理

	"""
	app = "product"
	resource = "offshelf_products"

	@param_required(['owner_id'])
	def get(args):
		'''
		待售商品列表
		'''
		opt = {
			'owner_id': args['owner_id'],
			'shelve_type': 0,   #int 0 待售标志 
			'is_deleted': False,
			'fill_options': {
				'with_selected_category': True,
				'with_all_category': True,
				'with_image': True,
				'with_property': True,
				'with_group_buy_info': True,
				'with_sales': True,
				'with_product_promotion': True,
				'with_price': True,
				'with_product_model': True

			} # 填充参数
		}
		# 分页
		page_info = {
			'cur_page': int(args.get('cur_page', 1)),
			'count_per_page': int(args.get('count_per_page', 10))
		}
		opt.update(page_info)
		products, pageinfo = Product.from_owner_id(opt)
		return {
			'pageinfo': pageinfo.to_dict(),
			'products': [product.to_dict() for product in products]
		}