class Response(object):
  
  id = 0
  text = ''
  
  def __init__(self, text, id=0):
    super(Response, self).__init__()
    self.id = id
    self.text = text
  
  def set_id(self, id):
    self.id = id
    
  def get_id(self):
    return self.id
    
  def set_text(self, text):
    self.text = text
    
  def get_text(self):
    return self.text