__version__ = '1.0'

import logging
import datetime
import time
import json
import shutil
from pathlib import Path
from typing import List


from package.parsers.forum import DiscordForumParser
from package.parsers.voice_model import VoiceModel, VoiceModelParser
from package.utils.helpers import get_html_files, load_html, load_json, save_text

BASE_DIR = Path(__file__).parent
HTML_DIR = BASE_DIR / 'pages'  # look for .html files in this directory

log_file_path:Path = BASE_DIR / f'{datetime.date.today()}.log'
logger = logging.getLogger('base')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file_path, encoding='utf8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s'))
logger.addHandler(file_handler)


def main():
    html_files = get_html_files(HTML_DIR)
    total_files_analyzed = len(html_files)

    previous_data = load_json(BASE_DIR / 'data.json')
    if previous_data == {}:
        previous_data = {'voice_models': []}
    new_data = {'voice_models': []}  # this will be merged with previous_data and saved to data.json

    # fp = File path
    for fp in html_files[:3]:
        print(f'Analyzing {fp.name}...')
        time.sleep(0.05)

        html_data = load_html(fp)

        try:
            forum_parser = DiscordForumParser(html_data)
            model_parser = VoiceModelParser(forum_parser)

            # don't add to json if there's no link
            if not model_parser.links:
                logger.warning(f'No link found for {model_parser.title}')
                print(f'No link found for {model_parser.title}, manually analyze it by looking the dumps folder')
                forum_parser.save_extracted_text()
                continue

            # don't add to json if there are multiple links
            if len(model_parser.links) > 1:
                logger.warning(f'Multiple links found for {model_parser.title}')
                print(f'Multiple links found for {model_parser.title}, manually analyze it by looking the dumps folder')
                forum_parser.save_extracted_text()
            else:
                # if there's only one link allow saving the data to json
                voice_model = model_parser.extract_model()
                # TODO: fix release date
                new_data['voice_models'].append(voice_model.to_dict())

                # move to archived folder if everything went well
                try:
                    # TODO: create archive folder if doesn't exist
                    #shutil.move(str(fp), str(BASE_DIR / 'pages' / 'archived'))
                    logger.info(f'Moved {fp.name} to archive')
                    logger.info(f'OK - {model_parser.title}')
                except Exception as e:
                    logger.error(f'Failed to move {fp.name} to archive')
                    logger.exception(e)
        except Exception as e:
            logger.error(f'FAIL - {model_parser.title}')
            logger.exception(e)

        print('-' * 128)
        print()

    #with open(BASE_DIR / 'data.json', 'w', encoding='utf8') as json_f:
        # merge the new data with previous one
        #previous_data['voice_models'] +=  new_data['voice_models']
        #json.dump(previous_data, json_f, indent=4)

    message = f'{total_files} file(s) analyzed. See "{log_file_path.name}" for more details.\n\n'
    print(message)


if __name__ == '__main__':
    #main()
    ...