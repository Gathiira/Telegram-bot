import telegram
import main_menu as menu
from telegram.ext import ConversationHandler
from telegram import InlineKeyboardButton,InlineKeyboardMarkup,KeyboardButton,ChatAction
import random
import string
import os
import traceback
import config

from orders import Orders
from Language import Lang

# Defining diffirent states
ENTRY = 'entry'
START = 'start'
ORDER_ADDRESS = 'order_address'
ORDER_PICKUP = 'order_pickup'
ORDER_PHONE = 'order_phone'
ORDER_COLLECTION = 'order_collection'
QUANTITY = 'quantity'
REVALIDATE_QUANTITY = 'revalidate_qty'
ORDER_TIME = 'delivery_time'
ADD_ITEM = 'add_item'
ORDER_CONFIRM = 'order_confirm'
ORDER_SEND = 'order_send'
ORDER_LOCATION = 'order_location'
ORDER_SELFIE = 'selfie'
COMMENTS = 'comments'

END_CONVERSATION = ConversationHandler.END

class OrderHandler(object):

	def __init__(self ,arg_db):
		self.db = arg_db
		self.store  = dict()
		self.order_details = dict()

	def items_available(self,item):
		available = False
		if item[3] >=3:
			available = True
		return available

	def items_over(self,items):
		items = self.db.get_items_by_status('1').fetchall()
		items_less =  self.db.get_items_by_quantity().fetchall()
		over = False
		if len(items) == len(items_less):
			over = True
		return over

	def entry_point(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)
		telegram_id  = update.message.from_user.id
		self.store[telegram_id] = {}
		self.order_details[telegram_id] = {}
		self.order_details[telegram_id][0] = {}
		return self.load_items(bot,update)

	def load_items(self,bot,update):
		telegram_id  = update.message.from_user.id
		username = update.message.chat.username
		keyboard = []
		if len(self.db.get_items().fetchall())<=0:
			msg = bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_NO_PRODUCT']
				,reply_markup = menu.main_menu(bot, update))
			self.db.add_msg(msg['message_id'], msg['text'])
			return END_CONVERSATION
		if username == None:
			msg = bot.send_message(chat_id=update.message.chat_id, text = Lang.Lang['English']['TXT_SET_USERNAME'])
			self.db.add_msg(msg['message_id'], msg['text'])
			return END_CONVERSATION

		self.store[telegram_id]['username'] = username
		items = self.db.get_items_by_status('1').fetchall()
		if len(items)>0:
			for item in items:
				if not self.items_over(items):
					if self.items_available(item):
						if item[5] == '1':
							button = [item[1] +' @ '+str(item[4])+'sh']
							keyboard.append(button)
						elif item[3] == 0:
							msg = bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_NO_PRODUCT']
								,reply_markup = menu.main_menu(bot, update))
							self.db.add_msg(msg['message_id'], msg['text'])
						else:
							msg = bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_NO_PRODUCT']
								,reply_markup = menu.main_menu(bot, update))
							self.db.add_msg(msg['message_id'], msg['text'])

							keys = list(self.order_details[telegram_id].keys())
							keys.sort(reverse = True)
							if keys[0]>0:
								telegram.ReplyKeyboardRemove()
								custom_keyboard = [[Lang.Lang['English']['TXT_FINISH'],Lang.Lang['English']['CMD_ADD']]]
								reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
								bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_ADD_ITEM'],
									reply_markup = reply_markup)
								return ADD_ITEM
							else:
								return END_CONVERSATION
					else:
						msg = Lang.Lang['English']['TXT_REPORT_SHORTAGE'].format(item[1],item[3])
						bot.send_message(chat_id = Lang.Lang['English']['ORDER_CHANNEL'], text = msg)
				else:
					keys = list(self.order_details[telegram_id].keys())
					keys.sort(reverse = True)
					if keys[0]>0:
						telegram.ReplyKeyboardRemove()
						custom_keyboard = [[Lang.Lang['English']['TXT_FINISH']]]
						reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
						bot.send_message(chat_id=update.message.chat_id
							,text='No more items to order, click * Finish * to complete order',
							reply_markup = reply_markup)
						return ADD_ITEM
					else:
						msg = bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_NO_PRODUCT']
							,reply_markup = menu.main_menu(bot, update))
						self.db.add_msg(msg['message_id'], msg['text'])
						return END_CONVERSATION

			keyboard.append([Lang.Lang['English']['CMD_CANCEL']])
			reply_markup = telegram.ReplyKeyboardMarkup(keyboard,resize_keyboard=True)
			msg = update.message.reply_text(Lang.Lang['English']['TXT_SELECT_ITEMS'], reply_markup=reply_markup)
			self.db.add_msg(msg['message_id'], msg['text'])
			return START
		else:
			msg = bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_TURN_OFF_TXT'])
			self.db.add_msg(msg['message_id'], msg['text'])
			return END_CONVERSATION

	def start(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)
		telegram.ReplyKeyboardRemove()

		telegram_id  = update.message.from_user.id
		item_name = update.message.text.split(' ')[0]
		price_per_quantity = 20
		item_id = ''
		for row in self.db.get_item_by_name(item_name):
			item_id = row[0]
			price_per_quantity = row[4]

		self.store[telegram_id]['address'] = 'Nakujia'
		self.store[telegram_id]['item_id'] = item_id
		self.store[telegram_id]['item_name'] = item_name
		self.store[telegram_id]['price_per_quantity'] = price_per_quantity
		
		keys = list(self.order_details[telegram_id].keys())
		keys.sort(reverse = True)
		if keys[0]>0:
			keyboard = [[Lang.Lang['English']['TXT_YES']],[Lang.Lang['English']['CMD_CANCEL']]]
			reply_markup = telegram.ReplyKeyboardMarkup(keyboard,resize_keyboard=True)
			msg = bot.send_message(chat_id = update.message.chat_id, text= Lang.Lang['English']['TXT_PREV_DETAILS'],
				reply_markup = reply_markup)
			return ORDER_PICKUP

		msg  = Lang.Lang['English']['TXT_ORDER_INTRO'].format(update.message.chat.first_name)

		custom_keyboard = [[KeyboardButton(text=Lang.Lang['English']['TXT_SHARE_PHONE'], request_contact=True)]
								,[Lang.Lang['English']['CMD_CANCEL']]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
		chatMsg = bot.send_message(chat_id=update.message.chat_id, text=msg, reply_markup=reply_markup)

		self.db.add_msg(chatMsg['message_id'], chatMsg['text'])

		return ORDER_PHONE

	def order_phone(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[Lang.Lang['English']['CMD_CANCEL']]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

		telegram_id = update.message.from_user.id
		self.store[telegram_id]['phone_number'] = update.message.contact.phone_number
		msg = bot.send_message(chat_id = update.message.chat_id, text  = Lang.Lang['English']['TXT_CUST_SELFIE'],
			reply_markup = reply_markup)
		self.db.add_msg(msg['message_id'], msg['text'])
		return ORDER_SELFIE

	def photo(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.UPLOAD_PHOTO)

		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[Lang.Lang['English']['TXT_HOME_DELIVERY'],Lang.Lang['English']['TXT_PICKUP']]
							,[Lang.Lang['English']['CMD_CANCEL']]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

		telegram_id = update.message.from_user.id
		photo_file = bot.getFile(update.message.photo[-1].file_id)
		filename = os.path.join('photos/orders/', '{}.jpg'.format(telegram_id))
		photo_file.download(filename)
		self.store[telegram_id]['photo'] = filename

		bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_ORDER_COLLECTION']
			, reply_markup=reply_markup,parse_mode  = telegram.ParseMode.MARKDOWN)

		return ORDER_COLLECTION

	def order_collection(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		collection  = update.message.text
		telegram_id = update.message.from_user.id
		self.store[telegram_id]['collection'] = collection
		if collection ==Lang.Lang['English']['TXT_HOME_DELIVERY']:
			# request address
			bot.sendChatAction(update.message.chat_id, action=ChatAction.FIND_LOCATION)
			telegram.ReplyKeyboardRemove()
			custom_keyboard = [[Lang.Lang['English']['CMD_CANCEL']]]
			reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
			msg = bot.send_message(chat_id = update.message.chat_id, text  = Lang.Lang['English']['TXT_ADDRESS'],
				reply_markup = reply_markup)
			self.db.add_msg(msg['message_id'], msg['text'])
			return ORDER_ADDRESS

		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[Lang.Lang['English']['CMD_CANCEL'],Lang.Lang['English']['TXT_YES']]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
		msg = bot.send_message(chat_id = update.message.chat_id, text  = Lang.Lang['English']['TXT_PICKUP_INTRO'],
			reply_markup = reply_markup)
		self.db.add_msg(msg['message_id'], msg['text'])
		return ORDER_PICKUP

	def order_pickup(self, bot, update):
		telegram.ReplyKeyboardRemove()
		custom_keyboard = [['5','10','15','20','30','50'],[Lang.Lang['English']['CMD_CANCEL']]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

		telegram_id    = update.message.from_user.id
		item_id = self.store[telegram_id]['item_id']
		num_items = ''
		for item in self.db.get_item_by_id(item_id):
			num_items = item[3]

		msg = Lang.Lang['English']['TXT_QUANTITY'].format(num_items)
		msg = bot.send_message(chat_id = update.message.chat_id, text  = msg,
			reply_markup = reply_markup)
		self.db.add_msg(msg['message_id'], msg['text'])
		return QUANTITY

	def order_address(self, bot, update):
		telegram.ReplyKeyboardRemove()
		custom_keyboard = [['5','10','15','20','30','50'],[Lang.Lang['English']['CMD_CANCEL']]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

		telegram_id    = update.message.from_user.id
		collection = self.store[telegram_id]['collection']
		
		if collection == Lang.Lang['English']['TXT_HOME_DELIVERY']:# and address == 'none'
			self.store[telegram_id]['address'] =  update.message.text

		item_id = self.store[telegram_id]['item_id']
		num_items = ''
		for item in self.db.get_item_by_id(item_id):
			num_items = item[3]
			
		msg = Lang.Lang['English']['TXT_QUANTITY'].format(num_items)
		msg = bot.send_message(chat_id = update.message.chat_id, text  = msg,
			reply_markup = reply_markup)
		self.db.add_msg(msg['message_id'], msg['text'])
		return QUANTITY

	def order_quantity(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[Lang.Lang['English']['TXT_FINISH'],Lang.Lang['English']['CMD_ADD']]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

		try:
			telegram_id    = update.message.from_user.id
			quantity    = update.message.text
			quantity = int(quantity)

			item_id = self.store[telegram_id]['item_id']
			item_name = self.store[telegram_id]['item_name']

			num_items = ''
			for item in self.db.get_item_by_id(item_id):
				num_items = item[3]
			if quantity <= int(num_items):					
				new_quantity = int(num_items)- int(quantity)
				self.store[telegram_id]['quantity'] = quantity

				keys = list(self.order_details[telegram_id].keys())
				keys.sort(reverse = True)				
				count = keys[0] +1
				self.order_details[telegram_id][count] = {}
				self.order_details[telegram_id][count]['item_id'] = item_id
				self.order_details[telegram_id][count]['quantity'] = quantity
				self.order_details[telegram_id][count]['item_name'] = item_name

				self.db.update_item_quantity(new_quantity,item_id)

				msg = bot.send_message(chat_id = update.message.chat_id, text=Lang.Lang['English']['TXT_ADD_ITEM'],
					reply_markup= reply_markup)
				self.db.add_msg(msg['message_id'], msg['text'])
				return ADD_ITEM
			else:
				msg = Lang.Lang['English']['TXT_REMAINING_ITEMS'].format(num_items)
				bot.send_message(chat_id = update.message.chat_id, text  = msg)
				return QUANTITY

		except Exception as e:
			print(traceback.format_exc())
			bot.send_message(chat_id = update.message.chat_id, text  = Lang.Lang['English']['TXT_INVALID_AMOUNT'])
			return QUANTITY

	def add_item(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)
		telegram.ReplyKeyboardRemove()

		if update.message.text == Lang.Lang['English']['TXT_FINISH']:
			custom_keyboard = [[Lang.Lang['English']['TXT_TIME_SOON']],[Lang.Lang['English']['TXT_TIME_2HR']]
				,[Lang.Lang['English']['TXT_TIME_3HR']],[Lang.Lang['English']['CMD_CANCEL']]]
			reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

			msg = bot.send_message(chat_id = update.message.chat_id, text=Lang.Lang['English']['TXT_TIME_INPUT'],
				reply_markup= reply_markup)
			self.db.add_msg(msg['message_id'], msg['text'])
			return ORDER_TIME
		return END_CONVERSATION

	def order_time(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[Lang.Lang['English']['CMD_CANCEL']]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
		telegram_id = update.message.from_user.id
		self.store[telegram_id]['time'] = update.message.text
		bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_ADD_COMMENT'],reply_markup = reply_markup)
		return COMMENTS

	def comments(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[Lang.Lang['English']['CMD_CANCEL'],Lang.Lang['English']['TXT_YES']]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

		telegram_id    = update.message.from_user.id
		comment = update.message.text
		self.store[telegram_id]['comment'] = comment
		phone_number = self.store[telegram_id]['phone_number']
		collection = self.store[telegram_id]['collection']
		address = self.store[telegram_id]['address']
		time = self.store[telegram_id]['time']

		item_name = []
		item_qtt = []
		for user_id, orders in self.order_details.items():
			if user_id == telegram_id:
				keys = list(orders.keys())
				for key in keys:
					if key != 0:
						item_name.append(orders[key]['item_name'])
						item_qtt.append(orders[key]['quantity'])


		total_quantity = sum(item_qtt)
		msg = Lang.Lang['English']['TXT_ORDER_DISP_LINE_1'].format(item_name,item_qtt,phone_number,collection)
		if address != 'Nakujia':
			msg += Lang.Lang['English']['TXT_LOCATION'].format(address)
		msg += Lang.Lang['English']['TXT_ORDER_DISP_LINE_2'].format(total_quantity,menu.calculate_price(total_quantity))
		msg += Lang.Lang['English']['TXT_ORDER_DISP_LINE_3'].format(time,comment)
		msg += Lang.Lang['English']['TXT_ORDER_DISP_LINE_4']
		msg = bot.send_message(chat_id  = update.message.chat_id, text = msg,
				reply_markup = reply_markup,parse_mode  = telegram.ParseMode.MARKDOWN)
		self.db.add_msg(msg['message_id'], msg['text'])
		return ORDER_CONFIRM

	def order_confirm(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		telegram_id = update.message.from_user.id		
		username = self.store[telegram_id]['username']
		order_id =''.join([random.choice(string.ascii_letters + string.digits) for n in range(8)])
		phone_number = self.store[telegram_id]['phone_number']
		address = self.store[telegram_id]['address']
		time = self.store[telegram_id]['time']
		photo = self.store[telegram_id]['photo']
		collection = self.store[telegram_id]['collection']

		if update.message.text== Lang.Lang['English']['TXT_YES']:
			try:
				qty = []
				item_id = []
				item_name = []
				my_orders = self.order_details.pop(telegram_id)
				my_orders.pop(0)
				keys = list(my_orders.keys())				
				for key in keys:
					item_name.append(my_orders[key]['item_name'])
					qty.append(my_orders[key]['quantity'])
					item_id.append(my_orders[key]['item_id'])

				total_quantity = sum(qty)
				order = Orders(order_id,phone_number, item_id,telegram_id,qty
					,address,menu.calculate_price(total_quantity), time,item_name)
				self.db.add_order(order,total_quantity,username)
			except Exception as e:
				print(traceback.format_exc())
				self.cancel(bot, update)
				return END_CONVERSATION
			else:
				order_list_msg = Lang.Lang['English']['TXT_CONFIRM_DISP_1'].format(str(item_name)[1:-1],qty)
				# send to admin
				first_name = update.message.chat.first_name
				comment = self.store[telegram_id]['comment']
				msg  = Lang.Lang['English']['TXT_NEW_ORDER'].format(first_name)
				msg += order_list_msg
				msg += Lang.Lang['English']['TXT_CONFIRM_DISP_2'].format(username,phone_number,collection)
				if address != 'Nakujia':
					msg += Lang.Lang['English']['TXT_LOCATION'].format(address)
				msg += Lang.Lang['English']['TXT_ORDER_DISP_LINE_2'].format(total_quantity,menu.calculate_price(total_quantity))
				msg += Lang.Lang['English']['TXT_ORDER_DISP_LINE_3'].format(time,comment)

				button= [[InlineKeyboardButton(Lang.Lang['English']['TXT_CONFIRM_ORDER'], callback_data = (order_id + ' '+ str(telegram_id) + ' approve_order'))]]
				reply_markup = InlineKeyboardMarkup(button)
				bot.send_photo(chat_id = config.ORDER_CHANNEL, photo = open(photo,'rb'),caption=msg
					,reply_markup = reply_markup)
				msg = bot.send_message(chat_id=update.message.chat_id, text = Lang.Lang['English']['TXT_CONFIRMATION_TEXT']
					, reply_markup = menu.main_menu(bot, update)
					, parse_mode  = telegram.ParseMode.MARKDOWN)
				self.db.add_msg(msg['message_id'], msg['text'])
			return END_CONVERSATION
		return END_CONVERSATION

	def list_customer_orders(self, bot, update,status = '1'):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		counter = 0
		telegram_id = update.message.from_user.id
		orders = self.db.get_orders_by_cust_id(telegram_id).fetchall()
		if len(orders)>0:
			for order in orders:
				order_id, item_id, customer_id, phone_num, quantity, location, price_per_quantity, delivery_time, approved, status,item_name,total_quantity,username = order
				if status == '1':
					counter += 1
					msg = '{}. '.format(counter)+ Lang.Lang['English']['TXT_CONFIRM_DISP_1'].format(item_name,quantity)
					msg += Lang.Lang['English']['TXT_ORDER_DISP_LINE_2'].format(total_quantity,price_per_quantity)
					if location != 'Nakujia':
						msg += Lang.Lang['English']['TXT_LOCATION'].format(location)
					msg +=Lang.Lang['English']['TXT_ORDER_DISP_LINE_5'].format(approved =='1',phone_num,delivery_time)

					keyboard = [[InlineKeyboardButton(Lang.Lang['English']['TXT_CANCEL'], callback_data = order_id + " cancelorder")]]
					reply_markup = InlineKeyboardMarkup(keyboard)
					msg = bot.send_message(chat_id=update.message.chat_id, text=msg,
						reply_markup = reply_markup, parse_mode = telegram.ParseMode.MARKDOWN)
					self.db.add_msg(msg['message_id'], msg['text'])
			if counter == 0:
				msg = bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_NO_ORDER'])
				self.db.add_msg(msg['message_id'], msg['text'])
		else:
			msg = bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_NO_ORDER'])
			self.db.add_msg(msg['message_id'], msg['text'])

		return END_CONVERSATION

	def cancel(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)
		msg = bot.send_message(chat_id = update.message.chat_id,  text  = Lang.Lang['English']['TXT_PROCESS_CANCELLED']
			, reply_markup = menu.main_menu(bot, update)
			,parse_mode  = telegram.ParseMode.MARKDOWN)
		self.db.add_msg(msg['message_id'], msg['text'])

		# for key, order in self.order_details.items():
		# 	item_id = order['item_id']
		# 	quantity = order['quantity']
		# 	for item in self.db.get_item_by_id(item_id):
		# 		self.db.update_item_quantity(int(item[3])+int(quantity),item_id)

		return END_CONVERSATION