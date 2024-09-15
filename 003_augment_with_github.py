import os
import json
import requests
import numpy as np
import pandas as pd

# Function to extract the owner and repo name from a GitHub URL
def get_repo_info(url):
    # URL format: https://github.com/{owner}/{repo}
    try:
        parts = url.split('/')
        owner, repo = parts[-2], parts[-1]
        return owner, repo
    except Exception as e:
        return None, None

# Function to query GitHub API for stars count
def get_stars_count(owner, repo, token=None):
    if not owner or not repo:
        return -1, -1, -1, -1, None

    # GitHub API URL
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {}

    if token:
        headers['Authorization'] = f"token {token}"

    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            stars = data.get('stargazers_count', 0)
            forks = data.get('forks_count', 0)
            watchers = data.get('subscribers_count', 0)
            open_issues = data.get('open_issues_count', 0)
            language = data.get('language', None)
            return stars, forks, watchers, open_issues, language
        else:
            return -1, -1, -1, -1, None
    except requests.RequestException as e:
        return -1, -1, -1, -1, None

if __name__ == '__main__':
    df = pd.read_csv("output/ascl_ads.tsv", sep="\t")

    df['stars'] = 0
    df['forks'] = 0
    df['watchers'] = 0
    df['open_issues'] = 0
    df['language'] = None

    github_token = os.environ["GITHUB_TOKEN"]

    i = 0
    for index, row in df.iterrows():
        print(f"[{i+1}/{len(df)}]")
        github_url = row['github_url']
        if github_url:
            owner, repo = get_repo_info(github_url)
            stars, forks, watchers, open_issues, language = get_stars_count(owner, repo, token=github_token)
            df.at[index, 'stars'] = stars
            df.at[index, 'forks'] = forks
            df.at[index, 'watchers'] = watchers
            df.at[index, 'open_issues'] = open_issues
            df.at[index, 'language'] = language
            print(stars, forks, watchers, open_issues,language)
        i += 1
    df.to_csv("output/ascl_ads_github.tsv", sep="\t", index=False)

