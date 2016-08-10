# -*- coding: utf-8 -*-

import json

from eaglet.core import api_resource
from eaglet.decorator import param_required
from eaglet.core import watchdog
from eaglet.core.exceptionutil import unicode_full_stack

from business.mall.product_factory import ProductFactory
from business.mall.product import Product, ProductModel, ProductSwipeImage, ProductPool
from settings import PANDA_IMAGE_DOMAIN


class AProduct(api_resource.ApiResource):
    """
    商品上架状态处理
    """

    app = "product"
    resource = "product"

    @param_required(['ids'])
    def delete(args):
        pass
        