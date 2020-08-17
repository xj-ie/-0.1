import sys
sys.path.insert(0, '../')
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'

import django
django.setup()

from django.conf import settings

import os
from collections import OrderedDict
# from unittest import loader
from django.template import loader
from contents.utils import get_categories
from goods.models import ContentCategory



def get_index_html():
    categories = get_categories()

    # 查询首页广告数据
    # 查询所有的广告类别
    contents = OrderedDict()
    content_categories = ContentCategory.objects.all()
    for content_category in content_categories:
        # 使用广告类别查询出该类别对应的所有的广告内容
        contents[content_category.key] = content_category.content_set.filter(status=True).order_by(
            'sequence')  # 查询出未下架的广告并排序

    # 构造上下文
    context = {
        'categories': categories,
        'contents': contents
    }

    template = loader.get_template('index.html')
    set_index_html = template.render(context)
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'index.html')
    with open(file_path, 'w') as file:
        file.write(set_index_html)

if __name__ == '__main__':
    get_index_html()
