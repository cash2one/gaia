# -*- coding: utf-8 -*-

from eaglet.core import api_resource
from eaglet.decorator import param_required

from business.mall.corporation_factory import CorporationFactory

class AProductClassificationQualification(api_resource.ApiResource):
    """
    商品分类特殊资质
    """
    app = "mall"
    resource = "product_classification_qualification"

    @param_required(['corp_id', 'classification_id', 'qualification_infos:json'])
    def put(args):
        classification_id = args['classification_id']
        qualification_infos = args['qualification_infos']

        corp = CorporationFactory.get()
        classification = corp.product_classification_repository.get_product_classification(classification_id)
        classification.set_qualifications(qualification_infos)

        return {}

