__version__ = '1.0'

import logging
import datetime
import time
import json
import shutil
from pprint import pprint
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup

from package.parsers.forum import DiscordForumParser
from package.parsers.voice_model import VoiceModel, VoiceModelParser

BASE_DIR = Path(__file__).parent
HTML_DIR = BASE_DIR / 'pages'  # look for .html files in this directory

log_file_path:Path = BASE_DIR / f'{datetime.date.today()}.log'
logger = logging.getLogger('base')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file_path, encoding='utf8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s'))
logger.addHandler(file_handler)


def get_html_files(directory:Path) -> List[Path]:
    return [f for f in directory.iterdir() if (f.is_file() and f.suffix == '.html')]


def quick_testing():
    # test only one html file
    html_file = get_html_files(HTML_DIR)[0]
    fp = html_file
    with open(fp, mode='r', encoding='utf-8') as f:
        html_data = BeautifulSoup(f, 'html.parser')

    forum_parser = DiscordForumParser(html_data)
    model_parser = VoiceModelParser(forum_parser)

    model_parser.view_data()

    voice_model = model_parser.extract_model()
    print(str(voice_model))
    
    #post = forum_parser.post_content
    #print(post)

    #for reply in forum_parser.replies:
        #print(reply)


def main():
    html_files = get_html_files(HTML_DIR)
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
                # only add to json if found download links and there's only one link
                if len(parser.links) > 1:
                    logger.warning(f'Multiple links found, skipping {parser.title}')
                else:
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
    #main()
    quick_testing()
