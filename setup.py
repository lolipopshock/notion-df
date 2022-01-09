from setuptools import setup, find_packages
import os


def get_requirements(req_file):
    reqs = []
    with open(req_file, "r") as fp:
        for line in fp.readlines():
            if line.startswith("#") or line.strip() == "":
                continue
            else:
                reqs.append(line.strip())
    return reqs


# A trick from https://github.com/jina-ai/jina/blob/79b302c93b01689e82cf4b52f46522eb7497c404/setup.py#L20
libinfo_py = os.path.join("src", "notion_df", "__init__.py")
libinfo_content = open(libinfo_py, "r", encoding="utf8").readlines()
version_line = [l.strip() for l in libinfo_content if l.startswith("__version__")][0]
exec(version_line)  # gives __version__

setup(
    name="notion-df",
    version=__version__,
    description="Notion-DF: Seamlessly Connecting Notion Database with Pandas DataFrame",
    author="Zejiang Shen",
    author_email="zejiangshen@gmail.com",
    license="MIT",
    url="https://github.com/lolipopshock/notion-df",
    package_dir={"": "src"},
    packages=find_packages("src"),
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    install_requires=get_requirements("requirements.txt"),
    extras_require={
        "dev": [
            "black==21.12b0",
            "pytest",
        ],
    }
)