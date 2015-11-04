# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import signals
from scrapy.exceptions import DropItem

class DuplicateAndFilterConditionPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['link'] in self.ids_seen or len(item['condition'])<2:
            raise DropItem("Duplicate or useless item found: %s" % item)
        else:
            self.ids_seen.add(item['link'])
            return item