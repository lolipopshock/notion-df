import os 
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