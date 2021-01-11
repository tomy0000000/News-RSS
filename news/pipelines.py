from news.exporters import RSSExporter

ITEM_TO_RSS_MAPPING = {
    "url": ["link", "guid"],
    "rich_context": ["description"],
    "image": ["enclosure"],
    "timestamp": ["pubDate"],
    "third_party": ["source"],
}


def extend_to_rss_field(item):
    new_fields = {}
    for field, value in item.items():
        if field in ITEM_TO_RSS_MAPPING:
            for rss_field in ITEM_TO_RSS_MAPPING[field]:
                new_fields[rss_field] = value
    item.update(new_fields)
    return item


class NewsPipeline:
    def open_spider(self, spider):
        self.file = open(f"{spider.file_name}.xml", "wb")
        self.exporter = RSSExporter(self.file, spider.metadata, indent=2)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        item = extend_to_rss_field(item)
        self.exporter.export_item(item)
        return item
