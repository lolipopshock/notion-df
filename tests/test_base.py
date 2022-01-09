import pytest
import notion_df
import pandas as pd
from pydantic import ValidationError

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