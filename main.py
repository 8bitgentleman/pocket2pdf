# -*- coding: utf-8 -*-
import pprint
import pockexport.export as px
import configparser
from datetime import datetime
import os
import json

pp = pprint.PrettyPrinter(indent=4)


config = configparser.ConfigParser()
config.read('config.ini')

POCKET_CONSUMER_KEY = str(config['Pocket']['CONSUMER_KEY'])
POCKET_ACCESS_TOKEN = str(config['Pocket']['ACCESS_TOKEN'])


def save_file(pocket_data):
    if not os.path.exists('exports'):
        os.makedirs('exports')
    timestamp = int(datetime.timestamp(datetime.now()))
    out_filename = 'exports/pocket-' + str(timestamp) + ".json"
    with open(out_filename, 'w+') as f:
        # todo sort by block/
        json.dump(pocket_data, f, indent=4, separators=(',', ': '), ensure_ascii=False)


def main():
    # first export and save your pocket info
    pocket_data = px.get_json(consumer_key=POCKET_CONSUMER_KEY, access_token=POCKET_ACCESS_TOKEN)
    save_file(pocket_data)


if __name__ == '__main__':
    main()
