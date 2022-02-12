import os
import random
import pytest
import notion_df
import pandas as pd
from pydantic import ValidationError
from notion_df.agent import download, upload

NOTION_API_KEY = os.environ.get("NOTION_API_KEY")


def test_select_option():
    schema = notion_df.configs.DatabaseSchema(
        {"options": notion_df.configs.MultiSelectConfig()}
    )

    df = pd.DataFrame([{"options": [1, 2, 3]}])
    dff = schema.transform(df)
    notion_df.values.PageProperty.from_series(dff.iloc[0], schema)

    # Not working because of commas in the option string
    df = pd.DataFrame([{"options": ["a,b", "c,d"]}])
    dff = schema.transform(df)
    with pytest.raises(ValidationError):
        notion_df.values.PageProperty.from_series(dff.iloc[0], schema)

    # The following also checks whether it can convert elements into strings
    df = pd.DataFrame([{"options": [[1, 2, 3], [4, 5, 6]]}])
    dff = schema.transform(df)
    with pytest.raises(ValidationError):
        notion_df.values.PageProperty.from_series(dff.iloc[0], schema)


def test_rollup():
    NOTION_ROLLUP_DF = os.environ.get("NOTION_ROLLUP_DF")

    if not NOTION_ROLLUP_DF or not NOTION_API_KEY:
        pytest.skip("API key not provided")

    # Ensure the rollup values can be downloaded and uploaded
    df = download(NOTION_ROLLUP_DF, api_key=NOTION_API_KEY)
    upload(df[:2], NOTION_ROLLUP_DF, api_key=NOTION_API_KEY)
    # TODO: Add remove rollup values


def test_files_edit_by():
    NOTION_FILES_DF = os.environ.get("NOTION_FILES_DF")

    if not NOTION_FILES_DF or not NOTION_API_KEY:
        pytest.skip("API key not provided")

    df = download(NOTION_FILES_DF, api_key=NOTION_API_KEY)


def test_formula():
    NOTION_FORMULA_DF = os.environ.get("NOTION_FORMULA_DF")

    if not NOTION_FORMULA_DF or not NOTION_API_KEY:
        pytest.skip("API key not provided")

    df = download(NOTION_FORMULA_DF, api_key=NOTION_API_KEY)


def test_relation():
    NOTION_RELATION_DF = os.environ.get("NOTION_RELATION_DF")
    NOTION_RELATION_TARGET_DF = os.environ.get("NOTION_RELATION_TARGET_DF")

    if not NOTION_RELATION_DF or not NOTION_RELATION_TARGET_DF or not NOTION_API_KEY:
        pytest.skip("API key not provided")

    # download: resolve
    # upload: resolve
    df = download(
        NOTION_RELATION_DF, api_key=NOTION_API_KEY, resolve_relation_values=True
    )
    df_target = download(NOTION_RELATION_TARGET_DF, api_key=NOTION_API_KEY)

    assert "private_page" not in df.columns
    # See https://github.com/lolipopshock/notion-df/issues/17

    ## witout a new key
    upload(
        df[:1],
        NOTION_RELATION_DF,
        resolve_relation_values=True,
        create_new_rows_in_relation_target=True,
    )
    df_target_new = download(NOTION_RELATION_TARGET_DF, api_key=NOTION_API_KEY)
    assert len(df_target_new) == len(df_target)

    ## with a new key
    rint = random.randint(0, 100000)
    df.at[0, "Related to Tasks"] = [f"test {rint}"]
    upload(
        df[:1],
        NOTION_RELATION_DF,
        resolve_relation_values=True,
        create_new_rows_in_relation_target=True,
    )
    df_target_new = download(NOTION_RELATION_TARGET_DF, api_key=NOTION_API_KEY)
    assert len(df_target_new) == len(df_target) + 1
    df_target_new.iloc[-1]["name"] == f"test {rint}"

    # download: not-resolve
    # upload: resolve
    # Avoids creating new rows for uuid only lists
    df = download(
        NOTION_RELATION_DF, api_key=NOTION_API_KEY, resolve_relation_values=False
    )
    df_target = download(NOTION_RELATION_TARGET_DF, api_key=NOTION_API_KEY)

    upload(
        df[:1],
        NOTION_RELATION_DF,
        resolve_relation_values=True,
        create_new_rows_in_relation_target=True,
    )
    df_target_new = download(NOTION_RELATION_TARGET_DF, api_key=NOTION_API_KEY)
    assert len(df_target_new) == len(df_target)

    # download: resolve
    # upload: not-resolve
    # Raises error
    df = download(
        NOTION_RELATION_DF, api_key=NOTION_API_KEY, resolve_relation_values=True
    )

    with pytest.raises(ValidationError):
        upload(
            df[:1],
            NOTION_RELATION_DF,
            resolve_relation_values=False,
        )
