import datetime
import re
from typing import List

from bs4 import BeautifulSoup


class PostMessage:

    def __init__(self, title:str, author:str, content:str, publish_date:datetime.datetime):
        self.title = title
        self.author = author
        self.content = content
        self.publish_date = publish_date

    @property
    def reaction_count(self) -> int:
        ...

    def __str__(self) -> str:
        result = '\n'
        result += f'Title: {self.title}\n'
        result += f'Author: {self.author}\n'
        result += f'Publish date: {self.publish_date.strftime("%Y-%m-%d")}\n'
        result += f'Content:\n{self.content}\n'
        result += '-' * 128 + '\n'
        return result


class PostContent(PostMessage):
    
    def __init__(self, tags:List[str], **kwargs):
        super().__init__(**kwargs)
        self.tags = tags
        self.replies:List[PostMessage] = []

    def __str__(self) -> str:
        result = '\n'
        result += f'Title: {self.title}\n'
        result += f'Author: {self.author}\n'
        result += f'Tags: {self.tags}\n'
        result += f'Publish date: {self.publish_date.strftime("%Y-%m-%d")}\n'
        result += f'Content:\n{self.content}\n'
        result += '-' * 128 + '\n'
        return result


class DiscordForumParser:
    """Extracts info from a discord forum thread"""

    def __init__(self, html_data: BeautifulSoup):
        # start searching data from this section html element
        self.root_element = html_data.find('section', attrs={'role': 'complementary'})
        self.messages_wrapper = self.root_element.contents[1]
        self.chat_messages = self.messages_wrapper.find('ol', attrs={'data-list-id': 'chat-messages'})
        self.chat_title_container = self.chat_messages.contents[1]
        self.chat_messages_contents = self.chat_messages.find('li').contents[0].contents[0]

        reactions_div_attrs = {'class': 'reactions-3HFE-S reactions-2mDOkX', 'role': 'group'}
        self.reactions_container = self.chat_messages.find('div', attrs=reactions_div_attrs)

    @property
    def title(self) -> str:
        """Returns the title of the post"""
        return self.chat_title_container.find('h3').text
    
    @property
    def tags(self) -> List[str]:
        """Returns the tags found in the post"""
        chat_tags_container = self.chat_title_container.contents[-1]
        chat_tags = []
        for tag in chat_tags_container.contents:
            chat_tags.append(tag.text)
        return chat_tags
    
    @property
    def author(self) -> str:
        """Returns the author of the post"""
        return self.chat_messages_contents.find('h3').contents[0].contents[0].text
    
    @property
    def publish_date(self) -> datetime.datetime:
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
    def message(self) -> str:
        """The original message posted by the author, including links"""
        return self.chat_messages_contents.contents[2].text.strip()
    
    @property
    def reactions_count(self) -> int:
        count = 0
        results = self.reactions_container.find_all('div', attrs={'class': 'reactionCount-SWXh9W'})
        for result in results:
            count += int(result.text.strip())
        return count
    
    @property
    def replies(self) -> List[PostMessage]:
        """List containing the post replies"""
        list_items = self.chat_messages.find_all('li', attrs={'class': 'messageListItem-ZZ7v6g'})
        post_title = ''
        print(post_title)
        post_date:str = list_items[0].find_all('time')[0]['datetime'][:10]
        post_date:datetime.datetime = datetime.datetime.strptime(post_date, '%Y-%m-%d')
        post_message = PostMessage(
            title=post_title,
            author='',
            content='',
            publish_date=post_date
        )
        #print(post_message)
        #for item in list_items:
            #print(item.find())
        return list()
    
    @property
    def post_content(self) -> PostContent:
        content = PostContent(
            title=self.title,
            author=self.author,
            content=self.message,
            publish_date=self.publish_date,
            tags=self.tags
        )
        content.replies = self.replies
        return content
    
    def dump(self) -> str:
        content = ''
        content += f'Title: {self.title}\n'
        content += f'Tags: {self.tags}\n'
        content += f'Author: {self.author}\n'
        content += f'Publish date: {self.publish_date.strftime("%Y-%m-%d")}\n'
        content += f'Original message:\n{self.message}\n'
        content += '-' * 128 + '\n'
        content += f'Replies:\n'
        for reply in self.replies:
            print(f'Reply:\n{reply}\n')
        return content
    
    def get_post_message(self) -> PostMessage:
        return PostMessage(
            title=self.title,
            author=self.author,
            content=self.message,
            publish_date=self.publish_date
        )


class VoiceModel:
    ...


class VoiceModelParser:

    def __init__(self, html_data: BeautifulSoup, forum_parser: DiscordForumParser):
        self.forum_parser = forum_parser
        # start searching data from this section html element
        self.root_element = html_data.find('section', attrs={'role': 'complementary'})
        self.messages_wrapper = self.root_element.contents[1]
        self.chat_messages = self.messages_wrapper.find('ol', attrs={'data-list-id': 'chat-messages'})
        self.chat_title_container = self.chat_messages.contents[1]
        self.chat_messages_contents = self.chat_messages.find('li').contents[0].contents[0]

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
        if 'k' in epoch.lower():
            epoch = epoch.lower().replace('k', '')
            epoch = float(epoch) * 1000
        result = int(epoch)
        return result

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
        if 'k' in steps.lower():
            steps = steps.lower().replace('k', '')
            steps = float(steps) * 1000
        result = int(steps)
        return result

    @property
    def steps(self) -> int:
        return self.extract_steps(self.title)

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
    
    @staticmethod
    def extract_links(text:str) -> List[str]:
        """Attempt to extract links from a string (currently only google drive and mega)"""
        if 'drive.google.com/' in text:
            pattern = r'https://drive.google.com/file/d/.{33}/view\?usp=sharing'
        elif 'mega.nz/' in text:
            pattern= r'https://mega.nz/file/.{52}'
        else:
            return list()  # returns an empty list if google drive or mega link not found
        found_links = re.findall(pattern, text)
        return found_links

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
            # add steps if present
            if self.steps != -1:
                result['info'] += f' {self.steps} Steps'
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


if __name__ == '__main__':
    PostContent(
        title='Test post',
        author='test author',
        message='Hello world',
        publish_date=datetime.datetime.now(),
        tags=['Tag 1', 'Tag 2']
    )