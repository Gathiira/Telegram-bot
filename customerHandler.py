import os
import telegram
import main_menu as menu
from telegram.ext import ConversationHandler
from telegram import KeyboardButton,InlineKeyboardButton,InlineKeyboardMarkup,ChatAction
from customer import Customer
from tabulate import tabulate
import traceback
import config

from Language import Lang

TERMS = 'terms'
NEW_CUSTOMER = 'new_customer'
CUSTOMER_ID_CARD = 'customer_id_card'
CUSTOMER_PAYSLIP = 'cutomer_payslip'
CUSTOMER_NAME = 'customer_name'
CUSTOMER_PHONE = 'customer_phone'
CUSTOMER_ID_NUMBER = 'customer_id_number'
CUSTOMER_PHOTO = 'customer_photo'
CUSTOMER_LINK = 'customer_link'
CUSTOMER_LOC = 'customer_loc'
CUSTOMER_SEND = 'customer_send'
REGISTER = 'customer_register'
INLINE_KEYBOARD = 'inline_keyboard'
END_CONVERSATION = ConversationHandler.END

'''
====================================================
The Customer ConversationHandler Abstraction for the
bot.
====================================================
'''

class CustomerHandler():
	def __init__(self, arg_bot, arg_db):
		self.store = dict()
		self.bot = arg_bot
		self.db = arg_db

	def new_customer(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		telegram_id = update.message.from_user.id
		first_name = update.message.chat.first_name
		username = update.message.chat.username

		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[Lang.Lang['English']['TXT_YES']],[Lang.Lang['English']['CMD_CANCEL']]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

		self.store[telegram_id] = {}
		self.store[telegram_id]['first_name'] = first_name
		if username != None:
			self.store[telegram_id]['username'] = username
			msg  = Lang.Lang['English']['TXT_CUST_WELCOME'].format(first_name)
			bot.send_message(chat_id=update.message.chat_id, text=msg, reply_markup=reply_markup)
			return  TERMS
		msg = bot.send_message(chat_id=update.message.chat_id, text = Lang.Lang['English']['TXT_SET_USERNAME'])
		self.db.add_msg(msg['message_id'], msg['text'])
		return END_CONVERSATION

	def terms_n_condition(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[Lang.Lang['English']['CMD_CANCEL']]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

		if update.message.text ==Lang.Lang['English']['TXT_YES']:
			bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_CUST_NAME'], reply_markup=reply_markup)
			return  CUSTOMER_NAME

	def name(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[KeyboardButton(text=Lang.Lang['English']['TXT_SHARE_PHONE']
			, request_contact=True)],[Lang.Lang['English']['CMD_CANCEL']]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

		telegram_id = update.message.from_user.id
		self.store[telegram_id]['last_name']  = update.message.text

		if menu.is_registered(bot, update):
			bot.send_message(chat_id = update.message.chat_id,text  = Lang.Lang['English']['TXT_ALREADY_REGISTERED'],
				reply_markup = self.show_main_menu(bot, update))
			
			return END_CONVERSATION

		bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_CUST_PHONE']
			,reply_markup=reply_markup)
		return CUSTOMER_PHONE

	def order_phone(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[Lang.Lang['English']['CMD_CANCEL']]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

		telegram_id    = update.message.from_user.id
		phone_number = update.message.contact.phone_number
		self.store[telegram_id]['phone_number'] = phone_number

		bot.send_message(chat_id = update.message.chat_id, text  = Lang.Lang['English']['TXT_CUST_SELFIE'],
			reply_markup = reply_markup)
		return CUSTOMER_PHOTO

	# def id_number(self, bot, update):
	# 	bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

	# 	telegram.ReplyKeyboardRemove()
	# 	custom_keyboard = [[Lang.Lang['English']['CMD_CANCEL']]]
	# 	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

	# 	cust_id = update.message.text
	# 	telegram_id = update.message.from_user.id
	# 	if len(str(cust_id)) >=8:
	# 		self.store[telegram_id]['id'] = cust_id
	# 		bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_CUST_SELFIE'], reply_markup=reply_markup)
	# 		return  CUSTOMER_PHOTO

	# 	bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_ID_NUMBER_ERROR'], reply_markup=reply_markup)
	# 	return  CUSTOMER_ID_NUMBER

	def photo(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.UPLOAD_PHOTO)

		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[Lang.Lang['English']['CMD_CANCEL']]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

		telegram_id = update.message.from_user.id
		photo_file = bot.getFile(update.message.photo[-1].file_id)
		filename = os.path.join('photos/passports', '{}.jpg'.format(telegram_id))
		photo_file.download(filename)
		self.store[telegram_id]['photo'] = filename

		bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_CUST_LOC'], reply_markup=reply_markup)
		return CUSTOMER_LOC

	# def photo_id_card(self, bot, update):
	# 	bot.sendChatAction(update.message.chat_id, action=ChatAction.UPLOAD_PHOTO)

	# 	telegram.ReplyKeyboardRemove()
	# 	custom_keyboard = [[Lang.Lang['English']['CMD_CANCEL']]]
	# 	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

	# 	telegram_id = update.message.from_user.id
	# 	photo_file = bot.getFile(update.message.photo[-1].file_id)
	# 	filename = os.path.join('photos/id_cards', '{}.jpg'.format(telegram_id))
	# 	photo_file.download(filename)
	# 	self.store[telegram_id]['id_card'] = filename

	# 	bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_FB_LINK'], reply_markup=reply_markup)
	# 	return CUSTOMER_LINK

	# def facebook_link(self, bot, update):
	# 	bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

	# 	telegram.ReplyKeyboardRemove()
	# 	custom_keyboard = [[Lang.Lang['English']['CMD_CANCEL']]]
	# 	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

	# 	telegram_id  = update.message.from_user.id
	# 	link = update.message.text

	# 	if menu.is_valid_url(link):
	# 		self.store[telegram_id]['link']   = link
	# 		bot.send_message(chat_id = update.message.chat_id,
	# 			text = Lang.Lang['English']['TXT_CUST_LOC'],reply_markup = reply_markup)
	# 		return CUSTOMER_LOC
	# 	bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_FB_LINK_ERROR'], reply_markup=reply_markup)
	# 	return  CUSTOMER_LINK

	def save_location(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.FIND_LOCATION)

		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[Lang.Lang['English']['CMD_CANCEL'],Lang.Lang['English']['CMD_REGISTER']]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

		telegram_id    = update.message.from_user.id
		self.store[telegram_id]['location'] = update.message.text
		last_name   = self.store[telegram_id]['last_name']
		first_name  = self.store[telegram_id]['first_name']
		# cust_id          = self.store[telegram_id]['id']
		# link        = self.store[telegram_id]['link']
		phone_number = self.store[telegram_id]['phone_number']
		location = self.store[telegram_id]['location']

		data = [last_name,location,phone_number]
		labels=[Lang.Lang['English']['TXT_LNAME'],Lang.Lang['English']['TXT_LOC'],Lang.Lang['English']['TXT_PHONE_NO']]
		table=zip(labels,data)
		list=tabulate(table,tablefmt="plain")
		bot.send_message(chat_id=update.message.chat_id,text=list)

		bot.send_message(chat_id = update.message.chat_id, text  = Lang.Lang['English']['TXT_CUST_CONFIRM'],
			 reply_markup = reply_markup,
			 parse_mode  = telegram.ParseMode.MARKDOWN)
		return REGISTER

	def register(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		try:
			telegram_id = update.message.from_user.id
			last_name   = self.store[telegram_id]['last_name']
			first_name  = self.store[telegram_id]['first_name']
			# cust_id          = self.store[telegram_id]['id']
			photo       = self.store[telegram_id]['photo']
			# link        = self.store[telegram_id]['link']
			location = self.store[telegram_id]['location']
			# id_card     = self.store[telegram_id]['id_card']
			phone_number = self.store[telegram_id]['phone_number']
			username = self.store[telegram_id]['username']

			customer = Customer(telegram_id,'cust_id', first_name+" "+last_name, location, 'English', phone_number,
				'link', photo,'id_card')
			self.db.add_customer(customer)
		except Exception as e:
			print(traceback.format_exc())
			self.cancel(bot, update)  
		else:
			# send to admin
			msg  = Lang.Lang['English']['TXT_DISP_1'].format(telegram_id)
			msg += Lang.Lang['English']['TXT_DISP_2'].format(first_name, last_name)
			msg += Lang.Lang['English']['TXT_DISP_3'].format(location,phone_number,username)

			button= [[InlineKeyboardButton(Lang.Lang['English']['TXT_CONFIRM_CUSTOMER'], callback_data = str(telegram_id) +' approve_customer')]]
			reply_markup = InlineKeyboardMarkup(button)
			bot.send_photo(chat_id = config.CUSTOMER_CHANNEL, photo = open(photo,'rb'), caption=msg
				,reply_markup = reply_markup)
			
			bot.send_message(chat_id=update.message.chat_id, text = Lang.Lang['English']['TXT_CONFIRM_TEXT']
				,reply_markup = self.show_main_menu(bot, update))			    
			self.store.pop(telegram_id)
		return END_CONVERSATION

	def cancel(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		bot.send_message(chat_id=update.message.chat_id,  text=Lang.Lang['English']['TXT_PROCESS_CANCELLED']
			,reply_markup = self.show_main_menu(bot, update))
		self.store.pop(update.message.chat_id)		
		return END_CONVERSATION

	def show_main_menu(self, bot, update):
		reply_markup = menu.main_menu_unregistered(bot, update)
		if menu.is_registered(bot, update):
			reply_markup = menu.main_menu(bot, update)
		return reply_markup
		
