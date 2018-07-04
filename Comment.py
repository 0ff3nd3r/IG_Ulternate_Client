class Comment(object):
    """docstring for Comment"""

    id       = ''  # pk
    post_url = ''
    media_id = ''
    text     = ''

    def __init__(self, media_id, id, text='', code='', post_url=''):
        super(Comment, self).__init__()
        self.media_id = media_id
        self.id = id
        self.text = text
        self.post_url = post_url or self.generate_post_url(code)

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_media_id(self, media_id):
        self.media_id = media_id

    def get_media_id(self):
        return self.media_id

    def set_post_url(self, post_url):
        self.post_url = post_url

    def get_post_url(self):
        return self.post_url

    def set_text(self, text):
        self.text = text

    def get_text(self):
        return self.text

    # '''
    #    Determines Instagram post's short url by media_id
    # '''
    # @staticmethod
    # def decode_post_url_by_id(media_id):
    #     alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
    #
    #     url = ''
    #     id = int(media_id)
    #
    #     while id > 0:
    #         remainder = id % 64
    #         id = (id - remainder) / 64
    #         url = alphabet[int(remainder)] + url
    #
    #     return url

    # '''
    #     Builds post's url based on media_id
    # '''
    # def generate_post_url(self, media_id):
    #     return 'https://instagram.com/p/' + self.decode_post_url_by_id(media_id)

    '''
        Builds post's url based on media_id
    '''

    def generate_post_url(self, code):
        return 'https://instagram.com/p/{}'.format(code)