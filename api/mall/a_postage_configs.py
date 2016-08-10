# -*- coding: utf-8 -*-

from eaglet.core import api_resource
from eaglet.decorator import param_required

from business.mall.postage_config import PostageConfig


class APostageConfig(api_resource.ApiResource):
    """
    运费模板集合
    """
    app = 'mall'
    resource = 'postage_configs'


    @param_required(['owner_id'])
    def get(args):
        postage_configs = PostageConfig.get_list({'owner_id': args['owner_id']})

        return {
            'postage_configs': postage_configs
        }