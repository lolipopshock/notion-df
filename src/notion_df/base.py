from typing import List, Dict, Optional
import re
from enum import Enum
from pydantic import BaseModel, validator

### All colors supported in NOTION

ISO8601_REGEX = r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
# See https://stackoverflow.com/questions/41129921/validate-an-iso-8601-datetime-string-in-python


class NotionColorEnum(str, Enum):
    Default = "default"
    Gray = "gray"
    Brown = "brown"
    Orange = "orange"
    Yellow = "yellow"
    Green = "green"
    Blue = "blue"
    Purple = "purple"
    Pink = "pink"
    Red = "red"


class NotionExtendedColorEnum(str, Enum):
    Default = "default"
    Gray = "gray"
    Brown = "brown"
    Orange = "orange"
    Yellow = "yellow"
    Green = "green"
    Blue = "blue"
    Purple = "purple"
    Pink = "pink"
    Red = "red"
    GrayBackground = "gray_background"
    BrownBackground = "brown_background"
    OrangeBackground = "orange_background"
    YellowBackground = "yellow_background"
    GreenBackground = "green_background"
    BlueBackground = "blue_background"
    PurpleBackground = "purple_background"
    PinkBackground = "pink_background"
    RedBackground = "red_background"


class RichTextTypeEnum(str, Enum):
    Text = "text"
    Mention = "mention"
    Equation = "equation"


class Annotation(BaseModel):
    bold: bool
    italic: bool
    strikethrough: bool
    underline: bool
    code: bool
    color: NotionExtendedColorEnum


class BaseRichText(BaseModel):
    plain_text: Optional[str]
    # TODO: The Optional[plain_text] is used when creating property values
    href: Optional[str] = None
    annotations: Optional[Annotation] = None
    type: Optional[RichTextTypeEnum]


class Link(BaseModel):
    type: str
    url: str


class Text(BaseModel):
    content: str
    link: Optional[Link]


class RichText(BaseRichText):
    text: Text

    @classmethod
    def from_value(cls, value: str):
        return cls(text=Text(content=value))


class Mention(BaseModel):
    pass  # TODO


class SelectOption(BaseModel):
    id: Optional[str]
    name: str
    color: Optional[NotionColorEnum]

    @classmethod
    def from_value(cls, value: str):
        return cls(name=value)


class SelectOptions(BaseModel):
    options: Optional[List[SelectOption]]

    @classmethod
    def from_value(cls, values: List[str]):
        return cls(options=[SelectOption.from_value(value) for value in values])


class NumberFormat(BaseModel):
    format: str


class RollUpProperty(BaseModel):
    relation_property_name: Optional[str]
    relation_property_id: Optional[str]
    rollup_property_name: Optional[str]
    rollup_property_id: Optional[str]
    function: str
    # TODO: Change this to ENUM https://developers.notion.com/reference/create-a-database#rollup-configuration

class FormulaProperty(BaseModel):
    expression: str


class RelationProperty(BaseModel):
    database_id: str
    # TODO: Change this to UUID validation

class Date(BaseModel):
    start: str
    end: Optional[str] = None
    time_zone: Optional[str] = None

    @validator("start")
    def title_is_empty_dict(cls, v):
        if re.match(ISO8601_REGEX, v) is None:
            raise ValueError(
                "The data start is not appropriately formatted as an ISO 8601 date string."
            )
        return v

    @validator("end")
    def title_is_empty_dict(cls, v):
        if v is not None:
            if re.match(ISO8601_REGEX, v) is None:
                raise ValueError(
                    "The data end is not appropriately formatted as an ISO 8601 date string."
                )
        return v

    @classmethod
    def from_value(cls, value: str):
        return cls(start=value)
        # TODO: Now we assume the value has already been formated as strings
        # But we should parse them into appropriate formats.
