# -*- coding: utf-8 -*-

import copy
from datetime import datetime
import json

from eaglet.core.db import models
from db.account.models import User, UserProfile
from eaglet.core import watchdog
import settings


EXPRESS_TYPE = 'EXPRESS_API'

'''
快递详细信息
'''
class ExpressDetail(models.Model):
    order_id = models.IntegerField(verbose_name="订单id，以后暂不使用", default=-1)
    express_id = models.IntegerField(verbose_name="快递id", default=-1)
    context = models.CharField(max_length=1024, verbose_name="内容")
    status = models.CharField(max_length=50, verbose_name="状态")
    time = models.DateTimeField(verbose_name="时间，原始格式")
    ftime = models.CharField(max_length=50, verbose_name="格式化后时间")
    display_index = models.IntegerField(default=1, db_index=True, verbose_name="显示的排序")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta(object):
        db_table = 'tool_express_detail'
        verbose_name = '快递明细'
        verbose_name_plural = '快递明细'


'''
快递推送状态
'''
EXPRESS_PULL_NOT_STATUS = 0             # 未订阅
EXPRESS_PULL_SUCCESS_STATUS = 200       # 订阅成功
EXPRESS_PULL_REFUSE_STATUS = 701        # 拒绝订阅的快递公司
EXPRESS_PULL_INFO_ERROR_STATUS = 700    # 订阅方的订阅数据存在错误（如不支持的快递公司、单号为空、单号超长等）
EXPRESS_PULL_KEY_ERROR_STATUS = 600     # 您不是合法的订阅者（即授权Key出错）
EXPRESS_PULL_SERVER_ERROR_STATUS = 500  # 服务器错误
EXPRESS_PULL_REPEAT_STATUS = 501        # 重复订阅
# 不需要重新发送订阅请求的状态
EXPRESS_NOT_PULL_STATUSES = [
    EXPRESS_PULL_REFUSE_STATUS,
    EXPRESS_PULL_INFO_ERROR_STATUS,
    EXPRESS_PULL_REPEAT_STATUS
]

'''
快递服务商编号
'''
EXPRESS_100 = 0             #快递100
KDNIAO = 1                  #快递鸟


class ExpressHasOrderPushStatus(models.Model):
    order_id = models.IntegerField(verbose_name="订单id，以后暂不使用", default=-1)
    express_company_name = models.CharField(max_length=50, default='', verbose_name="快递公司名称")
    express_number = models.CharField(max_length=100, verbose_name="快递单号")
    status = models.IntegerField(default=EXPRESS_PULL_NOT_STATUS, verbose_name="状态")
    send_count = models.IntegerField(default=0, verbose_name="发送订阅请求次数")
    receive_count = models.IntegerField(default=0, verbose_name="接收推送请求次数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    # 重新订阅的依据信息（当重推后，该两字段的信息，将被清空）
    # abort_receive_at: 第一次接收 失败信息的时间
    # abort_receive_message 第一次接收 "status":"abort"而且message中包含“3天”关键字的数据
    abort_receive_at = models.DateTimeField(null=True, blank=True, verbose_name="接收信息时间")
    abort_receive_message = models.TextField(verbose_name="接收的信息")
    service_type = models.IntegerField(default=0, verbose_name="快递服务类型")
    webapp_id = models.CharField(max_length=20, default='', db_index=True, verbose_name='店铺ID')  # webapp

    class Meta(object):
        db_table = 'tool_express_has_order_push_status'
        verbose_name = '订单的推送状态'
        verbose_name_plural = '订单的推送状态'


    @staticmethod
    def get(id):
        express = ExpressHasOrderPushStatus.objects.filter(id=id)
        if express.count() > 0:
            return express[0]
        else:
            return None

    @staticmethod
    def get_by_order(order):
        express = ExpressHasOrderPushStatus.objects.filter(express_company_name=order.express_company_name, express_number=order.express_number)
        if express.count() > 0:
            return express[0]
        else:
            return None