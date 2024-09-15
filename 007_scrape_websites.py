import re
import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd

def is_textual_url(url):
    """
    Helper function to check if the URL points to a textual resource.
    Returns True if the URL has a textual file extension.
    """
    allowed_extensions = (
        # HTML files
        '.html', '.htm',

        # Plain text files
        '.txt', '.md', '.rst', '.log', '.csv', '.tsv',

        ## XML and related formats
        #'.xml', '.xhtml', '.rss', '.atom', '.svg',

        ## CSS and JavaScript files
        #'.css', '.js', '.json', '.jsonp',

        # Markdown and documentation formats
        '.md', '.rst', '.adoc', '.org', '.tex', '.latex',

        ## YAML and TOML configuration files
        #'.yml', '.yaml', '.toml',

        ## Source code files (if relevant to your scraping, exclude if not)
        #'.py', '.java', '.c', '.cpp', '.sh', '.pl', '.rb', '.php', '.asp', '.aspx', '.jsp', '.go',
        #'.rs', '.scala', '.swift', '.r', '.jl', '.m', '.lua', '.kt', '.ts', '.jsx', '.tsx', '.vb', '.cs',

        ## SQL files
        #'.sql',

        ## Configuration and property files
        #'.ini', '.conf', '.properties', '.cfg',

        # LaTeX and related formats
        '.tex', '.bib', '.cls',

        ## Non-binary types of documentation
        #'.rtf', '.odt',

        # Markdown and rich text format
        '.markdown', '.mdown', '.mkdn',

        ## Scripting and templating languages
        #'.jinja', '.jinja2', '.twig', '.ejs', '.erb', '.hbs', '.liquid',

        ## Other markup and template languages
        #'.yaml', '.yml', '.jsonnet',

        # Any files with no extension (likely HTML pages)
        '',
    )
    parsed_url = urlparse(url)
    _, ext = os.path.splitext(parsed_url.path)
    return ext.lower() in allowed_extensions

def scrape(url, base_url, base_domain, visited_urls=None, output_dir="output/scraped_pages"):
    if visited_urls is None:
        visited_urls = set()
    if url in visited_urls:
        return

    if not is_textual_url(url):
        #print(f'Skipping non-textual resource: {url}')
        return

    print(f'Scraping: {url}')
    visited_urls.add(url)

    # Create a file path for the local HTML file
    path = os.path.join(output_dir, f"{urlparse(url).netloc}_{urlparse(url).path.replace('/', '_')}.html")

    # Ensure the directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if not os.path.exists(path):
        # Get the HTML content if the file does not exist locally
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Save the HTML content to a file
        with open(path, 'w', encoding='utf-8') as file:
            file.write(soup.prettify())
    else:
        # If the file exists, read the HTML from the local file
        with open(path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')

    # Find all anchor tags and process their href links
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(url, href)  # Join relative URLs with the base

        # Parse the current URL and the found full URL
        parsed_base_url = urlparse(base_url)
        parsed_full_url = urlparse(full_url)

        # Check if the URL is within the same domain and subfolder
        if (parsed_full_url.netloc == parsed_base_url.netloc and
            parsed_full_url.path.startswith(parsed_base_url.path)):
            scrape(full_url, base_url, base_domain, visited_urls=visited_urls, output_dir=output_dir)


if __name__ == '__main__':
    ascl_output_path = 'output/ascl_codes.json'
    with open(ascl_output_path, 'r', encoding='utf-8') as json_file:
        ascl_data = json.load(json_file)

    df = pd.DataFrame(ascl_data.values())

    #ispec_id = '1409.006'
    #posidonius_id = '2104.031'
    #filtered_data = {d['ascl_id']: d for d in ascl_data.values() if d['ascl_id'] in (ispec_id, posidonius_id)}
    filtered_data = {d['ascl_id']: d for d in ascl_data.values()}

    github_url_pattern = re.compile(r'https?://(www\.)?github\.com/[\w-]+/[\w-]+')

    for ascl_id, target in filtered_data.items():
        site_list = target['site_list']
        github_urls = [url for url in site_list if re.match(github_url_pattern, url)]
        gitlab_urls = [url for url in site_list if "gitlab" in url]
        git_urls = [url for url in site_list if "git" in url and url not in github_urls and url not in gitlab_urls]
        pypi_urls = [url for url in site_list if "pypi.org" in url]
        doi_urls = [url for url in site_list if "doi.org" in url]
        readthedocs_urls = [url for url in site_list if "readthedocs.io" in url]
        other_urls = [url for url in site_list if url not in github_urls + gitlab_urls + git_urls + pypi_urls + doi_urls + readthedocs_urls]

        for target_url in other_urls:
            # Starting point for the recursive scraping
            base_url = target_url.rstrip('/')  # Ensure no trailing slash for consistency
            base_domain = urlparse(target_url).netloc

            #print(target_url)
            # Call the scrape function, specifying the output directory
            try:
                scrape(target_url, base_url, base_domain, output_dir=f"output/scraped_pages/{ascl_id}/{base_domain}")
            except Exception as e:
                print(f"Exception: {e}")
