# -*- coding: utf-8 -*-
import json

from behave import *
from features.util import bdd_util
from db.mall import models as mall_models


def __limit_type_name2number(name):
	if u'无限制' == name:
		return 0
	elif u'仅发货地区' == name:
		return 1
	elif u'不发货地区' == name:
		return 2
	else:
		return -1

def __postage_type_name2bool(name):
	if u"统一运费" == name:
		return True
	else:
		return False

def __product_names2ids_str(name_list):
	models = mall_models.ProductPendingStock.select().dj_where(name__in=name_list)
	return [m.id for m in models]

@when(u"{user}创建待入库商品")
def step_impl(context, user):
	datas = json.loads(context.text)
	for data in datas:
		response = context.client.put('/mall/pending_stock_product/', {
			'corp_id': bdd_util.get_user_id_for(user),
			'name': data['product_name'],
			'title': data['promotion_title'],
			'has_product_model': data['has_product_model'],
			'price': data['price'],
			'weight': data['weight'],
			'store': data['store'],
			'limit_zone_type': __limit_type_name2number(data['limit_zone_type']),
			'has_same_postage': __postage_type_name2bool(data['postage_type']),
			'postage_money': data['postage_money'],
			'remark': data['remark']
		})
		bdd_util.assert_api_call_success(response)

@when(u"{user}审核通过待入库商品")
def step_impl(context, user):
	datas = json.loads(context.text)
	response = context.client.put('/mall/review_pending_product/', {
		'corp_id': bdd_util.get_user_id_for(user),
		'product_ids': json.dumps(__product_names2ids_str(datas))
	})
	bdd_util.assert_api_call_success(response)