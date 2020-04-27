from typing_extensions import TypedDict
from typing import Optional

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
