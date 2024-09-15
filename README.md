
# ASCL Selection

This is a collection of small scripts to retrieve, augment, process and select records from ASCL to be used in the AstroCoder hackathon project at the [NLP for Space Science workshop](https://www.cosmos.esa.int/web/natural-language-processing-for-space-science).

## Usage

Create a Python environment ([https://github.com/astral-sh/uv](uv)):

```bash
uv venv
source .venv/bin/activate
uv pip install requests
uv pip install ipython
uv pip install beautifulsoup4
uv pip install pandas
uv pip install matplotlib
```

Setup tokens before running any script:

```bash
export ADS_API_TOKEN="<secret>"
export GITHUB_TOKEN="<secret>"
```

Available scripts:

- `000_download_ascl.py`: Download the full ASCL json file
- `001_download_ads.py`: Download ASCL metadata from ADS including `citation_count` and `read_count`
- `002_merge_ascl_ads.py`: Merge ASCL and ADS data
- `003_augment_with_github.py`: For all records that have a GitHub repo, augment including GitHub `stars`, `forks`, etc...
- `004_plot.py`: Generate plots to compare metrics
- `005_selection.py`: Final selection of Python packages for this project
- `006_download_zenodo_metadata.py`: Download zenodo metadata for zenodo DOIs
- `007_scrape_websites.py`: Scrape websites that are not github, doi, pypi, etc...

All the outputs will be saved in `./oputput/`. The two last scripts were not finally used by the hackathon project.
