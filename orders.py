class Orders(object):
	"""docstring for Orders"""
	def __init__(self,arg_id,arg_phonenumber, arg_item_id, arg_cust_id, arg_quantity, arg_location, arg_price_per_quantity,arg_delivery_time,arg_item_name):
		super(Orders, self).__init__()
		self.phonenumber = arg_phonenumber
		self.id = str(arg_id)
		self.item_id = arg_item_id
		self.cust_id = arg_cust_id
		self.quantity = arg_quantity
		self.location = arg_location
		self.price_per_quantity = arg_price_per_quantity
		self.delivery_time = arg_delivery_time
		self.approved = '0'
		self.status = '1'
		self.item_name = arg_item_name

	def get_item_name(self):
		return str(self.item_name)

	def set_item_name(self, arg_item_name):
		self.item_name = arg_item_name

	def set_approved(self, arg_approved):
		self.approved = arg_approved
		
	def set_status (self,arg_status):
		self.status = arg_status

	def isApproved(self):
		return int(self.approved) ==1

	def set_delivery_time(self,arg_delivery_time):
		self.delivery_time = arg_delivery_time

	def get_delivery_time(self):
		return str(self.delivery_time)

	def set_location(self, arg_location):
		self.location = arg_location

	def get_location(self):
		return self.location

	def set_phonenumber(self, arg_phonenumber):
		self.phonenumber = arg_phonenumber

	def get_phonenumber(self):
		return str(self.phonenumber)

	def set_id(self, arg_id):
		self.id = arg_id

	def get_id(self):
		return self.id

	def set_item_id(self, arg_item_id):
		self.item_id = arg_item_id

	def get_item_id(self):
		return str(self.item_id)

	def set_cust_id(self, arg_cust_id):
		self.cust_id = arg_cust_id

	def get_cust_id(self):
		return str(self.cust_id)

	def set_quantity(self, arg_quantity):
		self.quantity = arg_quantity

	def get_quantity(self):
		return str(self.quantity)

	def set_price_per_quantity(self, arg_price_per_quantity):
		self.price_per_quantity = arg_price_per_quantity

	def get_price_per_quantity(self):
		return str(self.price_per_quantity)

	def to_string(self):
		return self.id+','+self.item_id+','+self.cust_id+','+self.quantity+','+self.price_per_quantity
