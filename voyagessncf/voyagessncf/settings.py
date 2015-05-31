import os


BOT_NAME = 'voyagessncf'

SPIDER_MODULES = ['voyagessncf.spiders']
NEWSPIDER_MODULE = 'voyagessncf.spiders'

ITEM_PIPELINES = {}
current_dir = os.path.dirname(os.path.realpath(__file__))
