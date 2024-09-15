import pandas as pd

if __name__ == '__main__':
    df = pd.read_csv("output/ascl_ads_github.tsv", sep="\t")
    df = df[~df.github_url.isna()]
    df['total_citation_count'] = df['citation_count'] + df['sum_citation_count_described_in'] + df['sum_citation_count_used_in']
    df['total_read_count'] = df['read_count'] + df['sum_read_count_described_in'] + df['sum_read_count_used_in']
    fields = ["views", "total_read_count", "total_citation_count", "stars", "watchers", "open_issues"]
    for field in fields:
        df = df[df[field] > 1]
    df = df[df['language'] == "Python"]
    df['github_link'] = df['github_url']
    selected = df[['ascl_id', 'title_ascl', 'github_link', 'views', 'total_read_count', 'total_citation_count', 'stars', 'forks', 'watchers', 'open_issues']]
    selected.to_csv("output/selected_ascl_ads_github.csv", index=False)
