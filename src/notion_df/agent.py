from typing import List, Dict, Optional, Union, Tuple
from datetime import datetime
import warnings
import os
from functools import wraps

import pandas as pd
from httpx import HTTPStatusError
from notion_client import Client
from notion_client.helpers import get_id

from notion_df.values import PageProperties, PageProperty
from notion_df.configs import DatabaseSchema, NON_EDITABLE_TYPES
from notion_df.utils import is_uuid

API_KEY = None
NOT_REVERSE_DATAFRAME = -1
# whether to reverse the dataframe when performing uploading.
# for some reason, notion will reverse the order of dataframe
# when uploading.
# -1 for reversing, for not reversing
NOTION_DEFAULT_PAGE_SIZE = 100
NOTION_MAX_PAGE_SIZE = 100


def config(api_key: str):
    global API_KEY
    API_KEY = api_key


def _load_api_key(api_key: str) -> str:
    if api_key is not None:
        return api_key
    elif API_KEY is not None:
        return API_KEY
    elif os.environ.get("NOTION_API_KEY") is not None:
        return os.environ.get("NOTION_API_KEY")
    else:
        raise ValueError("No API key provided")


def _is_notion_database(notion_url):
    return "?v=" in notion_url.split("/")[-1]


def use_client(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        orig_client = client = kwargs.pop("client", None)

        if client is None:
            api_key = _load_api_key(kwargs.pop("api_key", None))
            client = Client(auth=api_key)
        out = func(client=client, *args, **kwargs)

        if orig_client is None:
            # Automatically close the client if it was not passed in
            client.close()
        return out

    return wrapper


def query_database(
    database_id: str,
    client: Client,
    start_cursor: Optional[str] = None,
    page_size: int = NOTION_DEFAULT_PAGE_SIZE,
):
    query_dict = {"database_id": database_id, "page_size": page_size}
    if start_cursor is not None:
        query_dict["start_cursor"] = start_cursor
        # For now, Notion API doesn't allow start_cursor='null'

    query_results = client.databases.query(**query_dict)

    assert query_results["object"] == "list"
    return query_results


def load_df_from_queries(
    database_query_results: List[Dict],
):
    properties = PageProperties.from_raw(database_query_results)
    df = properties.to_frame()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # TODO: figure out a better solution
        # When doing the following, Pandas may think you are trying
        # to add a new column to the dataframe; it will show the warnings,
        # but it will not actually add the column. So we use catch_warnings
        # to hide the warnings.
        # However this might not be the best way to do so. Some alternatives
        # include setting df.attrs https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.attrs.html
        # Or even use something like multi-level index for saving notion_ids.
        # Nevertheless, all of them seems not that perfect -- for example,
        # after copying or slicing, the values will disappear.
        # Should try to figure out a better solution in the future.
        df.notion_urls = pd.Series([ele["url"] for ele in database_query_results])
        df.notion_ids = pd.Series([ele["id"] for ele in database_query_results])
        df.notion_query_results = database_query_results
        # TODO: Rethink if this should be private

    return df


def download_df_from_database(
    notion_url: str,
    client: Client,
    nrows: Optional[int] = None,
    errors: str = "strict",
) -> pd.DataFrame:
    """Download a Notion database as a pandas DataFrame.

    Args:
        notion_url (str):
            The URL of the Notion database to download from.
        nrows (int, optional):
            Number of rows of file to read. Useful for reading
            pieces of large files.
        api_key (str, optional):
            The API key of the Notion integration.
            Defaults to None.
        client (Client, optional):
            The notion client.
            Defaults to None.
    Returns:
        pd.DataFrame: the loaded dataframe.
    """
    if not is_uuid(notion_url):
        assert _is_notion_database(notion_url)
        database_id = get_id(notion_url)
    else:
        database_id = notion_url

    # Check the if the id is a database first
    try:
        retrieve_results = client.databases.retrieve(database_id=database_id)
        schema = DatabaseSchema.from_raw(retrieve_results["properties"])
    except HTTPStatusError:
        error_msg = (
            f"The object {database_id} might not be a notion database, "
            "or integration associated with the API key don't have access "
            "to it."
        )
        if errors == "strict":
            raise ValueError(error_msg)
        elif errors == "warn":
            warnings.warn(error_msg)
            return None
        elif errors == "ignore":
            return None

    downloaded_rows = []

    page_size = NOTION_MAX_PAGE_SIZE
    if nrows is not None:
        if nrows <= NOTION_MAX_PAGE_SIZE:
            page_size = nrows

    query_results = query_database(database_id, client, page_size=page_size)
    downloaded_rows.extend(query_results["results"])

    while query_results["has_more"]:
        if nrows is not None:
            if len(downloaded_rows) >= nrows:
                break
            else:
                page_size = nrows - len(downloaded_rows)
        else:
            page_size = NOTION_MAX_PAGE_SIZE

        query_results = query_database(
            database_id,
            client,
            start_cursor=query_results["next_cursor"],
            page_size=page_size,
        )
        downloaded_rows.extend(query_results["results"])

    df = load_df_from_queries(downloaded_rows)
    df = schema.create_df(df)
    return df


@use_client
def download(
    notion_url: str,
    nrows: Optional[int] = None,
    resolve_relation_values: Optional[bool] = False,
    errors: str = "strict",
    *,
    api_key: str = None,
    client: Client = None,
):
    df = download_df_from_database(
        notion_url=notion_url,
        nrows=nrows,
        client=client,
        errors=errors,
    )
    if resolve_relation_values:
        for col in df.columns:
            if df.schema[col].type == "relation":
                relation_df = download_df_from_database(
                    df.schema[col].relation.database_id,
                    errors="warn",
                    client=client,
                )
                if relation_df is not None:
                    rel_title_col = relation_df.schema.title_column
                    obj_id_to_string = {
                        obj_id: obj_title
                        for obj_id, obj_title in zip(
                            relation_df.notion_ids, relation_df[rel_title_col]
                        )
                    }
                    df[col] = df[col].apply(
                        lambda row: [obj_id_to_string[ele] for ele in row]
                    )
    return df


def create_database(
    page_id: str, client: Client, schema: DatabaseSchema, title: str = ""
):
    response = client.databases.create(
        parent={"type": "page_id", "page_id": page_id},
        title=[{"type": "text", "text": {"content": title}}],
        properties=schema.query_dict(),
    )
    assert response["object"] == "database"
    return response


def upload_row_to_database(row, database_id, schema, client) -> Dict:

    properties = PageProperty.from_series(row, schema).query_dict()
    response = client.pages.create(
        parent={"database_id": database_id}, properties=properties
    )
    return response


def upload_to_database(df, databse_id, schema, client, errors) -> List[Dict]:
    all_response = []
    for _, row in df[::NOT_REVERSE_DATAFRAME].iterrows():
        try:
            response = upload_row_to_database(row, databse_id, schema, client)
            all_response.append(response)
        except Exception as e:
            if errors == "strict":
                raise e
            elif errors == "warn":
                warnings.warn(f"Encountered errors {e} while uploading row: {row}")
            elif errors == "ignore":
                continue
    return all_response[::NOT_REVERSE_DATAFRAME]


def load_database_schema(database_id, client):
    return DatabaseSchema.from_raw(
        client.databases.retrieve(database_id=database_id)["properties"]
    )


@use_client
def upload(
    df: pd.DataFrame,
    notion_url: str,
    schema: DatabaseSchema = None,
    mode: str = "a",
    title: str = "",
    title_col: str = "",
    errors: str = "strict",
    resolve_relation_values: bool = False,
    create_new_rows_in_relation_target: bool = False,
    return_response: bool = False,
    *,
    api_key: str = None,
    client: Client = None,
) -> Union[str, Tuple[str, List[Dict]]]:
    """Upload a dataframe to the specified Notion database.

    Args:
        df (pd.DataFrame):
            The dataframe to upload.
        notion_url (str):
            The URL of the Notion page to upload to.
            If it is a notion page, then it will create a new database
            under that page and upload the dataframe to it.
        schema (DatabaseSchema, optional):
            The schema of the Notion database.
            When not set, it will be inferred from (1) the target
            notion database (if it is) then (2) the dataframe itself.
        mode (str, optional):
            (the function is not supported yet.)
            Whether to append to the database or overwrite.
            Defaults to "a".
        title (str, optional):
            The title of the Notion database.
            Defaults to "".
        title_col (str, optional):
            Every Notion database requires a "title" column.
            When the schema is not set, by default it infers the first
            column of uploaded dataframe as the title column. You can
            set this value to specify the title column.
            Defaults to "".
        errors (str, optional):
            Since we upload the dataframe to Notion row by row, you
            can specify how to handle errors during uploading. There
            are several options:
                1. "strict": raise an error when there is one.
                2. "ignore": ignore errors and continue uploading
                    subsequent rows.
                3. "warn": print the error message and continue uploading
            Defaults to "strict".
        resolve_relation_values (bool, optional):
            If `True`, notion-df assumes the items in any relation columns
            are not notion object ids, but the value of the corresponding 
            "title column" in the target table. It will try to convert the 
            relation column to notion object ids by looking up the value. 
            Defaults to False.
        create_new_rows_in_relation_target (bool, optional):
            This argument is used in conjunction with `resolve_relation_values`.
            If True, then notion-df will try to create new rows in the target
            the relation table if the relation column value is not found there.
            Defaults to False.
        return_response (bool, optional):
            If True, then the function will return a list of responses for
            the updates from Notion.
        api_key (str, optional):
            The API key of the Notion integration.
            Defaults to None.
        client (Client, optional):
            The notion client.
            Defaults to None.
    """
    if schema is None:
        if hasattr(df, "schema"):
            schema = df.schema

    if not _is_notion_database(notion_url):
        if schema is None:
            schema = DatabaseSchema.from_df(df, title_col=title_col)
        database_properties = create_database(get_id(notion_url), client, schema, title)
        databse_id = database_properties["id"]
        notion_url = database_properties["url"]
    else:
        databse_id = get_id(notion_url)
        if schema is None:
            schema = load_database_schema(databse_id, client)

    # At this stage, we should have the appropriate schema
    assert schema is not None

    if not schema.is_df_compatible(df):
        raise ValueError(
            "The dataframe is not compatible with the database schema."
            "The df contains columns that are not in the databse: "
            + f"{[col for col in df.columns if col not in schema.configs.keys()]}"
        )

    if mode not in ("a", "append"):
        raise NotImplementedError
        # TODO: clean the current values in the notion database (if any)

    df = schema.transform(df, remove_non_editables=True)

    # Assumes the notion database is created and has the appropriate schema
    if resolve_relation_values:
        for col in df.columns:
            if schema[col].type == "relation":
                
                if df[col].apply(lambda row: all([is_uuid(ele) for ele in row])).all():
                    # The column is all in uuid, we don't need to resolve it 
                    continue 

                # Try to download the target_relation_df   
                relation_db_id = schema[col].relation.database_id
                relation_df = download_df_from_database(
                    relation_db_id,
                    errors="warn",
                    client=client,
                )

                if relation_df is not None:
                    rel_title_col = relation_df.schema.title_column
                    obj_string_to_id = {
                        obj_title: obj_id
                        for obj_id, obj_title in zip(
                            relation_df.notion_ids, relation_df[rel_title_col]
                        )
                    }

                    all_unique_obj_strings_in_relation_df = set(
                        relation_df[rel_title_col].tolist()
                    )
                    all_unique_obj_strings_in_df = set(sum(df[col].tolist(), []))
                    # This assumes the column has been transformed to a list of lists;
                    # which is a true assumption given the transformation for the relation
                    # column (LIST_TRANSFORM).
                    new_object_strings = all_unique_obj_strings_in_df.difference(
                        all_unique_obj_strings_in_relation_df
                    )

                    if create_new_rows_in_relation_target and len(new_object_strings) > 0:
                        new_relation_df = pd.DataFrame(
                            list(new_object_strings), columns=[rel_title_col]
                        )
                        responses = upload_to_database(
                            new_relation_df,
                            relation_db_id,
                            relation_df.schema,
                            client,
                            "warn",
                        )
                        appended_relation_df = load_df_from_queries(responses)
                        obj_string_to_id.update(
                            {
                                obj_title: obj_id
                                for obj_id, obj_title in zip(
                                    appended_relation_df.notion_ids,
                                    appended_relation_df[rel_title_col],
                                )
                            }
                        )

                    df[col] = df[col].apply(
                        lambda row: [obj_string_to_id[ele] for ele in row if ele in obj_string_to_id]
                    )

    response = upload_to_database(df, databse_id, schema, client, errors)

    print(f"Your dataframe has been uploaded to the Notion page: {notion_url} .")
    if return_response:
        return notion_url, response
    return notion_url
