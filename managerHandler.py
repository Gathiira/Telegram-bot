import telegram
from telegram.ext import ConversationHandler
from telegram import InlineKeyboardButton,InlineKeyboardMarkup,ChatAction
import main_menu as menu
from orderHandler import OrderHandler
import traceback
import txt

END_CONVERSATION = ConversationHandler.END
REMOVE_ADMIN = 'remove_admin'
CONFIRM_NAME = 'confirm_name'

class ManagerHandler(object):
	"""docstring for ManagerHandler"""
	def __init__(self,arg_db):
		self.db = arg_db

	def start(self,bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		msg = bot.send_message(chat_id=update.message.chat_id
			, text=txt.TXT_MANAGER_INTRO, reply_markup = self.manager_menu(bot, update))
		self.db.add_msg(msg['message_id'], msg['text'])

	def manager_menu(self, bot, update):
		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[txt.TXT_REMOVE_ADMIN,txt.TXT_ADD_ADMIN],[txt.TXT_STOP_BOT,txt.TXT_SETTINGS_MENU]]
		return telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)


class NewAdmin(object):
	"""docstring for NewAdmin"""
	def __init__(self, arg_db):
		self.manager = ManagerHandler(arg_db)
		self.db = arg_db

	def cancel(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		msg = bot.send_message(chat_id=update.message.chat_id,  text=txt.TXT_PROCESS_CANCELLED
			, reply_markup = self.manager.manager_menu(bot, update))
		self.db.add_msg(msg['message_id'], msg['text'])
		return END_CONVERSATION

	def add(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[txt.CMD_CANCEL]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

		msg = bot.send_message(chat_id=update.message.chat_id,text=txt.TXT_MANAGER_ID
			, reply_markup = reply_markup)
		self.db.add_msg(msg['message_id'], msg['text'])
		return CONFIRM_NAME

	def confirm_name(self,bot,update):
		telegram_id  = update.message.text
		users = self.db.get_cust(telegram_id).fetchall()
		if len(users)>0:
			for user in users:				
				if user[0] not in menu.ADMINS:
					menu.ADMINS.append(user[0])
					bot.send_message(chat_id=update.message.chat_id,  text=txt.TXT_ADD_ADMIN_SUCCESS.format(telegram_id),
						reply_markup = self.manager.manager_menu(bot, update))
					bot.send_message(chat_id=user[0],  text=txt.TXT_SENT_TEXT
						,reply_markup = menu.main_menu(bot, update))
				else:
					bot.send_message(chat_id=update.message.chat_id,  text=txt.TXT_USER_ALREADY_ADMIN,
						reply_markup = self.manager.manager_menu(bot, update))
					self.cancel(bot,update)
					return END_CONVERSATION
		else:
			bot.send_message(chat_id=update.message.chat_id,  text=txt.TXT_USER_NOT_FOUND,
				reply_markup = self.manager.manager_menu(bot, update))
			self.cancel(bot,update)
			return END_CONVERSATION		
		return END_CONVERSATION

class RemoveAdmin(object):
	"""docstring for NewAdmin"""
	def __init__(self, arg_db):
		self.manager = ManagerHandler(arg_db)
		self.db = arg_db

	def cancel(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		msg = bot.send_message(chat_id=update.message.chat_id,  text=txt.TXT_PROCESS_CANCELLED
			, reply_markup = self.manager.manager_menu(bot, update))
		self.db.add_msg(msg['message_id'], msg['text'])
		return END_CONVERSATION

	def add(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[txt.CMD_CANCEL]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

		msg = bot.send_message(chat_id=update.message.chat_id,  text=txt.TXT_MANAGER_ID
			, reply_markup = reply_markup)
		self.db.add_msg(msg['message_id'], msg['text'])
		return REMOVE_ADMIN

	def remove_admin(self,bot,update):
		telegram_id  = update.message.text
		users = self.db.get_cust(telegram_id).fetchall()
		if len(users)>0:
			for user in users:				
				if user[0] != 768103930:
					menu.ADMINS.remove(user[0])
					bot.send_message(chat_id=update.message.chat_id,  text=txt.TXT_REMOVE_ADMIN_SUCCESS.format(telegram_id),
						reply_markup = self.manager.manager_menu(bot, update))
					bot.send_message(chat_id=user[0],  text=txt.TXT_REMOVED_ADMIN_TEXT
						,reply_markup = menu.main_menu(bot, update))
				else:
					bot.send_message(chat_id=update.message.chat_id,  text=txt.TXT_FUCK_YOU,
						reply_markup = self.manager.manager_menu(bot, update))
					self.cancel(bot,update)
					return END_CONVERSATION
		else:
			bot.send_message(chat_id=update.message.chat_id,  text=txt.TXT_USER_NOT_FOUND,
				reply_markup = self.manager.manager_menu(bot, update))
			self.cancel(bot,update)
			return END_CONVERSATION	
		return END_CONVERSATION