from django.shortcuts import render
from django.views import View
# Create your views here.
# from goods.models import GoodsChannel, GoodsChannelGroup, GoodsCategory
from goods.models import GoodsCategory,GoodsChannelGroup,GoodsChannel
# GoodsCategory(广告类别)
# GoodsChannelGroup(广告频道）
# GoodsChannel(商品频道
class INDEX_VIEWS(View):
    def get(self, request):
        """提供首页广告界面"""
        """"""
        categories = {}
        channels =  GoodsChannel.objects.all().order_by("sequence")
        for channel in channels:
            group_id = channel.group_id

            if group_id not in categories:
                categories["group_id"]={  "channels": [
                ],
                "sub_cats": [
                        ]}
            ca1 = channel.category
            categories["group_id"]['channels'].append({"id":ca1.id,"name":ca1.name,'url': channel.url})
            for ca2 in ca1.subs.all():
                ca2.sub_cats=[]
                for ca3 in ca2.subs.all():
                    ca2.sub_cats.append(ca3)
                categories["group_id"]["sub_cats"].append(ca2)
        context = {
            'categories': categories,
        }
        print(categories)
        return render(request, 'index.html', context)











        return render(request, 'index.html')