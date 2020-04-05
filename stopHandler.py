import telegram
from telegram.ext import ConversationHandler
from telegram import KeyboardButton,ReplyKeyboardMarkup,ChatAction

from settingsHandler import SettingHandler

CONFIRM = 'confirm'
ENTRY = 'entry'
STOP = 'stop'
END_CONVERSATION = ConversationHandler.END

class StopHandler(object):
	"""docstring for StopHander"""
	def __init__(self, arg_db, arg_updater):
		super(StopHandler, self).__init__()
		self.updater = arg_updater
		self.settings = SettingHandler()
		self.db = arg_db

	def cancel_markup(self):
		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[txt.CMD_CANCEL]]
		return telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

	def entry(self, bot, update):
		msg = bot.send_message(chat_id=update.message.chat_id, text='Enter confirmation code',
			reply_markup=self.cancel_markup())
		self.db.add_msg(msg['message_id'], msg['text'])
		return CONFIRM

	def confirm(self, bot, update):
		code = update.message.text
		if code == '1234':
			for row in self.db.get_messages().fetchall():
				try:
					self.delete_message(bot,update, row[0])
				except Exception as e:
					print(e)
			msg = bot.send_message(chat_id=update.message.chat_id, text='Done')
			self.updater.stop()
			return END_CONVERSATION
		else:
			msg = bot.send_message(chat_id=update.message.chat_id, text='Wrong code', 
				reply_markup=self.cancel_markup())
			self.db.add_msg(msg['message_id'], msg['text'])
			return ENTRY

	def delete_message(self, bot,update, msg_id):
		bot.delete_message(chat_id=update.message.chat_id, message_id=msg_id)
		self.db.delete_message(str(msg_id))

	def cancel(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		msg = bot.send_message(chat_id=update.message.chat_id,  text=txt.TXT_PROCESS_CANCELLED
			, reply_markup = self.settings.settings_menu(bot, update))

		self.db.add_msg(msg['message_id'], msg['text'])
		return END_CONVERSATION

		