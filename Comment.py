class Comment(object):
  """docstring for Comment"""
  
  id       = ''      # pk
  media_id = ''
  text     = ''
  
  def __init__(self, media_id, id, text=''):
    super(Comment, self).__init__()
    self.media_id = media_id
    self.id = id
    self.text = text
    
  def set_id(self, id):
    self.id = id
    
  def get_id(self):
    return self.id
    
  def set_media_id(self, media_id):
    self.media_id = media_id
    
  def get_media_id(self):
    return self.media_id
  
  def set_text(self, text):
    self.text = text
    
  def get_text(self):
    return self.text