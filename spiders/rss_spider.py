from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from scrapy.http import Request
from rss_crawler.items import RSSItem
# from scrapy.spiders import XMLFeedSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import XmlXPathSelector
from bs4 import BeautifulSoup
import feedparser
import re
from urlparse import urlparse
import xml.sax

import lxml.html
from lxml.etree import ParserError
from lxml.cssselect import CSSSelector
from scrapy import log

from rss_crawler.items import RssFeedItem, RssEntryItem
import chardet
import datetime
from dateutil.tz import tzutc

class RSSSpider(BaseSpider):
    name = "rss"
    
    _allowed_domain = {"mscaregiverdonna.wordpress.com" }
    start_urls = [
        "https://mscaregiverdonna.wordpress.com/"
    ]
    
    _gathered_fields = ('published_parsed' ,'title' ,  'link' ,'summary');

    
    def parse(self, response):
        try:
            document = lxml.html.fromstring(response.body)
            document.make_links_absolute(base_url=response.url, resolve_base_href=True)
        except ParserError:
            #Document is probably empty, return no items
            return
        rss_elements = CSSSelector('rss, feed, xml, rdf, atom')(document)
        character_set = chardet.detect(response.body)["encoding"]
        # is this an rss file
        if all((rss_elements, character_set)):
            try:
                feed = feedparser.parse(
                    url_file_stream_or_string = response.body,

                )

                #seeing as we've requested the document, might as well save it
                if feed.version:
                    rssFeedItem = RssFeedItem(url = response.url);
                    for key in {'title', 'summary', 'link'} & feed.feed.__dict__.viewkeys():
                        rssFeedItem[key] = getattr(feed.feed, key)
                    rssFeedItem['entries'] = []
                    for entry in feed.entries:
                        entry_item = RssEntryItem()
                        published = entry.get("published_parsed", None)
                        if published:
                            entry["published"] = datetime.datetime(*(published[0:6]), tzinfo=tzutc()).isoformat()
                        for key in {'title', 'link', 'summary', 'published'} & entry.viewkeys():
                            entry_item[key] = entry[key]
                        soup = BeautifulSoup(entry['summary'], 'html.parser')
                        entry_item['summary'] = soup.get_text(separator=u' ').replace(u'\xa0', u' ') 
                        entry_item['url'] = rssFeedItem['url']
                        yield entry_item
                else:
                    self.log("{url} looked like a feed, but wasn't one".format(url=response.url), level=log.DEBUG)
            except xml.sax.SAXException:
                pass
            
        urls = set(
            map(
                lambda x: x[2], #the link is third element from items in iterlinks
                document.iterlinks()
            )
        )

        for url in urls:
            if urlparse(url).netloc.endswith(tuple(self._allowed_domain)):
                yield Request(url)
   
class MalformedURLException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
