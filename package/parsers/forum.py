import datetime
import pathlib
from typing import List
from bs4 import BeautifulSoup


class PostMessage:

    def __init__(
            self, author:str, content:str,
            publish_date:datetime.datetime, title:str='', reaction_count:int=0):
        self.title = title
        self.author = author
        self.content = content
        self.publish_date = publish_date
        self.reaction_count = reaction_count

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
    def content(self) -> str:
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
        return list()
    
    @property
    def links(self) -> List[str]:
        """All links found in the post"""
        links = []
        for link in self.chat_messages_contents.find_all('a'):
            links.append(link.get('href'))
        return links
    
    @property
    def text(self) -> str:
        """Returns all text found in the post"""
        found_text = ''
        messages_wrapper = self.root_element.find('div', attrs={'class': 'messagesWrapper-RpOMA3'})
        messages_scroller_inner = messages_wrapper.find('ol', attrs={'data-list-id': 'chat-messages'})
        chat_messages_container = messages_scroller_inner.find_all('li', attrs={'class': 'messageListItem-ZZ7v6g'})
        for msg in chat_messages_container:
            msg_author = msg.find('span', attrs={'class': 'username-h_Y3Us'})
            msg_time = msg.find('time')
            msg_content = msg.find('div', attrs={'class': 'markup-eYLPri messageContent-2t3eCI'})
            if msg_author:
                found_text += f'\n[{msg_author.text}]\n'
            found_text += msg_time.text + '\n'
            found_text += msg_content.text + '\n'
        return found_text
    
    def save_extracted_text(self):
        # Saves all extracted text from the page to a text file
        filename = f'{datetime.date.today()} - {self.title}.txt'
        basedir = pathlib.Path(__file__).parent.parent.parent / 'dumps'
        if not basedir.exists():
            basedir.mkdir()
        fp = basedir / filename
        with open(fp, mode='w', encoding='utf8') as f:
            f.write(self.text)
    
    def get_post_message(self) -> PostMessage:
        return PostMessage(
            title=self.title,
            author=self.author,
            content=self.message,
            publish_date=self.publish_date
        )