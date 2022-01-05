# `notion-df`: Seamlessly Connecting Notion Database with Pandas DataFrame

*Please Note: This project is currently in pre-alpha stage. The code are not appropriately documented and tested. Please report any issues you find.*

## Installation

```bash
pip install "git+https://github.com/lolipopshock/notion-df.git#egg=notion-df"
```

## Usage

- Before starting, please follow the instructions to [create a new integration](https://www.notion.com/my-integrations) and [add it to your Notion page or database](https://developers.notion.com/docs/getting-started#step-2-share-a-database-with-your-integration). 
    - We'll refer `Internal Integration Token` as the `api_key` below.

- Download your Notion table as a pandas DataFrame
    ```python
    import notion_df
    df = notion_df.load(notion_database_url, api_key=api_key)
    df.head()
    ```

- Append a local `df` to a Notion database:

    ```python
    import notion_df
    notion_df.upload(df, notion_database_url, title="page-title", api_key=api_key)
    ```

- Upload a local `df` to a newly created database in a Notion page:
    
    ```python
    import notion_df
    notion_df.upload(df, notion_page_url, title="page-title", api_key=api_key)
    ```

- Tired of typing `api_key=api_key` each time?

    ```python
    import notion_df
    notion_df.config(api_key=api_key) # Or set an environment variable `NOTION_API_KEY`
    df = notion_df.load(notion_database_url)
    notion_df.upload(df, notion_page_url, title="page-title")
    ```

## TODOs

- [ ] Monkey patching Pandas such that we can use the same set of APIs with pandas. For example:
    ```python
    import pandas as pd 
    import notion_df
    notion_df.pandas()
    df = pd.load_notion(notion_database_url, api_key=api_key) # <- similar to many other pandas io apis like load_csv, load_excel, etc.
    df.to_notion(notion_database_url, api_key=api_key) # <- similar to many other pandas io apis like to_csv, to_excel, etc.
    ```
- [ ] Add tests for
    - [ ] `load` 
    - [ ] `upload` 
    - [ ] `values.py`
    - [ ] `configs.py`
    - [ ] `base.py`
- [ ] Better class organizations/namings for `*Configs` and `*Values`