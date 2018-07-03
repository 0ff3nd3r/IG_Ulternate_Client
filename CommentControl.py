import json
import random
import time
import sqlite3

import emoji
from InstagramAPI import InstagramAPI
from Comment import Comment
from Response import Response


class CommentControl:
    TABLE_ID_COMMENTS = 1
    TABLE_ID_RESPONSES = 2
    POST_LIMIT = 10
    MIN_TIME_DELAY = 40  # seconds
    MAX_TIME_DELAY = 90  # seconds
    USERNAME = ""
    PASSWORD = ""
    DB_PATH  = "comments.sqlite3"

    comments = []
    responses = []

    def __init__(self, ):      
        # Populate comments list
        self.__read_from_db(TABLE_ID_COMMENTS)
        self.__read_from_db(TABLE_ID_RESPONSES)
        
    def login(self, username, password):
        # Login to Instagram
        self.api = InstagramAPI(username or self.USERNAME, password or self.PASSWORD)
        self.api.login()
    
    '''
    Adds new response to the pool
    '''
    def add_response(self, text):
        response = Response(text)
        __write_to_db(response)
        
        # Look up and update id
        __update_id(response)
    
    '''
    Removes the response from the pool
    '''
    def remove_response(self, response):
        __delete_from_db(response)
    
    '''
    Determines Instagram post's short url by media_id
    '''
    def decode_post_url_by_id(self, media_id):
        ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
        
        url = ''
        id = int(media_id)
        
        while id > 0:
            remainder = id % 64
            id = (id - remainder) / 64
            url = ALPHABET[int(remainder)] + url
            
        return url

    '''
    Deletes comment from Instagram
    '''
    def delete_comment(self, comment):
        if isinstance(comment, Comment) and self.api.deleteComment(comment.get_media_id(), comment.get_comment_id()):
            self.__delete_from_db(comment)
            return True
        else:
            return False
    
    '''
    Deletes all comments in query from Instagram
    '''
    def delete_all_comments(self):
        print("Preparing to delete all comments...")
        while len(self.comments):
            comment = self.comments.pop()
            if not self.delete_comment(comment):
                return False
        print("Success!")

    '''
    Adds new comment to certain media_id post
    '''
    def add_comment(self, media_id, comment_text=''):
        comment_text = comment_text or self.__choose_random_response()
        self.api.comment(media_id, emoji.emojize(comment_text))
        comment_id = self.api.LastJson["comment"]["pk"]
        self.__register_comment(media_id, comment_id, comment_text)
    
    '''
    Adds comments to posts found by certain hashtag
    '''
    def add_comments_by_tag(self, tag):
        posts = self.tag_lookup(tag)

        for post in posts:
            self.add_comment(post["id"])
            time.sleep(random.randint(self.MIN_TIME_DELAY, self.MAX_TIME_DELAY))

    '''
    Returns an array of posts on Instagram by specified hashtag
    '''
    def tag_lookup(self, tag):
        self.api.tagFeed(tag)
        return self.api.LastJson["items"][:self.POST_LIMIT]

    '''
    Chooses random response from the pool
    '''
    def __choose_random_response(self):
        return random.choice(self.responses).get_text()
        
    '''
    Registers newly added comment
    '''
    def __register_comment(self, media_id, comment_id, comment_text=''):
        comment = Comment(media_id, comment_id, comment_text)
        self.comments.append(comment)
        if self.__write_to_db(comment):
            print("Succesfully added comment (id: {} )\r\n\t{}".format(comment.get_id(), comment.get_text()))
        else:
            print("Failed to add comment (id: {} )\r\n\t{}".format(comment.get_id(), comment.get_text()))
    
    '''
    Deletes specific obj from db
    '''
    def __delete_from_db(self, obj):
        
        # Connect to db
        db = sqlite3.connect(self.DB_PATH)
        print("Connected to db to write!")
        
        if isinstance(obj, Comment):
            comment = obj
            
            # Prepare SQL statement
            statement = 'DELETE FROM Comments where id = \"{}\"'.format(comment.get_id())
            
        elif isinstance(obj, Response):
            response = obj
            
            # Prepare SQL statement
            statement = 'DELETE FROM Responses where id = \"{}\"'.format(response.get_id())
            
        else:
            db.close()
            return False
            
        # Execute SQL statement
        db.execute(statement)
        db.commit()
        
        print('Success!')
        
        db.close()
        return True
    '''
    Determines the id(s) of the obj from db and return the corresponding array
    '''    
    def __find_id_in_db(self, obj):
        # Connect to db
        db = sqlite3.connect(self.DB_PATH)
        print("Connected to db to read!")
        
        # Prepare SQL statement
        if isinstance(obj, Comments):
            statement = 'SELECT id, media_id FROM Comments WHERE text=\"' + obj.get_text() + '\"'
        elif isinstance(obj, Response):
            statement = 'SELECT id FROM Responses WHERE text=\"' + obj.get_text() + '\"'
        
        # Execute SQL statement
        array = db.execute(statement)
        
        print('Success!')
        
        db.close()
        
        return array
    
    '''
    Updates the ids of obj
    '''
    def __update_id(self, obj):
        array = __find_id_in_db(obj)
        
        # Fill up
        if isinstance(obj, Comments):
            obj.set_media_id(array[1])
            obj.set_id(array[0])
        elif isinstance(obj, Response):
            obj.set_id(array[0])
        
    '''
    Reads comments from db
    '''
    def __read_from_db(self, table_id):
        # Connect to db
        db = sqlite3.connect(self.DB_PATH)
        print("Connected to db to read!")
        
        # Prepare SQL statement
        if table_id == TABLE_ID_COMMENTS:
            statement = 'SELECT id, media_id, text FROM Comments'
        elif table_id == TABLE_ID_RESPONSES:
            statement = 'SELECT id, text FROM Responses'
        
        # Execute SQL statement
        array = db.execute(statement)
       
        # Fill up
        if table_id == TABLE_ID_COMMENTS:
            for comment in array:
                self.comments.append(Comment(comment[1], comment[0], comment[2]))
        elif table_id == TABLE_ID_RESPONSES:
            for response in array:
                self.responses.append(Response(response[0], response[1]))
            
        print('Success!')
        
        db.close()
        
    '''
    Writes specified comment -- of type Comment --- to db
    '''
    def __write_to_db(self, obj):
        if isinstance(obj, Comment):
            comment = obj
            
            # Connect to db
            db = sqlite3.connect(self.DB_PATH)
            print("Connected to db to write!")
            
            # Prepare SQL statement
            statement = 'INSERT INTO Comments (id, media_id, text) VALUES (\"{0}\", \"{1}\", \"{2}\")'.format(comment.get_id(), comment.get_media_id(), comment.get_text())
            
            # Execute SQL statement
            db.execute(statement)
            db.commit()
            
            print('Success!')
            
            db.close()
            return True
        elif isinstance(obj, Response):
            response = obj
            
            # Connect to db
            db = sqlite3.connect(self.DB_PATH)
            print("Connected to db to write!")
            
            # Prepare SQL statement
            statement = 'INSERT INTO Responses (text) VALUES (\"{0}\")'.format(response.get_text())
            
            # Execute SQL statement
            db.execute(statement)
            db.commit()
            
            print('Success!')
            
            db.close()
            return True
        else:
            return False