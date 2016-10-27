Feature: 添加属性模板
"""
	Jobs通过管理系统在商城中添加属性模板
"""

@gaia @mall @mall.product @mall.product_property_template @hermes
Scenario:1 更新属性模板
	jobs更新属性模板的名称和属性后
	1. job的属性模板更新
	2. bill的属性模板不受影响
	
	Given jobs登录系统
	When jobs添加属性模板
		"""
		[{
			"name": "计算机模板",
			"properties": [{
				"name": "CPU",
				"description": "CPU描述"
			}, {
				"name": "内存",
				"description": "内存描述"
			}]
		}, {
			"name": "大米模板",
			"properties": [{
				"name": "产地",
				"description": "产地描述"
			}]
		}, {
			"name": "空模板",
			"properties": []
		}]
		"""
	Then jobs能获取属性模板列表
		"""
		[{
			"name": "计算机模板",
			"properties": [{
				"name": "CPU",
				"description": "CPU描述"
			}, {
				"name": "内存",
				"description": "内存描述"
			}]
		}, {
			"name": "大米模板",
			"properties": [{
				"name": "产地",
				"description": "产地描述"
			}]
		}, {
			"name": "空模板",
			"properties": []
		}]
		"""
	Given bill登录系统
	Then bill能获取属性模板列表
		"""
		[]
		"""
