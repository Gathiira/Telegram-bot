class Item(object):
	"""docstring for Item"""
	def __init__(self, arg_item_id, arg_name,arg_photo,arg_quantity, arg_price_per_quantity):
		super(Item, self).__init__()
		self.item_id = arg_item_id
		self.name = arg_name
		self.photo = arg_photo
		self.quantity = arg_quantity
		self.price_per_quantity = arg_price_per_quantity

	def set_item_id(self, arg_item_id):
		self.item_id = arg_item_id

	def get_item_id(self):
		return self.item_id

	def set_name(self, arg_name):
		self.name = arg_name

	def get_name(self):
		return self.name

	def set_photo(self, arg_photo):
		self.photo = arg_photo

	def get_photo(self):
		return self.photo

	def set_quantity(self, arg_quantity):
		self.quantity = arg_quantity

	def get_quantity(self):
		return self.quantity

	def set_price_per_quantity(self, arg_price_per_quantity):
		self.price_per_quantity = arg_price_per_quantity

	def get_price_per_quantity(self):
		return self.price_per_quantity

	def to_string(self):
		return self.id+','+self.name+','+self.quantity+','+self.price_per_quantity +','+self.description
		