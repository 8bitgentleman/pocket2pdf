# -*- coding: utf-8 -*-
import pprint
import pockexport.export as px
import pockexport.dal as dal
from os import listdir, path
import configparser
from datetime import datetime
import os
import json
import requests
from readability import Document
from bs4 import BeautifulSoup as bs
import logging

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.ERROR)

pp = pprint.PrettyPrinter(indent=4)


config = configparser.ConfigParser()
config.read('config.ini')

POCKET_CONSUMER_KEY = str(config['Pocket']['CONSUMER_KEY'])
POCKET_ACCESS_TOKEN = str(config['Pocket']['ACCESS_TOKEN'])
USER_AGENT = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:75.0) Gecko/20100101 Firefox/75.0'

def list_files_of_specific_format(directory, extension=None):
    '''list all files of a specific extension from a directory'''
    specific_files = []

    for file in listdir(directory):
        if extension:
            if file.endswith("." + extension):
                specific_files.append(path.join(directory, file))
                # print(path.basename(file).split(' - ')[0])
        else:
            specific_files.append(path.join(directory, file))
    specific_files = sorted(specific_files)
    return specific_files


def save_pocket_data(pocket_data):
    '''Saves the pocket data as a json file'''
    if not os.path.exists('pocket_exports'):
        os.makedirs('pocket_exports')
    timestamp = int(datetime.timestamp(datetime.now()))
    out_filename = 'pocket_exports/pocket-' + str(timestamp) + ".json"
    with open(out_filename, 'w+') as f:
        json.dump(pocket_data, f, indent=4, separators=(',', ': '), ensure_ascii=False)


def process_pocket_data():
    '''A catch all funciton for now. '''
    pocket_path = 'pocket_exports/'

    fil = list_files_of_specific_format(pocket_path, 'json')
    # access the article info
    d = dal.DAL(fil)
    archived = []
    for a in d.articles():
        if a.json['status'] == '0':
            archived.append(a.json)
    # sort by time added
    archived = sorted(archived, key=lambda k: k.get('time_added', 0), reverse=True)
    for a in archived:
        # omit tags I don't want printed
        if 'tags' in a:
            if "news" in a['tags']:
                continue
            if "covid19" in a['tags']:
                continue
            if "politics" in a['tags']:
                continue
        # collect info about the article to eventually filter through a template
        title = a['resolved_title']
        given_url = a['given_url']
        excerpt = a['excerpt']
        item_id = a['resolved_id']

        try:
            tags = list(a['tags'].keys())
        except Exception:
            pass
        # trying to pull out author info
        try:
            authors = []
            # pp.pprint(a['authors'])
            for n in a['authors']:
                # pp.pprint(n)
                authors.append(n['name'])
            # print(authors)
        except Exception:
            pass
        # domain = a['domain_metadata']['name']
        # top_image = a['top_image_url']
        try:
            logging.info("Downloading article '%s' from %s", title, given_url)
            article_html = dl_article(item_id, given_url)
            save_article('article_exports/article-' + item_id + ".html", article_html)
        except Exception as Argument:
            logging.exception("Error when saving article '%s' from %s", title, given_url)
            pass

def save_article(filename, content):
    '''Save the article to disk'''
    if not os.path.exists('article_exports'):
        os.makedirs('article_exports')

    with open(filename, 'w+') as f:
        f.write(content)

def dl_article(article_id, url):
    '''Download the actual article. Uses a python port of readability.js'''
    # set the user agent to a browser in order to prevent HTTP 406 errors
    headers = {'User-Agent': USER_AGENT}
    response = requests.get(url=url, headers=headers)
    response.raise_for_status()
    doc = Document(response.text)
    # make the output pretty/human readable
    soup = bs(doc.summary(), features="lxml")
    prettyHTML = soup.prettify()
    return prettyHTML

def main():
    # first export and save your pocket info
    logging.info("Downloading data from the Pocket API")
    pocket_data = px.get_json(consumer_key=POCKET_CONSUMER_KEY, access_token=POCKET_ACCESS_TOKEN)
    logging.info("Saving Pocket data")
    save_pocket_data(pocket_data)
    # then sort through the data
    logging.info("Processing Pocket data")
    process_pocket_data()


if __name__ == '__main__':
    main()
