# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel


class Author(BaseModel):
    id: Union[str, UUID] = uuid4()
    name: str


class Image(BaseModel):
    url: str
    title: Optional[str] = None
    link: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    description: Optional[str] = None
    type: Optional[str] = None
    length: Optional[int] = None


class Category(BaseModel):
    id: Union[str, UUID] = uuid4()
    name: str


class Article(BaseModel):
    id: Union[str, UUID] = uuid4()
    url: str  # link, guid
    title: str  # title
    summary: str  # description
    context: str  # description (complete raw text)
    rich_context: str  # description (complete HTML)
    author: Optional[List[Author]] = []  # author
    image: Optional[Image] = {}  # enclosure
    category: Optional[List[Category]] = []  # category
    timestamp: Optional[datetime] = None  # pubDate
    updated_at: Optional[datetime] = None
    third_party: Optional[str]  # source
    subtitle: Optional[str]
