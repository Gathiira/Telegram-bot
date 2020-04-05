from datetime import datetime
import telegram
from telegram.ext import ConversationHandler
from telegram import KeyboardButton,InlineKeyboardButton,InlineKeyboardMarkup,ReplyKeyboardMarkup,ChatAction
import main_menu as mn
import traceback
import txt

END_CONVERSATION = ConversationHandler.END
SHOPPING_EXPERIENCE = 'shopping_experince'
QUALITY = 'quality'
SERVICES = 'services'
PRICE = 'price'


class MoreHandler():
	def __init__(self, arg_db=None):
		self.db = arg_db

	def start(self,bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		msg = bot.send_message(chat_id=update.message.chat_id
			, text=txt.TXT_MORE_INTRO, reply_markup = self.more_menu(bot, update))
		self.db.add_msg(msg['message_id'], msg['text'])

	def more_menu(self, bot, update):
		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[txt.TXT_FEEDBACK_BTN,txt.TXT_HIST_BTN]
			,[txt.TXT_SAVED_BTN,txt.TXT_COMMUNITY,txt.TXT_MAIN_MENU]]
		return telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

class FeedBack(object):
	def __init__(self, arg_db):
		self.menu = MoreHandler(arg_db)
		self.db = arg_db
		self.store  = dict()
		self.keyboard = [['1','2','3','4','5','6','7','8','9','10'],[txt.CMD_CANCEL]]

	def cancel(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		msg = bot.send_message(chat_id=update.message.chat_id,  text=txt.TXT_PROCESS_CANCELLED
			, reply_markup = mn.main_menu(bot, update))
		self.db.add_msg(msg['message_id'], msg['text'])
		return END_CONVERSATION

	def feedback(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		custom_keyboard = [[txt.CMD_CANCEL]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
		msg = bot.send_message(chat_id = update.message.chat_id,  text = txt.TXT_MORE_DESCRIPTION, 
			reply_markup = reply_markup, parse_mode  = telegram.ParseMode.MARKDOWN)
		self.db.add_msg(msg['message_id'], msg['text'])
		return SHOPPING_EXPERIENCE

	def shopping_experince(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		reply_markup = telegram.ReplyKeyboardMarkup(self.keyboard, resize_keyboard=True)
		telegram_id  = update.message.from_user.id
		self.store[telegram_id] = {}
		self.store[telegram_id]['shopping_experince'] = update.message.text
		msg = bot.send_message(chat_id = update.message.chat_id,  text = txt.TXT_RATE_QUALITY, 
			reply_markup = reply_markup, parse_mode  = telegram.ParseMode.MARKDOWN)
		self.db.add_msg(msg['message_id'], msg['text'])
		return QUALITY 

	def quality(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		reply_markup = telegram.ReplyKeyboardMarkup(self.keyboard, resize_keyboard=True)

		telegram_id  = update.message.from_user.id
		self.store[telegram_id]['quality'] = update.message.text
		msg = bot.send_message(chat_id = update.message.chat_id,  text = txt.TXT_RATE_SERVICE, 
			reply_markup = reply_markup , parse_mode  = telegram.ParseMode.MARKDOWN)
		self.db.add_msg(msg['message_id'], msg['text'])
		return SERVICES 

	def services(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		reply_markup = telegram.ReplyKeyboardMarkup(self.keyboard, resize_keyboard=True)

		telegram_id  = update.message.from_user.id
		self.store[telegram_id]['services'] = update.message.text
		msg = bot.send_message(chat_id = update.message.chat_id,  text = txt.TXT_RATE_PRICE, 
			reply_markup = reply_markup, parse_mode  = telegram.ParseMode.MARKDOWN)
		self.db.add_msg(msg['message_id'], msg['text'])
		return PRICE

	def price(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)
		telegram.ReplyKeyboardRemove()
		try:
			telegram_id  = update.message.from_user.id
			price= update.message.text
			services = self.store[telegram_id]['services']
			experience = self.store[telegram_id]['shopping_experince']
			quality = self.store[telegram_id]['quality']
			total_feeback = len(self.db.get_all_feedback().fetchall())+1

			name = ''
			for user in self.db.get_cust(telegram_id).fetchall():				
				name = user[2]

			msg = txt.TXT_FEEDBACK_DISP_1.format(name,datetime.now().strftime('%Y-%m-%d'),total_feeback)
			msg += txt.TXT_FEEDBACK_DISP_2.format(experience,quality,services,price)
			self.db.add_feedback(telegram_id,msg)
		except Exception as e:
			print(traceback.format_exc())
			self.cancel(bot, update)
			END_CONVERSATION
		else:			
			bot.send_message(chat_id = txt.ORDER_CHANNEL, text=msg)
			msg = bot.send_message(chat_id=update.effective_user.id, text=txt.TXT_FEEDBACK_SENT, 
				reply_markup=mn.main_menu(bot, update,telegram_id))
			self.db.add_msg(msg['message_id'], msg['text'])
			return END_CONVERSATION	
		END_CONVERSATION
 