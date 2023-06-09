import pathlib
import re
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
    

class InfoExtractor:

    @staticmethod
    def extract_name(text:str, is_rvc:bool=True) -> str:
        """Removes epochs and steps info from a string"""
        result = ''
        if is_rvc:
            # try to find (RVC) or RVC in the title and remove it and everything after
            if '(rvc' in text.lower():
                # Artist (RVC) 300 epochs -> Artist
                # Artist (From Band) (RVC v2) 300 epochs -> Artist (From Band)
                extra_info_index = text.lower().find('(rvc')
                result = text[:extra_info_index].strip()
            elif 'rvc' in text.lower():
                # Artist RVC 300 epochs -> Artist
                extra_info_index = text.lower().find('rvc')
                result = text[:extra_info_index].strip()
            else:
                # on failure returns the original string
                result = text
        else:
            # SVC models
            # Try to find the number of steps and remove it and everything after
            # Artist 100k -> Artist
            pattern = r'\s\d+[k]?'
            matches = re.findall(pattern, text)
            # if nothing found returns the original string
            if not matches:
                result = text
            else:
                extra_info_index = text.find(matches[0])
                result = text[:extra_info_index]
        return result
    
    @staticmethod
    def extract_epochs(text:str) -> int:
        """Attempts to extract epochs from a string, returns -1 on failure"""
        pattern = r'\(?\d+\.?\d*[k]? epoch[s]?\)?'
        text = text.lower()
        # remove parenthesis
        text = text.replace('(', '').replace(')', '')
        matches = re.findall(pattern, text)
        if not matches:
            # cound't find the epochs
            return -1
        result = matches[0].strip()
        epoch, _ = result.split(' ')
        return NumberConverter.from_string(epoch)
    
    @staticmethod
    def extract_steps(text:str) -> int:
        """Attempts to extract steps from a string, returns -1 on failure"""
        pattern = r'\(?\d+\.?\d*[k]? step[s]?\)?'
        text = text.lower()
        # remove parenthesis
        text = text.replace('(', '').replace(')', '')
        matches = re.findall(pattern, text)
        if not matches:
            # cound't find the epochs
            return -1
        result = matches[0].strip()
        steps, _ = result.split(' ')
        return NumberConverter.from_string(steps)
    
    @staticmethod
    def extract_links(text:str) -> List[str]:
        """Attempt to extract links from a string (currently only google drive and mega)"""
        if 'drive.google.com/' in text:
            pattern = r'https://drive.google.com/file/d/.{33}/view\?usp=(sharing|drive_link)'
            matches = re.finditer(pattern, text)
            return [m.group(0) for m in matches]
        elif 'mega.nz/' in text:
            pattern= r'https://mega.nz/file/.{52}'
        else:
            return list()  # returns an empty list if google drive or mega link not found
        found_links = re.findall(pattern, text)
        return found_links
    

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

# TODO: create archive function to move files to archived folder


def save_json(fp:pathlib.Path, data:dict) -> bool:
    """Note: This function overwrites previous saved data"""
    success:bool = False
    try:
        with open(fp, 'w', encoding='utf8') as json_f:
            json.dump(data, json_f, indent=4)
        success = True
    except Exception as e:
        print(f'Failed to save {fp.name} in {fp.parent}')
    return success


def load_json(fp:pathlib.Path) -> dict:
    data = {}
    # create the file if it doesn't exist
    if not fp.exists():
        save_json(fp, data)

    try:
        with open(fp, 'r', encoding='utf8') as f:
            data = json.load(f)
    except Exception as e:
        print(f'Failed to load {fp.name} from {fp.parent}')
    return data
        