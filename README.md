# `notion-df`: Seamlessly Connecting Notion Database with Pandas DataFrame

*Please Note: This project is currently in pre-alpha stage. The code are not appropriately documented and tested. Please report any issues you find.*

## Installation

```bash
pip install "git+https://github.com/lolipopshock/notion-df.git#egg=notion-df"
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
    df = notion_df.load(notion_database_url, api_key=api_key)
    # Equivalent to: df = pd.read_notion(notion_database_url, api_key=api_key)
    df.head()
    ```

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
    df = notion_df.load(notion_database_url)
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