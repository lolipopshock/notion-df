from notion_df import upload, load


def read_notion(
    notion_url: str,
    api_key: str = None,
):
    return load(notion_url, api_key=api_key)


def to_notion(
    self,
    notion_url: str,
    schema=None,
    mode="a",
    title: str = "",
    title_col: str = "",
    api_key: str = None,
):

    return upload(
        df=self,
        notion_url=notion_url,
        schema=schema,
        mode=mode,
        title=title,
        title_col=title_col,
        api_key=api_key,
    )


def pandas():
    import pandas as pd

    pd.read_notion = read_notion
    pd.DataFrame.to_notion = to_notion
