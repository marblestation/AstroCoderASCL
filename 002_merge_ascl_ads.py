import os
import json
import requests
import numpy as np
import pandas as pd

def extract_github_url(site_list):
    for url in site_list:
        if 'github.com' in url:
            return url
    return None

if __name__ == '__main__':
    ascl_output_path = 'output/ascl_codes.json'
    with open(ascl_output_path, 'r', encoding='utf-8') as json_file:
        ascl_data = json.load(json_file)
    ascl = pd.DataFrame(ascl_data.values())
    ascl.keys()

    with open("output/ads.json", "r") as f:
        ads_data = json.loads(f.read())
    ads = pd.DataFrame(ads_data)

    merged_df = pd.merge(ascl, ads, on='ascl_id', how='inner', suffixes=["_ascl", "_ads"])
    merged_df['views'] = pd.to_numeric(merged_df['views'], errors='coerce').astype('Int64')
    merged_df['github_url'] = merged_df['site_list'].apply(extract_github_url)
    merged_df.to_csv("output/ascl_ads.tsv", sep="\t", index=False)



