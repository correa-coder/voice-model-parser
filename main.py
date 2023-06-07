__version__ = '1.0'

import logging
import datetime
import time
import json
import shutil
from pprint import pprint
from pathlib import Path

from bs4 import BeautifulSoup

from utils.parsers import VoiceModelParser

BASE_DIR = Path(__file__).parent

log_file_path:Path = BASE_DIR / f'{datetime.date.today()}.log'
logger = logging.getLogger('base')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file_path, encoding='utf8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s'))
logger.addHandler(file_handler)


def main():
    html_dir = BASE_DIR / 'pages'  # look for .html files in this directory
    html_files = [f for f in html_dir.iterdir() if (f.is_file() and f.suffix == '.html')]
    total_files = len(html_files)
    previous_data = {}
    with open(BASE_DIR / 'data.json', 'r', encoding='utf8') as json_f:
        previous_data = json.load(json_f)
    new_data = {'voice_models': [{'test': 123}]}  # this will be saved to data.json

    # fp = File path
    for fp in html_files:
        logger.info(f'Analyzing {fp.name}...')
        time.sleep(0.05)
        with open(fp, mode='r', encoding='utf-8') as f:
            html_data = BeautifulSoup(f, 'html.parser')

        try:
            parser = VoiceModelParser(html_data)
            parser.view_data()
            if parser.links:
                # only add to json if found download links
                new_data['voice_models'].append(parser.to_dict())
                # move to archived folder if everything went well
                try:
                    shutil.move(str(fp), str(BASE_DIR / 'pages' / 'archived'))
                    logger.info(f'Moved {fp.name} to archive')
                    logger.info(f'OK - {parser.title}')
                except Exception as e:
                    logger.error(f'Failed to move {fp.name} to archive')
                    logger.exception(e)
            else:
                logger.warning(f'No download links for {parser.title}')
        except IndexError as e:
            logger.error(f'FAIL - {parser.title} (Couldn\'t extract epochs)')
            logger.exception(e)
        except Exception as e:
            logger.error(f'FAIL - {parser.title}')
            logger.exception(e)

        print('-' * 128)
        print()

    with open(BASE_DIR / 'data.json', 'w', encoding='utf8') as json_f:
        # merge the new data with previous one
        previous_data['voice_models'] +=  new_data['voice_models']
        json.dump(previous_data, json_f, indent=4)

    message = f'{total_files} file(s) analyzed. See "{log_file_path.name}" for more details.\n\n'
    print(message)


if __name__ == '__main__':
    main()
