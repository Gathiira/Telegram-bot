import telegram
from telegram.ext import ConversationHandler
from telegram import InlineKeyboardButton,InlineKeyboardMarkup,ChatAction
import main_menu as menu
from orderHandler import OrderHandler
import traceback
import txt

END_CONVERSATION = ConversationHandler.END
EDIT_ITEM = 'edit_item'
ITEM_QUANTITY = 'item_quantiy'

class ProductHandler(object):
	"""docstring for ProductHandler"""
	def __init__(self,arg_db):
		self.db = arg_db

	def start(self,bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		msg = bot.send_message(chat_id=update.message.chat_id
			, text=txt.TXT_PRODUCT_INTRO, reply_markup = self.product_menu(bot, update))
		self.db.add_msg(msg['message_id'], msg['text'])

	def product_menu(self, bot, update):
		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[txt.TXT_ADD_ITEM_BTN,txt.TXT_EDIT_ITEM]
			,[txt.TXT_TURN_ON,txt.TXT_TURN_OFF]
			,[txt.TXT_DELETE_ITEM,txt.TXT_SETTINGS_MENU]]
		return telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

	def delete(self, bot, update):
		items = self.db.get_items().fetchall()
		if len(items)>0:
			update.message.reply_text(txt.TXT_SELECT_PRODUCT,
				reply_markup=self.delete_reply_markup(items))
		else:
			msg = bot.send_message(chat_id=update.message.chat_id, text=txt.TXT_NO_PRODUCT)
			self.db.add_msg(msg['message_id'], msg['text'])
			return END_CONVERSATION

	def delete_reply_markup(self, items):
		keyboard = []
		for item in items:
			keyboard.append([InlineKeyboardButton(item[1], callback_data = item[0]),
				InlineKeyboardButton(txt.TXT_DELETE_ITEM_TXT, callback_data = item[0] + ' delete_item')])
		return InlineKeyboardMarkup(keyboard)

	def order_option(self, bot, update):
		items = self.db.get_items().fetchall()
		if len(items)>0:
			update.message.reply_text(txt.TXT_SELECT_PRODUCT,
				reply_markup=self.order_option_reply_markup(items))
		else:
			msg = bot.send_message(chat_id=update.message.chat_id, text=txt.TXT_NO_PRODUCT)
			self.db.add_msg(msg['message_id'], msg['text'])
			return END_CONVERSATION

	def order_option_reply_markup(self, items):
		keyboard = []
		for item in items:
			if item[5] =='1':
				keyboard.append([InlineKeyboardButton(item[1], callback_data = (item[0])),
					InlineKeyboardButton(txt.TXT_TURN_OFF_ITEM, callback_data = item[0]  + " off")])
			else:
				keyboard.append([InlineKeyboardButton(item[1], callback_data = (item[0])),
					InlineKeyboardButton(txt.TXT_TURN_ON_ITEM, callback_data = item[0]  + " on")])
		return InlineKeyboardMarkup(keyboard)

	def turn_off_ordering(self,bot,update):
		users   = self.db.get_verified_cust().fetchall()
		if users:
			for user in users:	
				msg = bot.send_message(user[0], text=txt.TXT_TURN_OFF_TXT)
				self.db.add_msg(msg['message_id'], msg['text'])
		items = self.db.get_items().fetchall()
		self.db.change_ordering_option('2')

	def turn_on_ordering(self,bot,update):
		users   = self.db.get_verified_cust().fetchall()
		if users:
			for user in users:				
				msg = bot.send_message(user[0], text=txt.TXT_TURN_ON_TXT)
				self.db.add_msg(msg['message_id'], msg['text'])
		self.db.change_ordering_option('1')

class EditItem(object):
	"""docstring for EditItem"""
	def __init__(self, arg_db):
		self.product = ProductHandler(arg_db)
		self.db = arg_db
		self.store = dict()

	def cancel(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		msg = bot.send_message(chat_id=update.message.chat_id,  text=txt.TXT_PROCESS_CANCELLED
			, reply_markup = self.product.product_menu(bot, update))
		self.db.add_msg(msg['message_id'], msg['text'])

		return END_CONVERSATION

	def add(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[txt.CMD_CANCEL]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

		msg = bot.send_message(chat_id=update.message.chat_id,  text=txt.TXT_PRODUCT_NAME
			, reply_markup = reply_markup)
		self.db.add_msg(msg['message_id'], msg['text'])
		return EDIT_ITEM

	def edit_item(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[txt.CMD_CANCEL]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

		item_name = update.message.text
		item_name = item_name.capitalize()
		item_nem = []
		item_id = ''
		item_qtt = 0
		for item in self.db.get_items().fetchall():
			item_nem.append(item[1].capitalize())
		if item_name.capitalize() not in item_nem:
			msg  = txt.TXT_NO_ITEM.format(item_name)
			bot.send_message(chat_id=update.message.chat_id, text=msg)
			return EDIT_ITEM
		for item in self.db.get_item_by_name(item_name).fetchall():
			item_id = item[0]
			item_qtt = item[3]

		telegram_id = update.message.from_user.id
		self.store[telegram_id] = {}
		self.store[telegram_id]['item_id']  = item_id
		msg  = txt.TXT_UPDATE_ITEMS.format(item_qtt)
		bot.send_message(chat_id=update.message.chat_id, text=msg, reply_markup=reply_markup)
		return ITEM_QUANTITY

	def item_quantiy(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)
		telegram_id = update.message.from_user.id
		quantity = update.message.text
		item_id = self.store[telegram_id]['item_id']

		try:
			self.db.update_item_quantity(quantity,item_id)
			bot.send_message(chat_id=update.message.chat_id, text = txt.TXT_ITEM_QTT
				,reply_markup=self.product.product_menu(bot, update))

			return END_CONVERSATION
		except Exception as e:
			print(traceback.format_exc())
			bot.send_message(chat_id=update.message.chat_id, text = txt.TXT_PROCESS_CANCELLED)
			self.cancel(bot,update)
			return END_CONVERSATION
		return END_CONVERSATION
		