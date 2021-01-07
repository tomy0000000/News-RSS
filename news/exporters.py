from datetime import datetime
from email.utils import format_datetime
from xml.sax.saxutils import escape

from scrapy.exporters import XmlItemExporter
from scrapy.utils.python import is_listlike

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
    "channel_image": [
        "description",
        "height",
        "link",
        "title",
        "url",
        "width",
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
            if field not in VALID_RSS_ELEMENTS["channel"]:
                continue
            if field == "image":
                image_value = {}
                if isinstance(value, dict):
                    for image_field in VALID_RSS_ELEMENTS["channel_image"]:
                        image_value[image_field] = value.get(image_field)
                elif isinstance(value, str):
                    image_value["url"] = value
                for image_field in VALID_RSS_ELEMENTS["channel_image"]:
                    if image_field not in image_value or not image_value[image_field]:
                        image_value[image_field] = self.channel_meta.get(image_field)
                value = image_value
            self._export_xml_field(field, value, depth=2)

    def export_item(self, item):
        # Didn't actually write to file, store to list and write after sorting
        self.item_list.append(item)

    def write_item(self, item):
        # Edit from `export_item` from `scrapy.exporters.XmlItemExporter`
        self._beautify_indent(depth=2)
        self.xg.startElement(self.item_element, {})
        self._beautify_newline()
        for name, value in self._get_serialized_fields(item, default_value=""):
            if name not in VALID_RSS_ELEMENTS["item"]:
                continue

            # Special handler for image
            if name == "enclosure":
                self._export_xml_field(name, None, depth=3, attributes=value)
                continue

            # Cleanup data
            if isinstance(value, datetime):  # Format timestamp
                value = format_datetime(value)
            elif value is None:  # Fill empty field with empty string
                value = ""

            # Write to xml
            self._export_xml_field(
                name,
                value,
                depth=3,
                escape_content=VALID_RSS_ELEMENTS["item"][name],
            )
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

    def _export_xml_field(
        self, name, serialized_value, depth, attributes=None, escape_content=False
    ):
        if attributes is None:
            attributes = {}
        self._beautify_indent(depth=depth)
        self.xg.startElement(name, attributes)
        if hasattr(serialized_value, "items"):
            self._beautify_newline()
            for subname, value in serialized_value.items():
                self._export_xml_field(subname, value, depth=depth + 1)
            self._beautify_indent(depth=depth)
        elif is_listlike(serialized_value):
            self._beautify_newline()
            for value in serialized_value:
                self._export_xml_field("value", value, depth=depth + 1)
            self._beautify_indent(depth=depth)
        elif serialized_value:  # Make sure content is not empty
            content = escape(str(serialized_value))
            if escape_content:
                self._xg_raw_characters(f"<![CDATA[{content}]]>")
            else:
                self._xg_raw_characters(content)
        self.xg.endElement(name)
        self._beautify_newline()

    def _xg_raw_characters(self, content):
        if content:
            self.xg._finish_pending_start_element()
            if not isinstance(content, str):
                content = str(content, self.xg._encoding)
            self.xg._write(content)
