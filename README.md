# `notion-df`: Seamlessly Connecting Notion Database with Pandas DataFrame

*Please Note: This project is currently in pre-alpha stage. The code are not appropriately documented and tested. Please report any issues you find.*

## Installation

```bash
git clone https://github.com/lolipopshock/notion-df && cd notion-df
pip install -e .
```

## Usage

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
    notion_df.config(api_key=api_key)
    ```