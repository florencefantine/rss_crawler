from scrapy.item import Item, Field

# class RSSItem(Item):
#     id = Field()
#     name=Field()
#     description = Field()
#     pubDate = Field()
#     published = Field()
#     updated = Field()    
#     title = Field()
#     url = Field()
#     everything = Field()

class RssItem(Item):
    title = Field()# the Title of the feed
    link = Field()# the URL to the web site(not the feed)
    summary = Field();# short description of feed
    user_id = Field();

class RssFeedItem(RssItem):
    entries = Field();# will contain the RSSEntrItems
    url = Field()# the URL to the feed(not the web site)

class RssEntryItem(RssItem):
    published = Field()
    url = Field()
