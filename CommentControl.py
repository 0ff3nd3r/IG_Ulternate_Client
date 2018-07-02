from InstagramAPI import InstagramAPI
import emoji
import random
import time
import json


class CommentControl:

    POST_LIMIT = 10

    COMMENTS = [emoji.emojize("Nice pic! :thumbs_up:"),
               emoji.emojize(":thumbs_up: :thumbs_up: :thumbs_up:"),
               emoji.emojize(":fire: :fire: :fire:"),
               emoji.emojize("😍 😍 😍"),
               emoji.emojize("Nice one! :thumbs_up:"),
               emoji.emojize("Loving it! 💜"),
               emoji.emojize("Wow that looks awesome! :thumbs_up:"),
               emoji.emojize("Love ur profile! Keep it up! 🙏")]

    comments = []
    USERNAME = ""
    PASSWORD = ""

    def __init__(self, username, password, comments_file_path=''):
        self.api = InstagramAPI(username or self.USERNAME, password or self.PASSWORD)
        self.api.login()
        if comments_file_path:
            self.load_comments(comments_file_path)

    def delete_all_comments(self):
        while len(self.comments):
            comment = self.comments.pop()
            if not self.delete_comment(comment["mediaId"], comment["commentId"]):
                return False

    def delete_comment(self, mediaid, commentId):
        return self.api.deleteComment(mediaid, commentId)

    def register_commentId(self, api, mediaId, commentId):
        self.comments.append({"mediaId" : mediaId, "commentId" : commentId})

    def leave_comment(self, mediaId, comment_text=''):
        comment_text = comment_text or self.choose_text()
        self.api.comment(mediaId, comment_text)
        comment_id = self.api.LastJson["comment"]["pk"]
        self.register_commentId(self.api, mediaId, comment_id)

    def choose_text(self):
        return random.choice(self.COMMENTS)

    def tag_lookup(self, tag):
        self.api.tagFeed(tag)
        return self.api.LastJson["items"][:self.POST_LIMIT]

    def leave_comments_by_tag(self, tag):
        posts = self.tag_lookup(tag)

        for post in posts:
            self.leave_comment(post["id"])
            time.sleep(20)  # 20sec

    def save_comments(self, path=''):
        with open(('comments_{}.json'.format(int(time.time()))), 'w') as out:
             json.dump(self.comments, out)

    def load_comments(self, file_path):
        with open(file_path, 'r') as file:
            self.comments = json.load(file)