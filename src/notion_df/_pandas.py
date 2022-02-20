from typing import Optional
from notion_df import upload, download


def read_notion(
    notion_url: str,
    nrows: Optional[int] = None,
    resolve_relation_values: bool = False,
    errors: str = "strict",
    api_key: str = None,
) -> "pd.DataFrame":
    """Download a Notion database as a pandas DataFrame.

    Args:
        notion_url (str):
            The URL of the Notion database to download from.
        nrows (int, optional):
            Number of rows of file to read. Useful for reading
            pieces of large files.
        resolve_relation_values (bool, optional):
            By default, when downloading relation columns, notion-df
            will just download the object ids. If set `resolve_relation_values`
            to `True`, notion-df will try to pull the values of the title 
            column from the target table and map the object ids to those values.
            Defaults to False.  
        errors (str, optional):
            You can specify how to handle errors during downloading. There
            are several options:
                1. "strict": raise an error when there is one.
                2. "ignore": ignore errors.
                3. "warn": print the error message.
            Defaults to "strict".
        api_key (str, optional):
            The API key of the Notion integration.
            Defaults to None.
    Returns:
        pd.DataFrame: the loaded dataframe.
    """
    return download(
        notion_url,
        nrows=nrows,
        resolve_relation_values=resolve_relation_values,
        errors=errors,
        api_key=api_key,
    )


def to_notion(
    self,
    notion_url: str,
    schema=None,
    mode: str = "a",
    title: str = "",
    title_col: str = "",
    errors: str = "strict",
    resolve_relation_values: bool = False,
    create_new_rows_in_relation_target: bool = False,
    return_response: bool = False,
    api_key: str = None,
):

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
    """

    return upload(
        df=self,
        notion_url=notion_url,
        schema=schema,
        mode=mode,
        title=title,
        title_col=title_col,
        errors=errors,
        resolve_relation_values=resolve_relation_values,
        create_new_rows_in_relation_target=create_new_rows_in_relation_target,
        return_response=return_response,
        api_key=api_key,
    )


def pandas():
    import pandas as pd

    pd.read_notion = read_notion
    pd.DataFrame.to_notion = to_notion
