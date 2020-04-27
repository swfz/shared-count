from typing_extensions import TypedDict
from typing import Optional, List, Union

class Pocket(TypedDict):
    url: str
    count: str

class Engagement(TypedDict):
    count: int
    social_sentence: str


class OgObject(TypedDict):
    engagement: Engagement
    id: str


class Facebook(TypedDict):
    og_object: Optional[OgObject]
    id: str


class Bookmark(TypedDict):
    comment: str
    user: str
    tags: List[str]
    timestamp: str


class Hatena(TypedDict):
    eid: str
    count: str
    screenshot: str
    url: str
    title: str
    entry_url: str
    bookmarks: List[Bookmark]
    requested_url: str


class Star(TypedDict):
    name: str
    quote: str


class Entry(TypedDict):
    uri: str
    can_comment: int
    stars: List[Star]
    colored_stars: List[Star]


class HatenaStar(TypedDict):
    can_comment: int
    entries: List[Entry]


class Twitter(TypedDict):
    url: str
    count: int
    likes: int


