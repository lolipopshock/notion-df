# `notion-df`: Seamlessly Connecting Notion Database with Pandas DataFrame

*Please Note: This project is currently in pre-alpha stage. The code are not appropriately documented and tested. Please report any issues you find.*

## Installation

```bash
pip install notion-df
```

## Usage

- Before starting, please follow the instructions to [create a new integration](https://www.notion.com/my-integrations) and [add it to your Notion page or database](https://developers.notion.com/docs/getting-started#step-2-share-a-database-with-your-integration). 
    - We'll refer `Internal Integration Token` as the `api_key` below.

- Pandas-flavored APIs: Just need to add two additional lines of code:
    ```python
    import notion_df
    notion_df.pandas() #That's it!

    import pandas as pd
    df = pd.read_notion(page_url, api_key=api_key)
    df.to_notion(page_url)
    ```

- Download your Notion table as a pandas DataFrame
    ```python
    import notion_df
    df = notion_df.download(notion_database_url, api_key=api_key)
    # Equivalent to: df = pd.read_notion(notion_database_url, api_key=api_key)
    df.head()
    ```
    <details>
    <summary>Only downloading the first `nrows` from a database</summary>
    
    ```python
    df = notion_df.download(notion_database_url, nrows=nrows) #e.g., 10
    ```

    </details>
    
    <details>
    <summary>What if your table has a relation column?</summary>
    
    ```python
    df = notion_df.download(notion_database_url, 
                            resolve_relation_values=True)
    ```
    The `resolve_relation_values=True` will automatically resolve the linking for all the relation columns whose target can be accessed by the current notion integration.

    In details, let's say the `"test"` column in df is a relation column in Notion. 
    1. When `resolve_relation_values=False`, the return results for that column will be a list of UUIDs of the target page: `['65e04f11-xxxx', 'b0ffcb4b-xxxx', ]`. 
    2.  When `resolve_relation_values=True`, the return results for that column will be a list of regular strings corresponding to the name column of the target pages: `['page1', 'page2', ]`. 

    </details>

- Append a local `df` to a Notion database:

    ```python
    import notion_df
    notion_df.upload(df, notion_database_url, title="page-title", api_key=api_key)
    # Equivalent to: df.to_notion(notion_database_url, title="page-title", api_key=api_key)
    ```

- Upload a local `df` to a newly created database in a Notion page:
    
    ```python
    import notion_df
    notion_df.upload(df, notion_page_url, title="page-title", api_key=api_key)
    # Equivalent to: df.to_notion(notion_page_url, title="page-title", api_key=api_key)
    ```

- Tired of typing `api_key=api_key` each time?

    ```python
    import notion_df
    notion_df.config(api_key=api_key) # Or set an environment variable `NOTION_API_KEY`
    df = notion_df.download(notion_database_url)
    notion_df.upload(df, notion_page_url, title="page-title")
    # Similarly in pandas APIs: df.to_notion(notion_page_url, title="page-title")
    ```

## TODOs

- [ ] Add tests for
    - [ ] `load` 
    - [ ] `upload` 
    - [ ] `values.py`
    - [ ] `configs.py`
    - [ ] `base.py`
- [ ] Better class organizations/namings for `*Configs` and `*Values`