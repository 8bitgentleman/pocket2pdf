# -*- coding: utf-8 -*-
import pprint
import pockexport.export as px
import pockexport.dal as dal
from os import listdir, path
import configparser
from datetime import datetime
import os
import json

pp = pprint.PrettyPrinter(indent=4)


config = configparser.ConfigParser()
config.read('config.ini')

POCKET_CONSUMER_KEY = str(config['Pocket']['CONSUMER_KEY'])
POCKET_ACCESS_TOKEN = str(config['Pocket']['ACCESS_TOKEN'])


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


def save_file(pocket_data):
    if not os.path.exists('pocket_exports'):
        os.makedirs('pocket_exports')
    timestamp = int(datetime.timestamp(datetime.now()))
    out_filename = 'pocket_exports/pocket-' + str(timestamp) + ".json"
    with open(out_filename, 'w+') as f:

        json.dump(pocket_data, f, indent=4, separators=(',', ': '), ensure_ascii=False)


def pocket_archived():
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
        # omit tags I don't want to print
        if 'tags' in a:
            if "news" in a['tags']:
                continue
            if "covid19" in a['tags']:
                continue
            if "politics" in a['tags']:
                continue
        # if a['resolved_title'] is '':
        #     print(a['given_title'])
        # else:
        #     print(a['resolved_title'])

        title = a['resolved_title']
        resolved_url = a['resolved_url']
        excerpt = a['excerpt']
        try:
            tags = list(a['tags'].keys())
        except Exception:
            pass
        try:
            authors = []
            pp.pprint(a['authors'])
            for n in a['authors']:
                # pp.pprint(n)
                authors.append(n['name'])
            print(authors)
        except Exception:
            pass
        # # authors = a['authors']
        # # domain = a['domain_metadata']['name']
        # # top_image = a['top_image_url']


def main():
    # first export and save your pocket info
    # pocket_data = px.get_json(consumer_key=POCKET_CONSUMER_KEY, access_token=POCKET_ACCESS_TOKEN)
    # save_file(pocket_data)
    pocket_archived()


if __name__ == '__main__':
    main()
