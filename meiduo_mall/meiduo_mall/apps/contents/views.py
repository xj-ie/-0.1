from django.shortcuts import render
from django.views import View
from collections import OrderedDict
# Create your views here.
# from goods.models import GoodsChannel, GoodsChannelGroup, GoodsCategory
from goods.models import GoodsCategory, GoodsChannelGroup, GoodsChannel, ContentCategory
from contents.utils import get_categories

# GoodsCategory(广告类别)
# GoodsChannelGroup(广告频道）
# GoodsChannel(商品频道

class INDEX_VIEWS(View):
    # def get(self, request):
    #     """提供首页广告界面"""
    #     """"""
    #     categories = {}
    #     channels = GoodsChannel.objects.all().order_by("sequence")
    #     # channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    #
    #     for channel in channels:
    #         group_id = channel.group_id
    #     # for channel in channels:
    #     #     group_id = channel.group_id  # 当前组
    #
    #         if group_id not in categories:
    #             categories["group_id"] = {"channels": [], "sub_cats": []}
    #         # if group_id not in categories:
    #             # categories[group_id] = {'channels': [], 'sub_cats': []}
    #
    #         # cat1 = channel.category  # 当前频道的类别
    #         ca1 = channel.category
    #         categories["group_id"]['channels'].append({"id": ca1.id, "name": ca1.name, 'url': channel.url})
    #         for ca2 in ca1.subs.all():
    #             ca2.sub_cats = []
    #             for ca3 in ca2.subs.all():
    #                 ca2.sub_cats.append(ca3)
    #             categories["group_id"]["sub_cats"].append(ca2)
    #     context = {
    #         'categories': categories,
    #     }
    #     # print(categories)
    #
    #
    #     """
    #
    #     """
    #     return render(request, 'index.html', context)
    def get(self, request):
        """提供首页广告页面"""
        # 查询并展示商品分类
        categories = get_categories()

        # 查询首页广告数据
        # 查询所有的广告类别
        contents = OrderedDict()
        content_categories = ContentCategory.objects.all()
        for content_category in content_categories:
            # 使用广告类别查询出该类别对应的所有的广告内容
            contents[content_category.key] = content_category.content_set.filter(status=True).order_by('sequence') # 查询出未下架的广告并排序

        # 构造上下文
        context = {
            'categories':categories,
            'contents':contents
        }

        return render(request, 'index.html', context)
