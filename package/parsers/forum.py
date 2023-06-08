import datetime
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
    
    @property
    def links(self) -> List[str]:
        """All links found in the post"""
        links = []
        for link in self.chat_messages_contents.find_all('a'):
            links.append(link.get('href'))
        return links
    
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