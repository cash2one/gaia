# -*- coding: utf-8 -*-
import json

from eaglet.core import api_resource
from eaglet.decorator import param_required
from business.mall.supplier_factory import SupplierFactory

class ASupplier(api_resource.ApiResource):
    """
    供货商的信息
    """
    app = "mall"
    resource = "supplier"

    @param_required(['owner_id', 'name', 'responsible_person', 'supplier_tel', 'supplier_address'])
    def put(args):
        owner_id = int(args['owner_id'])
        name = args['name']
        responsible_person = args['responsible_person']
        supplier_tel = args['supplier_tel']
        supplier_address = args['supplier_address']
        remark = args.get('remark', '')

        supplier = SupplierFactory.create({
                'owner_id': owner_id,
                'name': name,
                'responsible_person': responsible_person,
                'supplier_tel': supplier_tel,
                'supplier_address': supplier_address,
                'remark': remark
            })

        return supplier.save()