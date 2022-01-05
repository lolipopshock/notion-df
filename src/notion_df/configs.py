from typing import List, Dict, Optional, Callable, Tuple
import warnings
import itertools
from dataclasses import dataclass

from pydantic import BaseModel, validator, parse_obj_as
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
    is_bool_dtype,
    is_categorical_dtype,
    is_list_like,
)

from notion_df.base import SelectOptions, NumberFormat, RollUpProperty, FormulaProperty, RelationProperty
from notion_df.utils import flatten_dict, ISO8601_STRFTIME_TRANSFORMER


class BasePropertyConfig(BaseModel):
    id: Optional[str]
    type: Optional[str]

    def query_dict(self):
        return flatten_dict(self.dict())


class TitleConfig(BasePropertyConfig):
    title: Dict

    # TODO: Make the validator automatically geneerated
    @validator("title")
    def title_is_empty_dict(cls, v):
        if v:
            raise ValueError("The title dict must be empty")
        return v


class RichTextConfig(BasePropertyConfig):
    rich_text: Dict

    @validator("rich_text")
    def title_is_empty_dict(cls, v):
        if v:
            raise ValueError("The rich_text dict must be empty")
        return v


class NumberConfig(BasePropertyConfig):
    number: NumberFormat

    # TODO:Add enum based on https://developers.notion.com/reference/create-a-database#number-configuration


class SelectConfig(BasePropertyConfig):
    select: Optional[SelectOptions]


class MultiSelectConfig(BasePropertyConfig):
    multi_select: Optional[SelectOptions]


class DateConfig(BasePropertyConfig):
    date: Dict

    @validator("date")
    def title_is_empty_dict(cls, v):
        if v:
            raise ValueError("The date dict must be empty")
        return v


class PeopleConfig(BasePropertyConfig):
    people: Dict

    @validator("people")
    def title_is_empty_dict(cls, v):
        if v:
            raise ValueError("The people dict must be empty")
        return v


class FilesConfig(BasePropertyConfig):
    files: Dict

    @validator("files")
    def title_is_empty_dict(cls, v):
        if v:
            raise ValueError("The files dict must be empty")
        return v


class CheckboxConfig(BasePropertyConfig):
    checkbox: Dict

    @validator("checkbox")
    def title_is_empty_dict(cls, v):
        if v:
            raise ValueError("The checkbox dict must be empty")
        return v


class URLConfig(BasePropertyConfig):
    url: Dict

    @validator("url")
    def title_is_empty_dict(cls, v):
        if v:
            raise ValueError("The url dict must be empty")
        return v


class EmailConfig(BasePropertyConfig):
    email: Dict

    @validator("email")
    def title_is_empty_dict(cls, v):
        if v:
            raise ValueError("The email dict must be empty")
        return v


class PhoneNumberConfig(BasePropertyConfig):
    phone_number: Dict

    @validator("phone_number")
    def title_is_empty_dict(cls, v):
        if v:
            raise ValueError("The phone_number dict must be empty")
        return v


class FormulaConfig(BasePropertyConfig):
    formula: FormulaProperty


class RelationConfig(BasePropertyConfig):
    relation: RelationProperty


class RollupConfig(BasePropertyConfig):
    roll_up: RollUpProperty


class CreatedTimeConfig(BasePropertyConfig):
    created_time: Dict

    @validator("created_time")
    def title_is_empty_dict(cls, v):
        if v:
            raise ValueError("The created_time dict must be empty")
        return v


class CreatedByConfig(BasePropertyConfig):
    created_by: Dict

    @validator("created_by")
    def title_is_empty_dict(cls, v):
        if v:
            raise ValueError("The created_by dict must be empty")
        return v


class LastEditedTimeConfig(BasePropertyConfig):
    last_edited_time: Dict

    @validator("last_edited_time")
    def title_is_empty_dict(cls, v):
        if v:
            raise ValueError("The last_edited_time dict must be empty")
        return v


class LastEditedByConfig(BasePropertyConfig):
    last_edited_by: Dict

    @validator("last_edited_by")
    def title_is_empty_dict(cls, v):
        if v:
            raise ValueError("The last_edited_by dict must be empty")
        return v


def _convert_classname_to_typename(s):
    import re

    s = s.replace("Config", "").replace("URL", "Url")
    return re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()


CONFIGS_MAPPING = {
    _convert_classname_to_typename(_cls.__name__): _cls
    for _cls in BasePropertyConfig.__subclasses__()
}


def parse_single_config(data: Dict) -> BasePropertyConfig:
    return parse_obj_as(CONFIGS_MAPPING[data["type"]], data)


@dataclass
class DatabaseSchema:

    configs: Dict[str, BasePropertyConfig]

    @classmethod
    def from_raw(cls, configs: Dict) -> "DatabaseSchema":

        configs = {key: parse_single_config(config) for key, config in configs.items()}
        return cls(configs)

    def __getitem__(self, key: int):
        return self.configs[key]

    def query_dict(self) -> Dict:
        return {key: config.query_dict() for key, config in self.configs.items()}


def guess_column_dtype(
    column: "pd.Series", column_index: int
) -> Optional[Tuple[BasePropertyConfig, Optional[Callable]]]:

    if column_index == 0:
        # By default, the first column is the title
        return TitleConfig(type="title", title={}), str

    dtype = column.dtype

    if is_object_dtype(dtype):
        if all(is_list_like(ele) for ele in column):
            all_possible_values = set(
                list(itertools.chain.from_iterable(column.to_list()))
            )
            all_possible_values = [str(ele) for ele in all_possible_values]
            return (
                MultiSelectConfig(
                    type="multi_select",
                    multi_select=SelectOptions.from_value(all_possible_values),
                ),
                lambda lst: [str(ele) for ele in lst],
            )
        else:
            return RichTextConfig(type="rich_text", rich_text={}), str
    if is_numeric_dtype(dtype):
        return NumberConfig(type="number", number=NumberFormat(format="number")), None
    if is_bool_dtype(dtype):
        return CheckboxConfig(type="checkbox", checkbox={}), None
    if is_categorical_dtype(dtype):
        return (
            SelectConfig(
                type="select",
                select=SelectOptions.from_value([str for cat in dtype.categories]),
            ),
            lambda ele: str(ele),
        )
    if is_datetime64_any_dtype(dtype):
        return DateConfig(type="date", date={}), ISO8601_STRFTIME_TRANSFORMER

    return None, None


def guess_align_schema_for_df(
    df: "pd.DataFrame",
) -> Tuple["pd.DataFrame", DatabaseSchema]:
    # TODO: rethink how to wrap the "align" part: whether
    # it should be implemented when actually uploading the data?

    df = df.infer_objects().reset_index()

    configs = {}
    for idx, col in enumerate(df.columns):
        config, transformer = guess_column_dtype(df[col], idx)

        if config is None:
            warnings.warn(
                f"Column {col} is not recognized as a column type that can be uploaded to notion."
            )
            continue

        configs[col] = config
        if transformer is not None:
            df[col] = df[col].apply(transformer)

    return df, DatabaseSchema(configs)
