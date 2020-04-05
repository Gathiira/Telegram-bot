import os
import telegram
from telegram.ext import ConversationHandler
from telegram import ChatAction
from item import Item
from tabulate import tabulate
import random
import string
import reviewHandler
import config

from Language import Lang
from productHandler import ProductHandler

ITEM_NAME = 'item_name'
ITEM_ID = 'item_id'
ITEM_PHOTO = 'item_photo'
ITEM_DESCRIPTION = 'description'
ITEM_QUANTITY = 'item_quantity'
REGISTER = 'register'
DELETE = 'delete'
ITEM_PRICE = 'item_price'
END_CONVERSATION = ConversationHandler.END

class ItemHandler():
	def __init__(self,arg_db):
		self.product = ProductHandler(arg_db)
		self.store = dict()
		self.db = arg_db

	def new_item(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[Lang.Lang['English']['CMD_CANCEL']]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

		telegram_id = update.message.from_user.id
		item_id =''.join([random.choice(string.ascii_letters + string.digits) for n in range(8)])
		self.store[telegram_id] = {}
		self.store[telegram_id]['item_id']  = item_id
		msg = bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_PRODUCT_NAME'], reply_markup=reply_markup)
		self.db.add_msg(msg['message_id'], msg['text'])
		return  ITEM_NAME

	def name(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[Lang.Lang['English']['CMD_CANCEL']]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

		item_nem = []
		for item in self.db.get_items().fetchall():
			item_nem.append(item[1].lower())

		item_name = update.message.text
		if item_name.lower() not in item_nem:
			telegram_id = update.message.from_user.id
			self.store[telegram_id]['item_name']  = item_name.capitalize()
			bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_PRODUCT_TYPE']
				, reply_markup=reply_markup)
			return ITEM_PRICE
		bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_PRODUCT_NAME_ERR'])
		return ITEM_PRICE

	def item_price(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[Lang.Lang['English']['CMD_CANCEL']]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

		telegram_id  = update.message.from_user.id
		self.store[telegram_id]['item_price']   = update.message.text
		bot.send_message(chat_id = update.message.chat_id,text = Lang.Lang['English']['TXT_PRODCUT_IMAGE']
			,reply_markup = reply_markup)
		return ITEM_PHOTO

	def photo(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.UPLOAD_PHOTO)

		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[Lang.Lang['English']['CMD_CANCEL']]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

		telegram_id = update.message.from_user.id
		photo_file = bot.getFile(update.message.photo[-1].file_id)
		filename = os.path.join('items', '{}.jpg'.format(str(self.store[telegram_id]['item_name'])))
		photo_file.download(filename)
		self.store[telegram_id]['photo'] = filename
		bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_PRODUCT_DES']
			,reply_markup=reply_markup
			,parse_mode = telegram.ParseMode.MARKDOWN )
		return ITEM_DESCRIPTION

	def description(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[Lang.Lang['English']['CMD_CANCEL']]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

		telegram_id  = update.message.from_user.id
		description = update.message.text
		self.store[telegram_id]['description']   = description
		bot.send_message(chat_id = update.message.chat_id,text = Lang.Lang['English']['TXT_PRODUCT_QTT']
			,reply_markup = reply_markup)
		return ITEM_QUANTITY

	def quantity(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[Lang.Lang['English']['CMD_CANCEL'],Lang.Lang['English']['CMD_ADD']]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

		telegram_id  = update.message.from_user.id
		quantity = update.message.text
		self.store[telegram_id]['quantity']   = quantity

		item_name   = self.store[telegram_id]['item_name']
		photo  = self.store[telegram_id]['photo']
		description =  self.store[telegram_id]['description']
		item_price = self.store[telegram_id]['item_price']

		data = [item_name,item_price,quantity,description]
		labels=[Lang.Lang['English']['TXT_NAME'],'@ Blant :',Lang.Lang['English']['TXT_QTT']
			,Lang.Lang['English']['TXT_DES']]
		table=zip(labels,data)
		listing=tabulate(table,tablefmt="plain")

		bot.send_photo(chat_id=update.message.chat_id, photo=open(photo,'rb'), caption = listing)
		bot.send_message(chat_id = update.message.chat_id,text = Lang.Lang['English']['TXT_PRODUCT_CLICK_ADD']
			,reply_markup = reply_markup,parse_mode  = telegram.ParseMode.MARKDOWN)
		return REGISTER

	def register(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		telegram_id    = update.message.from_user.id
		item_name   = self.store[telegram_id]['item_name']
		photo  = self.store[telegram_id]['photo']
		description =  self.store[telegram_id]['description']
		item_quantity = self.store[telegram_id]['quantity']
		item_id = self.store[telegram_id]['item_id']
		item_price = self.store[telegram_id]['item_price']

		data = [item_name,item_quantity,description]
		labels=[Lang.Lang['English']['TXT_NAME'],Lang.Lang['English']['TXT_QTT']
			,Lang.Lang['English']['TXT_DES']]
		table=zip(labels,data)
		listing=tabulate(table,tablefmt="plain")

		item = Item(item_id, item_name,photo,item_quantity,item_price)
		self.db.add_item(item,description,'item_kind')

		msg =Lang.Lang['English']['TXT_ITEM_DISP_1'].format(item_name,item_price,description)
		bot.send_photo(chat_id = config.ITEMS_CHANNEL, photo=open(photo,'rb'),
			caption=msg, reply_markup=reviewHandler.reply_markup(self.db, item_id))

		bot.send_message(chat_id=update.message.chat_id, text = Lang.Lang['English']['TXT_PRODUCT_ADDED']
			,reply_markup = self.product.product_menu(bot, update))
		self.store.pop(telegram_id)
		return END_CONVERSATION

	def cancel(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		bot.send_message(chat_id=update.message.chat_id,  text=Lang.Lang['English']['TXT_PROCESS_CANCELLED']
			, reply_markup = self.product.product_menu(bot, update))
		self.store.pop(update.message.chat_id)
		return END_CONVERSATION

