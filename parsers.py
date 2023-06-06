import datetime
import re
from typing import List

from bs4 import BeautifulSoup

'''
Post title rules by QuickWick
-----------------------------

`Britney Spears 100k` - For SVC, there will be no tag
`Jhay Cortez (RVC) 250 Epoch` - For RVC
`Gummibär (RVC v2) 300 Epoch` - For RVC v2
`Jeno (From NCT) (RVC) 350 Epoch 11k Steps` - This is RVC with a band name

If Artists is in a band or from game or animeshow, Do the following:

ArtistName `(From Bandname)` (RVC) 250 Epoch
ArtistName `(From AnimeShowName)` (RVC) 500 Epoch
ArtistName `(From GameName)` (RVC) 2.7k Epoch

Note: SVC should only include Steps. RVC Should include Epochs to easily differentiate - RVC can include both Epoch & Steps, if you so wish such as example #4.

If an Epoch or Steps surpasses 999, it should be named the following for title compression:
`ASAP Rocky (RVC) 1k Epoch`
`Maeve (From Paladins) 1.6k Epoch`
'''

class VoiceModel:
    ...


class VoiceModelParser:

    def __init__(self, html_data: BeautifulSoup):
        # start searching data from this section html element
        self.root_element = html_data.find('section', attrs={'role': 'complementary'})
        self.messages_wrapper = self.root_element.contents[1]
        self.chat_messages = self.messages_wrapper.find('ol', attrs={'data-list-id': 'chat-messages'})
        self.chat_title_container = self.chat_messages.contents[1]
        self.chat_messages_contents = self.chat_messages.find('li').contents[0].contents[0]

    @property
    def title(self) -> str:
        """Returns the title of the post"""
        return self.chat_title_container.find('h3').text

    @property
    def name(self) -> str:
        """Returns the voice model name extracted from the title"""
        info_start_index = self.title.lower().find('rvc')
        return self.title[:info_start_index-1].strip()

    @property
    def tags(self) -> List[str]:
      """Post tags such as RVC, Korean, Rapper etc."""
      chat_tags_container = self.chat_title_container.contents[-1]
      chat_tags = []
      for tag in chat_tags_container.contents:
          chat_tags.append(tag.text)
      return chat_tags

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
          pattern = r'\d*\.?\d+[K-k]? [E-e]poch[s]?'
          matches = re.findall(pattern, self.title)
          result = matches[0]
          epoch, _ = result.split(' ')
          if 'k' in epoch.lower():
            epoch = epoch.lower().replace('k', '')
            epoch = float(epoch) * 1000
          result = int(epoch)
        return result

    @property
    def steps(self) -> int:
        return -1

    @property
    def author(self) -> str:
        """Returns the author of the post"""
        return self.chat_messages_contents.find('h3').contents[0].contents[0].text

    @property
    def release_date(self) -> datetime.datetime:
        """Date when the post was published as a python datetime object"""
        post_date = self.chat_messages.contents[2].text.replace('new', '').strip()
        year = int(post_date.split(',')[-1].strip())
        day_and_month = post_date.split(',')[0].strip()
        month, day = day_and_month.split(' ')
        day = f'{int(day):02d}' # add leading 0 if missing e.g 1 -> 01
        post_date = f'{year} {month} {day}'
        format_code = '%Y %B %d'  # e.g. 2023 June 05
        result = datetime.datetime.strptime(post_date, format_code)
        return result

    @property
    def links(self) -> List[str]:
        """Returns links found within the post (except from comments)"""
        links = []
        # Filter download links
        allowed_links = ['drive.google.com', 'mega.nz', 'mediafire', 'pixeldrain', 'krakenfiles']
        links_filtered = []
        for link in self.chat_messages_contents.find_all('a'):
            # TODO: Filter links
            links.append(link.get('href'))
        # TODO: If links not found, search in author comments
        # sometimes they forgot and add the link later in a comment
        return links

    @property
    def message(self) -> str:
        """The original message posted by the author, including links"""
        return self.chat_messages_contents.contents[2].text

    def check_post_title(self):
        """Checks if title follows the naming rules"""
        title = self.title
        print(f'\nChecking title \'{title}\'\n')
        if 'RVC' in title:
            if 'v2' not in title.lower():
                print('✓ RVC')
            else:
                print('✓ RVC v2')
        else:
            print('✓ SVC')

        if 'epoch' in title.lower():
            print('✓ Epoch')
        else:
            print('❌ Missing epoch')
        
        # Optional info
        if 'step' in title.lower():
            print('✓ Steps')
        if 'from ' in title.lower():
            print('✓ Band/Group')
        if ' of ' in title.lower():
            print('❌ Band/Group name should be in parenthesis')
        

    def extract_model(self):
        """Creates a `VoiceModel` object from the html content"""
        return None

    def view_data(self):
        """Shows the data that has been extracted"""
        print('Title:', self.title)
        print('Author:', self.author)
        print('Tags:', self.tags)
        print('Category:', self.category)
        print('Epochs:', self.epochs)
        print('Steps:', self.steps)
        print('Date:', self.release_date.strftime('%Y-%m-%d'))
        print('Model:', self.name)
        if not self.links:
            print('Couldn\'t find any download link')
        else:
            print('Links:', self.links)
        print('\nOriginal message:\n', self.message)
        print()

    def to_dict(self) -> dict:
        result = {}
        result['name'] = self.name
        if self.epochs == -1:
            result['info'] = 'No additional info'
        else:
            result['info'] = f'{self.epochs} Epochs'
        result['release_date'] = self.release_date.strftime('%Y-%m-%d')
        if self.links:
            result['download_link'] = self.links[0]
        else:
            result['download_link'] = ''
        result['category'] = self.category
        result['author'] = self.author
        return result


class PostTitleChecker:
    ...
