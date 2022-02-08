import os
import pytest
from notion_df.agent import download

NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
NOTION_LARGE_DF = os.environ.get("NOTION_LARGE_DF")
NOTION_LARGE_DF_ROWS = 150

def test_nrows():
    if not NOTION_LARGE_DF or not NOTION_API_KEY:
        pytest.skip("API key not provided")

    df = download(NOTION_LARGE_DF, api_key=NOTION_API_KEY)
    assert len(df) == NOTION_LARGE_DF_ROWS

    df = download(NOTION_LARGE_DF, nrows=101, api_key=NOTION_API_KEY)
    assert len(df) == 101

    df = download(NOTION_LARGE_DF, nrows=15, api_key=NOTION_API_KEY)
    assert len(df) == 15