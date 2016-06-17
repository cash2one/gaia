# -*- coding: utf-8 -*-
import json

from eaglet.core import api_resource, paginator
from eaglet.decorator import param_required

from business.mall.order_product_relation import OrderProductRelation
from business.mall.order import Order
from business.mall.order_items import OrderItems
from business.account.user_profile import UserProfile

class AOrderExport(api_resource.ApiResource):
    """
    订单导出
    """
    app = 'panda'
    resource = 'order_export'

    @param_required(['product_ids'])
    def get(args):
        """
        订单列表
        """
        product_ids = args['product_ids'].split("_")

        relations = OrderProductRelation.get_for_product({
            'product_ids': product_ids
        })
        order_ids = [relation.order_id for relation in relations]
        orders = Order.from_ids({
            'ids': order_ids
        })
        orders = filter(lambda order: order.origin_order_id > 0, orders)
        orders = AOrderExport.search_orders(orders, args)

        return {
            'orders': [order.to_dict('products') for order in orders],
        }

    @staticmethod
    def search_orders(orders=None, args={}):
        # 筛选
        order_id = args.get('order_id', "")
        start_time = args.get('start_time', "")
        end_time = args.get('end_time', "")
        order_status = args.get('status', "")
        webapp_id = args.get('webapp_id', "")

        if order_id:
            orders = filter(lambda order: order.order_id == order_id, orders)
        if order_status:
            orders = filter(lambda order: order.status == int(order_status), orders)
        if webapp_id:
            orders = filter(lambda order: order.webapp_id == webapp_id, orders)
        if start_time and end_time:
            orders = filter(lambda order: order.created_at.strftime('%Y-%m-%d %H:%M:%S') >= start_time and order.created_at.strftime('%Y-%m-%d %H:%M:%S') <= end_time, orders)
        return orders