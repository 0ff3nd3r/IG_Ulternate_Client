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
    MIN_TIME_DELAY = 10  # seconds
    MAX_TIME_DELAY = 20  # seconds
    USERNAME = ""
    PASSWORD = ""
    DB_PATH  = "comments.sqlite3"

    comments = []
    responses = []
    api = {}

    def __init__(self, ):      
        # Populate comments list
        self.__read_from_db(self.TABLE_ID_COMMENTS)
        self.__read_from_db(self.TABLE_ID_RESPONSES)
        
    def login(self, username, password):
        # Login to Instagram
        self.api = InstagramAPI(username or self.USERNAME, password or self.PASSWORD)
        return self.api.login()

    def logout(self):
        self.api.logout()
    
    '''
    Adds new response to the pool
    '''
    def add_response(self, text):
        response = Response(text)
        self.__write_to_db(response)
        
        # Look up and update id
        self.__update_id(response)

        self.responses.append(response)
    
    '''
    Removes the response from the pool
    '''
    def remove_response(self, obj):
        if isinstance(obj, Response):
            self.__delete_from_db(obj)
            for i in range(len(self.responses)):
                if self.responses[i].get_id() == obj.get_id():
                    self.responses.pop(i)
        elif isinstance(obj, str) or isinstance(obj, int):
            self.remove_response(self.__find_obj_by_id(obj, self.TABLE_ID_RESPONSES))
        else:
            return False

    '''
    Deletes comment from Instagram
    '''
    def delete_comment(self, obj):
        if isinstance(obj, Comment) and self.api.deleteComment(obj.get_media_id(), obj.get_id()):
            self.__delete_from_db(obj)
            return True
        elif isinstance(obj, str) or isinstance(obj, int):
            self.delete_comment(self.__find_obj_by_id(obj, self.TABLE_ID_COMMENTS))
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
    def add_comment(self, media_id, post_code, comment_text=''):
        comment_text = comment_text or self.__choose_random_response()
        self.api.comment(media_id, emoji.emojize(comment_text))
        comment_id = self.api.LastJson["comment"]["pk"]
        self.__register_comment(media_id, comment_id, post_code, comment_text)
    
    '''
    Adds comments to posts found by certain hashtag
    '''
    def add_comments_by_tag(self, tag):
        posts = self.tag_lookup(tag)

        while True:
            post = posts.pop()
            self.add_comment(media_id=post["pk"], post_code=post["code"])
            if len(posts):
                delay = random.randint(self.MIN_TIME_DELAY, self.MAX_TIME_DELAY)
                print('Sleeping for {} seconds'.format(delay))
                time.sleep(delay)
            else:
                break

    '''
    Prints all comments with ids and posts urls to console
    '''
    def print_comments(self):
        print('--------------------------\nID\t\t\t\tPost Url\t\t\t\tText\n')
        for comment in self.comments:
            print('{0}\t\t{1}\t\t{2}'.format(comment.get_id(), comment.get_post_url(), comment.get_text()))
        print('--------------------------')

    '''
    Prints all responses to console
    '''
    def print_responses(self):
        print('--------------------------\nID\t\tText\n')
        for response in self.responses:
            print('{0}\t\t{1}\t\t'.format(response.get_id(), response.get_text()))
        print('--------------------------')

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
    def __register_comment(self, media_id, comment_id, post_code, comment_text=''):
        comment = Comment(media_id, comment_id, comment_text, post_code)
        self.comments.append(comment)
        if self.__write_to_db(comment):
            print("Succesfully added comment (id: {0} , url: {2} )\r\n\t{1}".format(comment.get_id(), comment.get_text(), comment.get_post_url()))
        else:
            print("Failed to add comment (id: {0} , url: {2} )\r\n\t{1}".format(comment.get_id(), comment.get_text(), comment.get_post_url()))
    
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
            statement = 'DELETE FROM Comments WHERE id={}'.format(comment.get_id())
            
        elif isinstance(obj, Response):
            response = obj
            
            # Prepare SQL statement
            statement = 'DELETE FROM Responses WHERE id={}'.format(response.get_id())
            
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

        statement = ''

        # Prepare SQL statement
        if isinstance(obj, Comment):
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
        array = self.__find_id_in_db(obj)
        
        # Fill up
        if isinstance(obj, Comment):
            obj.set_media_id(array[1])
            obj.set_id(array[0])
        elif isinstance(obj, Response):
            obj.set_id(array[0])

    '''
        Returns the obj found by id
    '''
    def __find_obj_by_id(self, obj_id, table_id):
        # Connect to db
        db = sqlite3.connect(self.DB_PATH)
        cur = db.cursor()
        print("Connected to db to read!")

        statement = ''

        # Prepare SQL statement
        if table_id == self.TABLE_ID_COMMENTS:
            statement = 'SELECT id, media_id, text, post_url FROM Comments WHERE id={}'.format(obj_id)
        elif table_id == self.TABLE_ID_RESPONSES:
            statement = 'SELECT text, id FROM Responses WHERE id={}'.format(obj_id)

        # Execute SQL statement
        cur.execute(statement)
        result = cur.fetchone()

        # Fill up
        if table_id == self.TABLE_ID_COMMENTS:
            return Comment(result[1], result[0], result[2], result[3])
        elif table_id == self.TABLE_ID_RESPONSES:
            return Response(result[0], result[1])
        
    '''
    Reads comments from db
    '''
    def __read_from_db(self, table_id):
        # Connect to db
        db = sqlite3.connect(self.DB_PATH)
        cur = db.cursor()
        print("Connected to db to read!")

        statement = ''

        # Prepare SQL statement
        if table_id == self.TABLE_ID_COMMENTS:
            statement = 'SELECT media_id, id, text, post_url FROM Comments'
        elif table_id == self.TABLE_ID_RESPONSES:
            statement = 'SELECT text, id FROM Responses'
        
        # Execute SQL statement
        cur.execute(statement)
        result = cur.fetchall()
       
        # Fill up
        if table_id == self.TABLE_ID_COMMENTS:
            for comment in result:
                self.comments.append(Comment(comment[0], comment[1], comment[2], comment[3]))
        elif table_id == self.TABLE_ID_RESPONSES:
            for response in result:
                self.responses.append(Response(response[0], response[1]))
            
        print('Success!')

        db.commit()
        db.close()
        
    '''
    Writes specified object to db
    '''
    def __write_to_db(self, obj):
        if isinstance(obj, Comment):
            comment = obj
            
            # Connect to db
            db = sqlite3.connect(self.DB_PATH)
            cur = db.cursor()
            print("Connected to db to write!")
            
            # Prepare SQL statement
            statement = 'INSERT INTO Comments (id, media_id, text, post_url) VALUES (\"{0}\", \"{1}\", \"{2}\", \"{3}\")'.format(comment.get_id(), comment.get_media_id(), comment.get_text(), comment.get_post_url())
            
            # Execute SQL statement
            cur.execute(statement)
            db.commit()
            
            print('Success!')
            
            db.close()
            return True
        elif isinstance(obj, Response):
            response = obj
            
            # Connect to db
            db = sqlite3.connect(self.DB_PATH)
            cur = db.cursor()
            print("Connected to db to write!")
            
            # Prepare SQL statement
            statement = 'INSERT INTO Responses (text) VALUES (\"{0}\")'.format(response.get_text())
            
            # Execute SQL statement
            cur.execute(statement)
            db.commit()
            
            print('Success!')
            
            db.close()
            return True
        else:
            return False