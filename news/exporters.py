from scrapy.exporters import XmlItemExporter


VALID_RSS_ELEMENT = {
    "channel": [
        "category",
        "cloud",
        "copyright",
        "description",
        "docs",
        "generator",
        "image",
        "language",
        "lastBuildDate",
        "link",
        "managingEditor",
        "pubDate",
        "rating",
        "skipDays",
        "skipHours",
        "textInput",
        "title",
        "ttl",
        "webMaster",
    ],
    "item": [
        "author",
        "category",
        "comments",
        "description",
        "enclosure",
        "guid",
        "link",
        "pubDate",
        "source",
        "title",
    ],
}


class RSSExporter(XmlItemExporter):
    def __init__(self, file, channel_meta, **kwargs):
        self.file = file
        self.channel_meta = channel_meta
        super().__init__(file, root_element="channel", **kwargs)

    def start_exporting(self):
        self.xg.startDocument()
        # rss tag
        self.xg.startElement("rss", {"version": "2.0"})
        self._beautify_newline(new_item=True)
        # channel tag
        self._beautify_indent(depth=1)
        self.xg.startElement(self.root_element, {})
        self._beautify_newline(new_item=True)

        # Inject channel metadata
        for field, value in self.channel_meta.items():
            self._export_xml_field(field, value, depth=2)

    def export_item(self, item):
        # Same as the parent class, just modifying indent depth to 2
        self._beautify_indent(depth=2)
        self.xg.startElement(self.item_element, {})
        self._beautify_newline()
        for name, value in self._get_serialized_fields(item, default_value=""):
            if name in VALID_RSS_ELEMENT["item"]:
                self._export_xml_field(name, value, depth=3)
        self._beautify_indent(depth=2)
        self.xg.endElement(self.item_element)
        self._beautify_newline(new_item=True)

    def finish_exporting(self):
        # channel tag
        self._beautify_indent(depth=1)
        self.xg.endElement(self.root_element)
        self._beautify_newline(new_item=True)
        # rss tag
        self.xg.endElement("rss")
        self.xg.endDocument()
