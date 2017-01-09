# -*- coding: utf-8 -*-

from eaglet.core import paginator

from business import model as business_model
from business.account.user_profile import UserProfile
from business.product.fill_product_detail_service import FillProductDetailService
from db.mall import models as mall_models
from product import Product

class GlobalProductRepository(business_model.Service):
	def filter_products(self, query_dict, page_info, fill_options=None):
		db_models = mall_models.Product.select().dj_where(is_deleted=False)

		if query_dict.get('owner_name'):
			pass
		print ('---------------------')
		print (query_dict['corp'].is_weizoom_corp())
		print ('---------------------')
		if query_dict['corp'].is_weizoom_corp():
			db_models = db_models.where(
				(mall_models.Product.pending_status << [mall_models.PRODUCT_PENDING_STATUS['SUBMIT'], mall_models.PRODUCT_PENDING_STATUS['REFUSED']])
				| (mall_models.Product.is_accepted == True)
			)
		else:
			db_models = db_models.dj_where(owner_id=query_dict['corp'].id)


		owner_ids = [p.owner_id for p in db_models]
		owner_id2name = UserProfile.get_user_id_2_username(owner_ids)

		if page_info:
			pageinfo, db_models = paginator.paginate(db_models, page_info.cur_page, page_info.count_per_page)
		else:
			pageinfo = None

		products = []
		for model in db_models:
			pre_product = Product(model)
			setattr(pre_product.__class__, 'owner_name', owner_id2name[model.owner_id])
			products.append(pre_product)

		fill_options = fill_options if fill_options else {}
		FillProductDetailService.get().fill_detail(products, fill_options)

		return pageinfo, products

	def get_product(self, product_id, fill_options=None):
		db_model = mall_models.Product.select().dj_where(id=product_id, is_deleted=False).get()
		product_model = Product(db_model)
		fill_options = fill_options if fill_options else {}
		FillProductDetailService.get().fill_detail([product_model], fill_options)
		return product_model

	def get_products_by_ids(self, product_ids, fill_options=None):
		db_models = mall_models.Product.select().dj_where(id__in=product_ids, is_deleted=False)
		product_models = [Product(db_model) for db_model in db_models]
		fill_options = fill_options if fill_options else {}
		FillProductDetailService.get().fill_detail(product_models, fill_options)
		return product_models
