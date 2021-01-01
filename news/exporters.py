from datetime import datetime
from email.utils import format_datetime

from scrapy.exporters import XmlItemExporter

VALID_RSS_ELEMENTS = {
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
    "item": {  # value: should this field be escaped
        "author": True,
        "category": True,
        "comments": True,
        "description": True,
        "enclosure": False,
        "guid": False,
        "link": False,
        "pubDate": False,
        "source": True,
        "title": True,
    },
}

# FIXME: guid isPermaLink attributes
# https://www.w3schools.com/xml/rss_tag_guid.asp

# FIXME: source url attributes
# https://www.w3schools.com/xml/rss_tag_source.asp

# FIXME: Add support for enclosure
# https://www.w3schools.com/xml/rss_tag_enclosure.asp


class RSSExporter(XmlItemExporter):
    def __init__(self, file, channel_meta, **kwargs):
        self.file = file
        self.channel_meta = channel_meta
        self.item_list = []
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
        # Didn't actually write to file, store to list and write after sorting
        self.item_list.append(item)

    def write_item(self, item):
        # Edit from `export_item` from `scrapy.exporters.XmlItemExporter`
        # Add indent depth from 2 to 3
        self._beautify_indent(depth=2)
        self.xg.startElement(self.item_element, {})
        self._beautify_newline()
        for name, value in self._get_serialized_fields(item, default_value=""):
            if name in VALID_RSS_ELEMENTS["item"]:
                # Cleanup data
                if isinstance(value, datetime):  # Format timestamp
                    value = format_datetime(value)
                elif value is None:  # Fill empty field with empty string
                    value = ""

                # Write to xml
                if VALID_RSS_ELEMENTS["item"][name]:  # should this field be escaped
                    self._export_xml_field(name, f"<![CDATA[{value}]]>", depth=3)
                else:
                    self._export_xml_field(name, value, depth=3)
        self._beautify_indent(depth=2)
        self.xg.endElement(self.item_element)
        self._beautify_newline(new_item=True)

    def finish_exporting(self):
        # Sort and write items
        self.item_list.sort(key=lambda x: x["pubDate"], reverse=True)
        for item in self.item_list:
            self.write_item(item)

        # channel tag
        self._beautify_indent(depth=1)
        self.xg.endElement(self.root_element)
        self._beautify_newline(new_item=True)
        # rss tag
        self.xg.endElement("rss")
        self.xg.endDocument()
