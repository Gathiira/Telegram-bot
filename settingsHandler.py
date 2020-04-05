import telegram
from telegram.ext import ConversationHandler
from telegram import InlineKeyboardButton,InlineKeyboardMarkup,ChatAction
import main_menu as menu
from orderHandler import OrderHandler
import traceback
import txt

END_CONVERSATION = ConversationHandler.END
SEND = 'send'

class SettingHandler():
	def __init__(self, arg_db=None):
		self.db = arg_db
		self.order  = OrderHandler(arg_db)

	def start(self,bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		msg = bot.send_message(chat_id=update.message.chat_id
			, text=txt.TXT_SETTINGS_INTRO, reply_markup = self.settings_menu(bot, update))
		self.db.add_msg(msg['message_id'], msg['text'])

	def settings_menu(self, bot, update):
		telegram.ReplyKeyboardRemove()
		custom_keyboard = [[txt.TXT_PRODUCT,txt.TXT_MANAGER],[txt.TXT_ORDER_OPTION,txt.TXT_REVIEWS]
			,[txt.TXT_BLOCK_USERS,txt.TXT_STATISTICS]
			,[txt.TXT_BROADCAST,txt.TXT_MAIN_MENU]]
		return telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

	def approve_reply_markup(self,users):
		keyboard = []
		for user in users:
			keyboard.append([InlineKeyboardButton(user[1], callback_data = user[0]),
				InlineKeyboardButton(txt.TXT_DELETE_PRODUCT, callback_data = item[0])])
		return InlineKeyboardMarkup(keyboard)

	def block_reply_markup(self, users):
		keyboard = []
		for user in users:
			if user[0] != 768103930:
				if menu.is_blocked(user[0]):
					keyboard.append([InlineKeyboardButton(user[2], callback_data=(str(user[0]) + ' unblock')),
						InlineKeyboardButton('UnBlock', callback_data=(str(user[0]) + ' unblock'))])
				else:
					keyboard.append([InlineKeyboardButton(user[2], callback_data=(str(user[0]) + ' block')),
						InlineKeyboardButton('Block', callback_data=(str(user[0]) + ' block'))])
		return InlineKeyboardMarkup(keyboard)

	def block(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)
		users = self.db.get_all_custs().fetchall()

		if len(users)>0:
			msg = update.message.reply_text(txt.TXT_SETTINGS_BLOCK, reply_markup=self.block_reply_markup(users))
			self.db.add_msg(msg['message_id'], msg['text'])
		else:
			msg = update.message.reply_text(txt.TXT_SETT_NO_CUST)
			self.db.add_msg(msg['message_id'], msg['text'])
			return END_CONVERSATION

	def statistics(self,bot, update,clicks):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)
		cust = len(self.db.get_all_custs().fetchall())
		orders = self.db.get_orders().fetchall()
		cancelled_orders = self.db.get_orders_by_status('0').fetchall()
		completed_orders = self.db.get_orders_by_status('2').fetchall()
		pending_orders = self.db.get_orders_by_status('1').fetchall()
		order_id = ''
		for order in orders:
			order_id = order[0]
		items = len(self.db.get_items().fetchall())
		msg = txt.TXT_STATS_DISP_1.format(clicks,cust)
		msg += txt.TXT_STATS_DISP_2.format(len(orders),items)
		cancelled_txt = txt.TXT_STATS_CANCELLED_ORDERS + '({})'.format(len(cancelled_orders))
		completed_txt = txt.TXT_STATS_COMPLETED_ORDERS + '({})'.format(len(completed_orders))
		pending_txt = txt.TXT_STATS_PENDING_ORDERS + '({})'.format(len(pending_orders))
		button= [
			[InlineKeyboardButton(cancelled_txt, callback_data=order_id+ " order list_cancelled_orders"),
			InlineKeyboardButton(completed_txt, callback_data=order_id+ " order list_completed_orders")],
			[InlineKeyboardButton(pending_txt, callback_data=order_id+ " order list_pending_orders"),
			InlineKeyboardButton(txt.TXT_STATS_BEST_CUST, callback_data=order_id+ " order best_cust")]]

		reply_markup = InlineKeyboardMarkup(button)
		msg = bot.send_message(chat_id  = update.message.chat_id, text = msg,
			reply_markup = reply_markup)
		self.db.add_msg(msg['message_id'], msg['text'])

class Send(object):
	def __init__(self, arg_db):
		self.settings = SettingHandler(arg_db)
		self.db = arg_db

	def cancel(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		msg = bot.send_message(chat_id=update.message.chat_id,  text=txt.TXT_PROCESS_CANCELLED
			, reply_markup = self.settings.settings_menu(bot, update))
		self.db.add_msg(msg['message_id'], msg['text'])
		return END_CONVERSATION

	def broadcast(self, bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		custom_keyboard = [[txt.CMD_CANCEL]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
		msg = bot.send_message(chat_id = update.message.chat_id,  text = txt.TXT_BROADCAST_TO_USERS,
			reply_markup = reply_markup)
		self.db.add_msg(msg['message_id'], msg['text'])
		return SEND

	def send(self,bot, update):
		bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

		telegram.ReplyKeyboardRemove()

		users   = self.db.get_verified_cust().fetchall()
		if users:
			for user in users:
				id = user[0]
				if id != update.effective_user.id:
					bot.send_message(id, text  = update.message.text)
		msg = bot.send_message(chat_id=update.message.chat_id, text=txt.TXT_MESSAGE_SENT,
			reply_markup=self.settings.settings_menu(bot, update))
		self.db.add_msg(msg['message_id'], msg['text'])
		return END_CONVERSATION


			
		
