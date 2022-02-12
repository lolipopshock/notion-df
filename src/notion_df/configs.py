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

from notion_df.base import (
    SelectOptions,
    NumberFormat,
    RollupProperty,
    FormulaProperty,
    RelationProperty,
)
from notion_df.utils import (
    flatten_dict,
    IDENTITY_TRANSFORM,
    REMOVE_EMPTY_STR_TRANSFORM,
    SECURE_STR_TRANSFORM,
    SECURE_BOOL_TRANSFORM,
    SECURE_TIME_TRANSFORM,
    LIST_TRANSFORM,
)


class BasePropertyConfig(BaseModel):
    id: Optional[str]
    type: Optional[str]

    def query_dict(self):
        return flatten_dict(self.dict())

    @validator("type", always=True)
    def automatically_set_type_value(cls, v):
        _type = list(cls.__fields__.keys())[-1]
        if v is None:
            return _type
        else:
            assert _type == v, f"{_type} != {v}"
            return _type


class TitleConfig(BasePropertyConfig):
    title: Dict = {}

    # TODO: Make the validator automatically geneerated
    @validator("title")
    def title_is_empty_dict(cls, v):
        if v:
            raise ValueError("The title dict must be empty")
        return v


class RichTextConfig(BasePropertyConfig):
    rich_text: Dict = {}

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
    date: Dict = {}

    @validator("date")
    def title_is_empty_dict(cls, v):
        if v:
            raise ValueError("The date dict must be empty")
        return v


class PeopleConfig(BasePropertyConfig):
    people: Dict = {}

    @validator("people")
    def title_is_empty_dict(cls, v):
        if v:
            raise ValueError("The people dict must be empty")
        return v


class FilesConfig(BasePropertyConfig):
    files: Dict = {}

    @validator("files")
    def title_is_empty_dict(cls, v):
        if v:
            raise ValueError("The files dict must be empty")
        return v


class CheckboxConfig(BasePropertyConfig):
    checkbox: Dict = {}

    @validator("checkbox")
    def title_is_empty_dict(cls, v):
        if v:
            raise ValueError("The checkbox dict must be empty")
        return v


class URLConfig(BasePropertyConfig):
    url: Dict = {}

    @validator("url")
    def title_is_empty_dict(cls, v):
        if v:
            raise ValueError("The url dict must be empty")
        return v


class EmailConfig(BasePropertyConfig):
    email: Dict = {}

    @validator("email")
    def title_is_empty_dict(cls, v):
        if v:
            raise ValueError("The email dict must be empty")
        return v


class PhoneNumberConfig(BasePropertyConfig):
    phone_number: Dict = {}

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
    rollup: RollupProperty


class CreatedTimeConfig(BasePropertyConfig):
    created_time: Dict = {}

    @validator("created_time")
    def title_is_empty_dict(cls, v):
        if v:
            raise ValueError("The created_time dict must be empty")
        return v


class CreatedByConfig(BasePropertyConfig):
    created_by: Dict = {}

    @validator("created_by")
    def title_is_empty_dict(cls, v):
        if v:
            raise ValueError("The created_by dict must be empty")
        return v


class LastEditedTimeConfig(BasePropertyConfig):
    last_edited_time: Dict = {}

    @validator("last_edited_time")
    def title_is_empty_dict(cls, v):
        if v:
            raise ValueError("The last_edited_time dict must be empty")
        return v


class LastEditedByConfig(BasePropertyConfig):
    last_edited_by: Dict = {}

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

NON_EDITABLE_TYPES = [
    "formula",  # TODO: Double check for this
    "files",  # According to https://developers.notion.com/reference/file-object#externally-hosted-files-vs-files-hosted-by-notion
    "created_time",
    "created_by",
    "last_edited_time",
    "last_edited_by",
    "rollup",
]


def parse_single_config(data: Dict) -> BasePropertyConfig:
    return parse_obj_as(CONFIGS_MAPPING[data["type"]], data)


CONFIGS_DF_TRANSFORMER = {
    "title": SECURE_STR_TRANSFORM,
    "rich_text": SECURE_STR_TRANSFORM,
    "number": None,
    "select": REMOVE_EMPTY_STR_TRANSFORM,
    "multi_select": lambda lst: [str(ele) for ele in lst]
    if is_list_like(lst)
    else str(lst),
    "date": SECURE_TIME_TRANSFORM,
    "checkbox": SECURE_BOOL_TRANSFORM,
    ### Notion-specific Properties ###
    # Currently we don't automatically convert these properties
    # We assume the users will use the correct type and we don't need to perform any transformation
    "people": IDENTITY_TRANSFORM,
    "relation": LIST_TRANSFORM,
    "url": REMOVE_EMPTY_STR_TRANSFORM,
    "email": REMOVE_EMPTY_STR_TRANSFORM,
    ### TODO: check the following ###
    "files": SECURE_STR_TRANSFORM,
    "phone_number": SECURE_STR_TRANSFORM,
    "formula": SECURE_STR_TRANSFORM,
    "rollup": SECURE_STR_TRANSFORM,
    "created_time": SECURE_STR_TRANSFORM,
    "created_by": SECURE_STR_TRANSFORM,
    "last_edited_time": SECURE_STR_TRANSFORM,
    "last_edited_by": SECURE_STR_TRANSFORM,
}


def _infer_series_config(column: "pd.Series") -> BasePropertyConfig:
    dtype = column.dtype

    if is_object_dtype(dtype):
        if all(is_list_like(ele) for ele in column):
            all_possible_values = set(
                list(itertools.chain.from_iterable(column.to_list()))
            )
            all_possible_values = [str(ele) for ele in all_possible_values]
            return MultiSelectConfig(
                multi_select=SelectOptions.from_value(all_possible_values),
            )
        else:
            return RichTextConfig()
    if is_numeric_dtype(dtype):
        return NumberConfig(number=NumberFormat(format="number"))
    if is_bool_dtype(dtype):
        return CheckboxConfig()
    if is_categorical_dtype(dtype):
        return SelectConfig(
            select=SelectOptions.from_value([str for cat in dtype.categories]),
        )
    if is_datetime64_any_dtype(dtype):
        return DateConfig()

    return None


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

    @classmethod
    def from_df(
        cls, df: "pd.DataFrame", title_col: Optional[str] = None
    ) -> "DatabaseSchema":
        """Automatically infer the schema from a pandas dataframe"""
        df = df.infer_objects()

        configs = {}
        for col in df.columns:
            config = _infer_series_config(df[col])
            configs[col] = config

        if title_col is not None:
            configs[title_col] = TitleConfig()
        else:
            configs[df.columns[0]] = TitleConfig()

        return cls(configs)

    @property
    def title_column(self) -> Optional[str]:
        for key, config in self.configs.items():
            if isinstance(config, TitleConfig) or config.type == "title":
                # TODO: Rethink this
                return key

    def create_df(self, df) -> "pd.DataFrame":
        
        notion_urls = df.notion_urls
        notion_ids = df.notion_ids
        notion_query_results = df.notion_query_results

        df = df.copy()
        # Ensure the column integrity
        # See the issue mentioned in https://github.com/lolipopshock/notion-df/issues/17
        columns = [col for col in df.columns if col in self.configs]
        df = df[columns]
        
        df.schema = self
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df.notion_urls = notion_urls
            df.notion_ids = notion_ids
            df.notion_query_results = notion_query_results

        return df

    def is_df_compatible(self, df: "pd.DataFrame") -> bool:
        """Validate the dataframe against the schema"""

        if hasattr(df, "schema"):
            if not df.schema == self:
                return False

            # TODO: There might miss one thing: if the rollup is not configured
            # the database reterive result will be empty for that column.
            # But the database query will return the value for that column
            # (even if that's empty). So this would miss this check...
        else:
            for col in df.columns:
                if col not in self.configs.keys():
                    return False

        # TODO: Add more advanced check on datatypes
        return True

    def transform(
        self, df: "pd.DataFrame", remove_non_editables=False
    ) -> "pd.DataFrame":
        """Transform the df such that the data values are compatible with the schema.
        It assumes the df has already been validated against the schema.
        """
        df = df.copy()
        used_columns = []
        for col in df.columns:
            if self[col].type in NON_EDITABLE_TYPES:
                continue  # Skip non-editable columns

            transform = CONFIGS_DF_TRANSFORMER[self[col].type]
            if transform is not None:
                df[col] = df[col].apply(transform)
            used_columns.append(col)
        if remove_non_editables:
            return df[used_columns]
        return df
