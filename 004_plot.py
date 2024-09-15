import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import itertools


if __name__ == '__main__':
    df = pd.read_csv("output/ascl_ads_github.tsv", sep="\t")
    #stats = df[['ascl_id', 'citation_count', 'read_count', 'views']]
    #stats.sort_values(by="citation_count", ascending=False)
    #stats.sort_values(by="read_count", ascending=False)
    #stats.sort_values(by="views", ascending=False)

    df['total_citation_count'] = df['citation_count'] + df['sum_citation_count_described_in'] + df['sum_citation_count_used_in']
    df['total_read_count'] = df['read_count'] + df['sum_read_count_described_in'] + df['sum_read_count_used_in']
    fields = ["views", "read_count", "citation_count", "stars", "watchers", "open_issues", "sum_read_count_described_in", "sum_citation_count_described_in", "sum_read_count_used_in", "sum_citation_count_used_in", "total_read_count", "total_citation_count"]
    #field_pairs = list(itertools.combinations(fields, 2)) # Without repetition
    field_pairs = list(itertools.permutations(fields, 2))
    df = df[df['language'] == "Python"]

    for x_label, y_label in field_pairs:
        x_values = df[x_label]
        y_values = df[y_label]
        plt.scatter(x_values, y_values)

        num_ticks = 10
        #xticks_positions = np.linspace(0, max(x_values), num=num_ticks)
        xticks_positions = np.linspace(0, np.percentile(x_values, 99), num=num_ticks)
        xticks_positions = np.round(xticks_positions).astype(int)
        plt.xticks(xticks_positions, rotation=45)
        plt.xlim(0, xticks_positions[-1])

        #yticks_positions = np.linspace(0, max(y_values), num=num_ticks)
        yticks_positions = np.linspace(0, np.percentile(y_values, 99), num=num_ticks)
        yticks_positions = np.round(yticks_positions).astype(int)
        plt.yticks(yticks_positions, rotation=45)
        plt.ylim(0, yticks_positions[-1])
        plt.ylabel(y_label)
        plt.xlabel(x_label)
        plt.tight_layout()

        plot_filename = f"output/plots/{x_label}_vs_{y_label}.png"
        os.makedirs(os.path.dirname(plot_filename), exist_ok=True)
        plt.savefig(plot_filename)
        plt.close()
        plt.clf()
