import os
import json
import requests
from bs4 import BeautifulSoup


class Spider:
    def __init__(self, total_pages=40):
        self.base_url = "http://vimcolors.com/?page="
        self.total_pages = total_pages
        self.download_dir = 'colors/'
        # If we don't have the download directory
        if not os.path.isdir(self.download_dir):
            print(self.download_dir, 'does not exist, trying to create it...')
            # create it...
            os.mkdir(self.download_dir)

    def download(self, name, url):
        # If we have already downloaded this file, just skip
        if os.path.isfile(self.download_dir + name):
            print('File:', name, 'already exists; skipping.')
            return

        try:
            # Get the response
            response = requests.get(url)
            # If response is 404 (Not Found), just exit
            if response.status_code == 404:
                raise Exception('File not found')
            # Create the file
            with open(self.download_dir + name, 'wb') as file_path:
                # Write content to the file
                file_path.write(response.content)
                # Confirm the download
                print('Downloaded', name)
        except:
            # This is a very generic error, perhaps I'll change it sometime :)
            print('Could not download the file', name)
            pass

    def crawl(self):
        def repo_formatter(scheme):
            return scheme['github_repo']['address'].replace('github.com', 'raw.githubusercontent.com') \
                   + '/master/colors/'

        # Loop over all the pages
        for page in range(self.total_pages):
            page_source = requests.get(self.base_url + str(page + 1))
            plain_text = page_source.text
            soup = BeautifulSoup(plain_text, 'lxml')

            # Get the data
            json_data = json.loads(soup.find('div', {'id': 'data'}).attrs['data-colorschemes'])

            # Download the files
            for data in json_data['colorschemes']:
                file_name = data['name'] + '.vim'
                self.download(file_name, repo_formatter(data) + file_name)


colors_spider = Spider()
colors_spider.crawl()
