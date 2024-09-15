import os
import requests

def download(url, output_path):
    # Send a GET request to the URL
    response = requests.get(url)
    response.raise_for_status()  # Automatically raise an exception for HTTP errors

    with open(output_path, 'w', encoding='utf-8') as json_file:
        json_file.write(response.text)
    print(f'JSON file downloaded and saved as {output_path}')

if __name__ == '__main__':
    ascl_output_path = 'output/ascl_codes.json'
    os.makedirs(os.path.dirname(ascl_output_path), exist_ok=True)
    if not os.path.exists(ascl_output_path):
        url = 'https://ascl.net/code/json'
        download(url, ascl_output_path)



