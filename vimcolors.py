import os
import time
import json
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool


class Link:
    def __init__(self, name, url):
        self.url = url
        self.name = name


class Spider:
    def __init__(self, total_pages=40):
        self.base_url = "http://vimcolors.com"
        self.total_pages = total_pages
        self.download_dir = 'colors'
        # If we don't have the download directory
        if not os.path.isdir(self.download_dir):
            print(self.download_dir, 'does not exist, trying to create it...')
            # create it...
            os.mkdir(self.download_dir)

    def download(self, link):
        name, url = link.name, link.url

        try:
            full_path = os.path.join(self.download_dir, name)
            # If we have already downloaded this file, just skip
            if os.path.isfile(full_path):
                raise Exception('File: {} already exists; skipping.'.format(name))

            # Get the response
            response = requests.get(url)
            if response.status_code == 404:
                raise Exception('File not found: {}'.format(url))

            # Try downloading the file
            with open(full_path, 'wb') as file_path:
                file_path.write(response.content)
        except Exception as e:
            print(e)
        else:
            print('Downloaded', name)

    def crawl(self):
        def repo_formatter(scheme):
            base_url = scheme['github_repo']['address'].replace('github.com', 'raw.githubusercontent.com')
            return '{}/master/colors/'.format(base_url)
        
        # This will hold all the links
        collection = []

        # Loop over all the pages
        for page in range(self.total_pages):
            print('Fetching links from page', page + 1, 'out of', self.total_pages)
            page_source = requests.get(self.base_url, params={'page': page + 1})
            plain_text = page_source.text
            soup = BeautifulSoup(plain_text, 'lxml')

            # Get the data
            json_data = json.loads(soup.find('div', {'id': 'data'}).attrs['data-colorschemes'])

            # Download the files
            for data in json_data['colorschemes']:
                file_name = data['name'] + '.vim'
                collection.append(Link(file_name, repo_formatter(data)))

        # Delegate to multiprocessing
        print('\n\nFinished crawling pages. Starting downloads...')
        time.sleep(2)

        p = Pool()
        p.map(self.download, collection)

        print('\n\nAll done. Saved files in', os.path.abspath(self.download_dir))

colors_spider = Spider()
colors_spider.crawl()
