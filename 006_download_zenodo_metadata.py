import re
import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd

def fetch_metadata(url, headers={}, timeout=30):
    """
    Fetches DOI metadata
    """
    record_found = False
    try_later = False
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
    except:
        logger.exception("HTTP request failed: %s", url)
        try_later = True
    else:
        if r.status_code == 400:
            logger.error("Bad request due to bad DOI or DOI not activated yet for: %s", url)
        elif r.status_code == 406:
            logger.error("No answer with the requested format (%s) for: %s", headers.get("Accept", "None"), url)
        elif r.status_code == 404:
            logger.error("Entry not found (404 HTTP error code): %s", url)
        elif not r.ok:
            # Rest of bad status codes
            try_later = True
            logger.error("HTTP request with error code '%s' for: %s", r.status_code, url)
        else:
            record_found = True

    content = None
    if not try_later and record_found:
        content = r.text
    return try_later, record_found, content


if __name__ == '__main__':
    df = pd.read_csv("output/ascl_ads_github.tsv", sep="\t")
    df = df[~df.github_url.isna()]
    df = df[(df['read_count'] > 1) & (df['views'] > 1) & (df['citation_count'] > 1)]
    df = df[(df['stars'] > 1) & (df['forks'] > 1) & (df['watchers'] > 1) & (df['open_issues'] > 1) & (df['language'] == "Python")]

    for idx, row in df.iterrows():
        site_list = json.loads(row['site_list'].replace("'", '"'))
        zenodo_urls = [url for url in site_list if "doi.org/10.5281/zenodo" in url]
        for i, url in enumerate(zenodo_urls):
            output_file = f"output/zenodo/{row['ascl_id']}/zenodo_{i}.xml"
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            if os.path.exists(output_file):
                continue
            print(url)
            headers = {}
            ## https://support.datacite.org/docs/datacite-content-resolver
            ## Supported content types: https://citation.crosscite.org/docs.html#sec-4
            #headers["Accept"] = "application/vnd.datacite.datacite+xml;q=1, application/vnd.crossref.unixref+xml;q=1"
            #headers["Accept"] = "application/vnd.crossref.unixref+xml;q=1" # This format does not contain software type tag
            headers["Accept"] = "application/vnd.datacite.datacite+xml;q=1"
            #base_doi_url = "https://doi.org/"
            #doi_endpoint = base_doi_url + doi
            doi_endpoint = url
            try_later, record_found, content = fetch_metadata(doi_endpoint, headers=headers, timeout=30)
            if record_found:
                with open(output_file, 'w', encoding='utf-8') as xml_file:
                    xml_file.write(content)

