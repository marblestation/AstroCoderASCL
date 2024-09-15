import re
import os
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

if __name__ == '__main__':
    ## Create a session to reuse settings like retries
    #session = requests.Session()

    ## Define a retry strategy with N retries
    #N = 3  # Number of retry attempts
    #retry_strategy = Retry(
        #total=N,  # Total number of retries
        #status_forcelist=[429, 500, 502, 503, 504],  # Retry on these status codes
        #allowed_methods=["HEAD", "GET", "OPTIONS"],  # Methods to retry
        #backoff_factor=1  # Delay between retries (in seconds)
    #)

    ## Attach the retry strategy to an HTTPAdapter
    #adapter = HTTPAdapter(max_retries=retry_strategy)

    ## Mount the adapter for both http and https requests
    #session.mount("http://", adapter)
    #session.mount("https://", adapter)


    # Define the API endpoint and your API token
    API_URL = "https://api.adsabs.harvard.edu/v1/search/query"
    API_TOKEN = os.environ['ADS_API_TOKEN']

    # Define the query
    query = "doctype:software bibstem:ascl"
    #fields = "bibcode,title,abstract,citation_count,read_count,links_data"
    fields = "bibcode,title,abstract,citation_count,read_count"
    rows = 2000  # Maximum number of results to fetch per request

    # Set up the request headers
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
    }

    # Set up the query parameters
    params = {
        "q": query,
        "fl": fields,  # Fields to return
        "rows": rows,
        "start": 0,  # For pagination
        "wt": "json"
    }

    ascl_pattern = r"https?://(ascl\.net)/(\d+\.\d+)"

    # Pagination loop to get all records
    results = []
    i = 0
    while True:
        print(f"[{i+1}] ASCL search")
        i += 1
        response = requests.get(API_URL, headers=headers, params=params)
        response.raise_for_status()  # Check if request was successful
        data = response.json()

        # Collect documents (bibcodes and associated data)
        docs = data['response']['docs']
        results.extend(docs)

        # Check if we need to get more results
        num_found = data['response']['numFound']
        if len(results) >= num_found:
            break

        # Increment the start parameter to get the next batch of results
        params['start'] += rows

    processed = []

    ads_output_file = "output/ads.json"
    if os.path.exists(ads_output_file):
        with open(ads_output_file, "r") as f:
            previous_ads_data = json.loads(f.read())
        processed += previous_ads_data

    done = [p['bibcode'] for p in processed]

    # Print out the results
    for i, doc in enumerate(results):
        print(f"[{i+1}/{len(results)}] {doc.get('bibcode', 'N/A')}")

        bibcode = doc.get('bibcode')
        if bibcode in done:
            continue
        associated_api_url = f"https://api.adsabs.harvard.edu/v1/resolver/{bibcode}/associated"
        # Set up the request headers
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        # Make the request to get associated material
        response = requests.get(associated_api_url, headers=headers)
        #response.raise_for_status()  # Check if the request was successful
        if response.ok:
            associated_data = response.json()
            used_in = [a['bibcode'] for a in associated_data.get('links', {}).get('records', []) if a['title'].startswith("Used in:")]
            described_in = [a['bibcode'] for a in associated_data.get('links', {}).get('records', []) if a['title'].startswith("Described in:")]
        else:
            used_in = []
            described_in = []
            print(f"[{response.status_code}] {associated_api_url}")

        ascl_id = None
        ascl_proxy_link = f"https://ui.adsabs.harvard.edu/link_gateway/{bibcode}/PUB_HTML"
        #response = requests.head(ascl_proxy_link, allow_redirects=True)
        #ascl_link = response.url
        response = requests.head(ascl_proxy_link)
        ascl_link = response.headers['Location']
        match = re.search(ascl_pattern, ascl_link)
        if match:
            domain, ascl_id = match.groups()

        processed.append({
            'bibcode': doc.get('bibcode'),
            'ascl_id': ascl_id,
            'title': doc.get('title'),
            'abstract': doc.get('abstract'),
            'citation_count': doc.get('citation_count'),
            'read_count': doc.get('read_count'),
            'used_in': used_in,
            'described_in': described_in,
        })

        with open(ads_output_file, "w") as f:
            f.write(json.dumps(processed))

import os
import requests
import json
with open("output/ads.json", "r") as f:
    processed = json.loads(f.read())
all_described_in = [bibcode for record in processed for bibcode in record['described_in']]
all_used_in = [bibcode for record in processed for bibcode in record['used_in']]

API_TOKEN = os.environ['ADS_API_TOKEN']
input_bibcodes = set(all_described_in + all_used_in)
bibcodes = "bibcode\n"+"\n".join(input_bibcodes)
url = "https://api.adsabs.harvard.edu/v1/search/bigquery"
params = {
    'q': '*:*',  # Query everything
    'fl': 'bibcode,read_count,citation_count',  # Fields to retrieve
    'wt': 'json',
    'fq':'{!bitset}',
    'rows': len(input_bibcodes),
}

headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'big-query/csv'
}

# Make the POST request to the API
response = requests.post(url, params=params, headers=headers, data=bibcodes)

metrics = {}
if response.status_code == 200:
    # Process the JSON response
    data = response.json()
    for doc in data['response']['docs']:
        metrics[doc['bibcode']] = {'read_count': doc.get('read_count', 0), 'citation_count': doc.get('citation_count', 0)}
else:
    print(f"Error: {response.status_code}, {response.text}")

for record in processed:
    sum_read_count_described_in = 0
    sum_citation_count_described_in = 0
    for bibcode in record['described_in']:
        sum_read_count_described_in += metrics.get(bibcode, {}).get('read_count', 0)
        sum_citation_count_described_in += metrics.get(bibcode, {}).get('citation_count', 0)
    sum_read_count_used_in = 0
    sum_citation_count_used_in = 0
    for bibcode in record['used_in']:
        sum_read_count_used_in += metrics.get(bibcode, {}).get('read_count', 0)
        sum_citation_count_used_in += metrics.get(bibcode, {}).get('citation_count', 0)
    record['sum_read_count_described_in'] = sum_read_count_described_in
    record['sum_citation_count_described_in'] = sum_citation_count_described_in
    record['sum_read_count_used_in'] = sum_read_count_used_in
    record['sum_citation_count_used_in'] = sum_citation_count_used_in

with open("output/metrics.json", "w") as f:
    f.write(json.dumps(metrics))

with open(ads_output_file, "w") as f:
    f.write(json.dumps(processed))

###ads = pd.DataFrame(processed)

