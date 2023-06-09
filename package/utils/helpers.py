import pathlib
import json
import shutil
from typing import List
from bs4 import BeautifulSoup


class NumberConverter:

    @staticmethod
    def to_string(number:int) -> str:
        # input: 44100, output: 44.1k
        if number >= 1000:
            if number % 1000 == 0:
                return f'{int(number/1000)}k'
            return f'{number/1000:.1f}k'
        return str(number)

    @staticmethod
    def from_string(text:str) -> int:
        # input: 44.1k, output: 44100
        text = text.lower().strip()
        if 'k' in text:
            number = text.replace('k', '')
            return int(float(number) * 1000)
        return int(text)
    

def load_html(src:pathlib.Path) -> BeautifulSoup:
    with open(src, mode='r', encoding='utf8') as html_file:
        html_data = BeautifulSoup(html_file, 'html.parser')
    return html_data


def save_text(text:str, dest:pathlib.Path, filename:str):
    # create the directory if it doesn't exist
    dest.mkdir(exist_ok=True)
    fp = dest / filename
    with open(fp, 'w', encoding='utf8') as f:
        f.write(text)


def get_html_files(directory:pathlib.Path) -> List[pathlib.Path]:
    return [f for f in directory.iterdir() if (f.is_file() and f.suffix == '.html')]

# TODO: create save dump function

# TODO: create archive function to move files to archived folder

# TODO: create helper function to load and save json