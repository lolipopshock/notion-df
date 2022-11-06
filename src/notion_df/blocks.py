from typing import List, Union, Dict, Any, Tuple, Optional
from pydantic import BaseModel, parse_obj_as, validator, root_validator

from notion_df.base import (
    RichTextObject,
    SelectOption,
    DateObject,
    RelationObject,
    UserObject,
    RollupObject,
    FileObject,
    FormulaObject,
    NotionExtendedColorEnum,
)


class ParentObject(BaseModel):
    type: str
    database_id: Optional[str]
    page_id: Optional[str]
    workspace: Optional[bool]
    block_id: Optional[str]


class BaseNotionBlock(BaseModel):
    object: str = "block"
    parent: ParentObject
    id: Optional[str]
    type: Optional[str]
    created_time: str
    # created_by
    last_edited_time: str
    # created_by
    has_children: bool
    archived: bool
    type: str

    @property
    def children(self):
        return self.__getattribute__(self.type).children

    def set_children(self, value: Any):
        self.__getattribute__(self.type).children = value


class BaseAttributeWithChildren(BaseModel):
    children: Optional[List["BaseNotionBlock"]]


class TextBlockAttributes(BaseAttributeWithChildren):
    rich_text: List[RichTextObject]
    color: Optional[NotionExtendedColorEnum]


class ToDoBlockAttribute(BaseAttributeWithChildren):
    rich_text: List[RichTextObject]
    color: Optional[NotionExtendedColorEnum]
    checked: Optional[bool]


class ParagraphBlock(BaseNotionBlock):
    type: str = "paragraph"
    paragraph: TextBlockAttributes


class BulletedListItemBlock(BaseNotionBlock):
    type: str = "bulleted_list_item"
    bulleted_list_item: TextBlockAttributes


class NumberedListItemBlock(BaseNotionBlock):
    type: str = "numbered_list_item"
    numbered_list_item: TextBlockAttributes


class ToDoBlock(BaseNotionBlock):
    type: str = "to_do"
    to_do: ToDoBlockAttribute


class ToggleBlock(BaseNotionBlock):
    type: str = "toggle"
    toggle: TextBlockAttributes


BLOCKS_MAPPING = {
    list(_cls.__fields__.keys())[-1]: _cls for _cls in BaseNotionBlock.__subclasses__()
}


def parse_block(data: Dict):
    return parse_obj_as(BLOCKS_MAPPING[data["type"]], data)
