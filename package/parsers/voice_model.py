import re
from typing import List

from .forum import DiscordForumParser
from ..utils.helpers import NumberConverter


class VoiceModel:
    
    def __init__(self, title:str, author:str, type:str='RVC', download_link:str='', epochs:int=-1, steps:int=-1):
        self.title = title
        self.author = author
        self.type = type
        self.download_link = download_link
        self.epochs = epochs
        self.steps = steps
        self.__group = 'No Group'

    @property
    def has_group(self) -> bool:
        return self.group != 'No Group'

    @property
    def group(self) -> str:
        # Remove parenthesis from title if any
        title = self.title.replace('(', '').replace(')', '')
        if 'from' in title.lower():
            start_index = title.lower().find('from')
            return title[start_index+5:].strip()
        if self.__group == 'No Group':
            # check common groups
            common_groups = ['TWICE', 'BLACKPINK', 'LE SSERAFIM']
            for grp in common_groups:
                if grp.lower() in title.lower():
                    return grp
        return self.__group

    @group.setter
    def group(self, text:str):
        self.__group = text

    @property
    def name(self) -> str:
        result = self.title
        if self.has_group:
            _name = self.title.replace(self.group, '')
            _name = _name.replace('(', '').replace(')', '')
            _name = _name.replace('From', '')
            _name = _name.replace('from', '')
            return _name.strip().title()
        return result.title()
    
    def to_dict(self) -> dict:
        result = {}
        result['name'] = self.name
        if self.epochs == -1:
            result['info'] = 'No additional info'
        else:
            result['info'] = f'{NumberConverter.to_string(self.epochs)} Epochs'
            # add steps if present
            if self.steps != -1:
                result['info'] += f' {NumberConverter.to_string(self.steps)} Steps'
        result['release_date'] = self.release_date.strftime('%Y-%m-%d')
        if self.links:
            result['download_link'] = self.links[0]
        else:
            result['download_link'] = ''
        result['category'] = self.category
        result['author'] = self.author
        return result

    def __str__(self) -> str:
        result = f'{self.name}'
        if self.has_group:
            result += f' (From {self.group})'
        
        result += f' ({self.type})'

        if self.epochs != -1:
            result += f' {NumberConverter.to_string(self.epochs)} Epochs'
        if self.steps != -1:
            result += f' {NumberConverter.to_string(self.steps)} Steps'
        return result


class VoiceModelParser:

    def __init__(self, forum_parser: DiscordForumParser):
        self.forum_parser = forum_parser

    @property
    def title(self) -> str:
        """Returns the title of the post"""
        return self.forum_parser.title

    @property
    def name(self) -> str:
        """Returns the voice model name extracted from the title"""
        is_rvc_model:bool = self.category.startswith('RVC')
        return self.extract_name(self.title, is_rvc_model)
    
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

    @property
    def tags(self) -> List[str]:
      """Post tags such as RVC, Korean, Rapper etc."""
      return self.forum_parser.tags

    @property
    def category(self) -> str:
        """RVC or RVC v2"""
        result = 'RVC'
        for tag in self.tags:
            if 'RVC V2' in tag:
              result += ' v2'
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

    @property
    def epochs(self) -> int:
        result = -1
        if self.category.startswith('RVC'):
          result = self.extract_epochs(self.title)
        return result
    
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

    @property
    def steps(self) -> int:
        return self.extract_steps(self.title)

    @property
    def links(self) -> List[str]:
        """Download links links found in the post"""
        all_links = self.forum_parser.links
        # Filter download links
        valid_download_providers = ['drive.google.com', 'mega.nz', 'mediafire', 'pixeldrain', 'krakenfiles']
        links_filtered = []
        for link in all_links:
            for valid_provider in valid_download_providers:
                if valid_provider in link:
                    links_filtered.append(link)
        # if links not found in the post, look for it in the comments
        if len(links_filtered) < 1:
            links_filtered = self.extract_links(self.forum_parser.text)
        return links_filtered
    
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

    def extract_model(self) -> VoiceModel:
        """Returns a `VoiceModel` object"""
        links = self.links
        download_link = ''
        if len(links) > 0:
            # if multiple links found get the first one
            download_link = links[0]

        model = VoiceModel(
            title=self.name,
            author=self.forum_parser.author,
            type=self.category,
            download_link=download_link,
            epochs=self.epochs,
            steps=self.steps
        )
        return model
