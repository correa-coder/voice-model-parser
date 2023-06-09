from typing import List

from .forum import DiscordForumParser
from ..utils.helpers import NumberConverter, InfoExtractor


class VoiceModel:
    
    def __init__(
            self,
            title:str,
            author:str,
            tags: List[str],
            download_link:str='',
            epochs:int=-1, steps:int=-1):
        self.title = title
        self.author = author
        self.tags = tags
        self.download_link = download_link
        self.epochs = epochs
        self.steps = steps
        self.__type = 'RVC'  # Defaults to RVC
        self.__group = 'No Group'

    @property
    def type(self) -> List[str]:
        """Extract the model type from the tags"""
        result = 'RVC'
        for tag in self.tags:
            if 'RVC V2' in tag:
              result += ' v2'
        return result

    @type.setter
    def type(self, model_type:str):
        self.__type = model_type  # RVC or RVC v2, SVC currently not supported

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
        return InfoExtractor.extract_name(self.title, is_rvc_model)
    
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

    @property
    def epochs(self) -> int:
        result = -1
        if self.category.startswith('RVC'):
          result = InfoExtractor.extract_epochs(self.title)
        return result

    @property
    def steps(self) -> int:
        return InfoExtractor.extract_steps(self.title)

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
            links_filtered = InfoExtractor.extract_links(self.forum_parser.text)
        return links_filtered
    
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
            tags=self.tags,
            download_link=download_link,
            epochs=self.epochs,
            steps=self.steps
        )
        return model
