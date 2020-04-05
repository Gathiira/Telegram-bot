class Customer(object):
	"""docstring for Customer"""
	def __init__(self,arg_telegram_id = None, arg_id=None, arg_name=None, arg_location=None, 
		arg_language=None, arg_phone=None, arg_fb_link=None, arg_photo=None,arg_id_card=None):
		super(Customer, self).__init__()
		self.name = arg_name
		self.telegram_id = str(arg_telegram_id)
		self.id = arg_id
		self.location = str(arg_location)
		self.language = str(arg_language)
		self.phone = arg_phone
		self.fb_link = arg_fb_link
		self.photo = arg_photo
		self.id_card = arg_id_card
		self.approved = '0'

	def set_telegram_id(self, arg_telegram_id):
		self.telegram_id = str(arg_telegram_id)

	def get_telegram_id(self):
		return self.telegram_id

	def set_id(self, arg_id):
		self.id = arg_id

	def get_id(self):
		return self.id

	def set_name(self, arg_name):
		self.name = arg_name

	def get_name(self):
		return self.name

	def get_location(self):
		return self.location

	def get_language(self):
		return self.language

	def set_phone(self, arg_phone):
		self.phone = arg_phone

	def get_phone(self):
		return self.phone

	def set_fb_link(self, arg_fb_link):
		self.fb_link = arg_fb_link

	def get_fb_link(self):
		return self.fb_link

	def set_photo(self, arg_photo):
		self.photo = arg_photo

	def get_photo(self):
		return self.photo

	def set_id_card(self, arg_id_card):
		self.id_card = arg_id_card

	def get_id_card(self):
		return self.id_card

	def set_approved(self, arg):
		self.approved = str(arg)

	def isApproved(self):
		return int(self.approved) == 1

	def to_string(self):
		return self.id()+','+self.name()+','+self.location+','+self.fb_link+', '+self.phone()
		