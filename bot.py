import traceback
import telegram
from telegram.ext import Updater,RegexHandler,CommandHandler,MessageHandler,Filters,CallbackQueryHandler,ConversationHandler
from telegram import InlineKeyboardButton,InlineKeyboardMarkup,ChatAction
import logging
import requests
import ast
from tabulate import tabulate
import operator
import config
from collections import Counter

import main_menu as menu
from DbManager import DatabaseManager
import reviewHandler as reviews

import customerHandler
from customerHandler import CustomerHandler

import settingsHandler
from settingsHandler import SettingHandler
from settingsHandler import Send

import managerHandler
from managerHandler import ManagerHandler
from managerHandler import NewAdmin
from managerHandler import RemoveAdmin

import productHandler
from productHandler import ProductHandler
from productHandler import EditItem

import orderHandler
from orderHandler import OrderHandler

import itemHandler
from itemHandler import ItemHandler

import stopHandler
from stopHandler import StopHandler

import moreHandler
from moreHandler import MoreHandler
from moreHandler import FeedBack

from Language import Lang

bot=telegram.Bot(token= config.BOT_TOKEN)
updater = Updater(token= config.BOT_TOKEN)

db = DatabaseManager()
settings = SettingHandler(db)
more = MoreHandler(db)
manager = ManagerHandler(db)
product = ProductHandler(db)

ABOUT = 'About'
CHECKDETAILS = 'Check Details'
JOKE = 'Joke'
NXTJOKE = 'Next Joke'
MAINMENU = 'Main Menu'
CLICKS = 0

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

def start(bot,update):
	bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

	global CLICKS
	CLICKS += 1

	reply_markup = telegram.ReplyKeyboardRemove()
	msg = bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_MAIN_WELCOME']
		, reply_markup = reply_markup)
	show_main_menu(bot, update)
	db.add_msg(msg['message_id'], msg['text'])

def show_main_menu(bot, update):
	bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)
	msg = None
	if menu.is_registered(bot, update):
		msg = bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_WELCOME_BACK']
							   , reply_markup = menu.main_menu(bot, update))
	else:
		msg = bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_WELCOME_MAIN_MENU']
							   , reply_markup =menu.main_menu_unregistered(bot, update))

	db.add_msg(msg['message_id'], msg['text'])

def button_clicks(bot, update):
	msg = update.message.text
	if msg == Lang.Lang['English']['TXT_ABOUT']:
		about(bot, update)
	elif msg == Lang.Lang['English']['TXT_JOKE']:
		bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_JOKE_INTRO'] + str(update.message.from_user.first_name))
		send_joke(bot, update)
	elif msg == Lang.Lang['English']['TXT_MAIN_MENU']:
		show_main_menu(bot, update)
	elif msg == Lang.Lang['English']['TXT_NEXT_JOKE']:
		send_joke(bot, update)
	elif msg == Lang.Lang['English']['TXT_CHECK_DETAILS']:
		check_details(bot, update)
	elif msg == Lang.Lang['English']['TXT_INVITE']:
		invite(bot, update)
	elif msg == Lang.Lang['English']['TXT_COMMUNITY']:
		invite(bot, update)
	elif msg == Lang.Lang['English']['TXT_REVIEWS']:
		reviews.review_items(db, bot, update)
	elif msg ==Lang.Lang['English']['TXT_SETTINGS_MENU']:
		settings.start(bot, update)
	elif msg == Lang.Lang['English']['TXT_BLOCK_USERS']:
		settings.block(bot, update)
	elif msg == Lang.Lang['English']['TXT_STATISTICS']:
		settings.statistics(bot, update,CLICKS)
	elif msg == Lang.Lang['English']['TXT_MORE']:
		more.start(bot, update)
	elif msg ==Lang.Lang['English']['TXT_MANAGER']:
		manager.start(bot,update)
	elif msg == Lang.Lang['English']['TXT_ORDER_OPTION']:
		product.order_option(bot, update)
	elif msg == Lang.Lang['English']['TXT_DELETE_ITEM']:
		product.delete(bot, update)
	elif msg == Lang.Lang['English']['TXT_PRODUCT']:
		product.start(bot,update)
	elif msg == Lang.Lang['English']['TXT_TURN_ON']:
		product.turn_on_ordering(bot,update)
	elif msg == Lang.Lang['English']['TXT_TURN_OFF']:
		product.turn_off_ordering(bot,update)

# Function to check the userdetails initiated by user on /checkdetails command
def check_details(bot,update):
	bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)
	msg = None
	value = update.message.from_user.id
	data = []
	for row in db.get_cust(value):
		is_approved = (int(row[9]) == 1)
		data=[row[2], row[5], row[3],is_approved]
	if len(data)>1:
		labels=[Lang.Lang['English']['TXT_LNAME'],'Contact','Mtaa',Lang.Lang['English']['TXT_APPROVED']]
		table=zip(labels,data)
		list=tabulate(table,tablefmt="plain")
		msg = bot.send_message(chat_id=update.message.chat_id,text=list
							   ,parse_mode  = telegram.ParseMode.MARKDOWN)
	else:
		msg = bot.send_message(chat_id=update.message.chat_id,text=Lang.Lang['English']['TXT_NOT_REGISTERED'])
		show_main_menu(bot, update)
	db.add_msg(msg['message_id'], msg['text'])

def invite(bot, update):
	msg = bot.send_message(chat_id = update.message.chat_id, text = Lang.Lang['English']['TXT_FORWARD_LINK'])
	db.add_msg(msg['message_id'], msg['text'])

def send_joke(bot, update):
	bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)
	"""
	Returns a random joke from the icanhazdadjoke API.
	"/joke"
	"""
	msg = None
	try:
		headers = {'Accept': 'application/json'}
		r = (requests.get("https://icanhazdadjoke.com", headers=headers).content).decode("utf-8")
		a = ast.literal_eval(r)
		msg = bot.send_message(chat_id=update.message.chat_id, text=a["joke"])
		show_joke_menu(bot, update)
	except Exception as e:
		print(e)
		msg = bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_JOKE_ERR'])

	db.add_msg(msg['message_id'], msg['text'])

def show_joke_menu(bot, update):
	bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

	telegram.ReplyKeyboardRemove()
	custom_keyboard = [[Lang.Lang['English']['TXT_NEXT_JOKE'], Lang.Lang['English']['TXT_MAIN_MENU']]]
	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
	msg = bot.send_message(chat_id=update.effective_user.id
		,text=u"\U0001F609",reply_markup=reply_markup)
	db.add_msg(msg['message_id'], msg['text'])

def inline_button_clicks(bot, update):
	update.callback_query.answer('👍')

	query = update.callback_query
	bot.sendChatAction(query.message.chat.id, action=ChatAction.TYPING)
	# handle the query
	if query.data.split(" ")[1] == 'delete_item':
		item_id = query.data.split(" ")[0]
		db.del_item_by_id(item_id)
		items = db.get_items().fetchall()
		if len(items) > 0:
			bot.editMessageReplyMarkup(chat_id=query.message.chat.id, message_id = query.message.message_id,
				reply_markup = product.delete_reply_markup(items))
		else:
			bot.editMessageText(Lang.Lang['English']['TXT_NO_PRODUCT'], chat_id=query.message.chat.id, message_id=query.message.message_id)

	elif query.data.split(" ")[1] == 'approve_customer':
		cust_tel_id = query.data.split(" ")[0]

		keyboard = [
			[InlineKeyboardButton('Block', callback_data = cust_tel_id + ' block')],
			[InlineKeyboardButton('Delete', callback_data = cust_tel_id + ' delete_customer')]]
		reply_markup = InlineKeyboardMarkup(keyboard)

		if not menu.is_approved(cust_tel_id):
			db.approve_customer(cust_tel_id)
			if menu.is_approved(cust_tel_id):
				msg = bot.send_message(cust_tel_id, text=Lang.Lang['English']['TXT_APPROVE_PASS']
					, reply_markup = menu.main_menu(bot, update,int(cust_tel_id)))
				db.add_msg(msg['message_id'], msg['text'])
				msg = bot.edit_message_reply_markup(chat_id=query.message.chat.id,
					message_id=query.message.message_id, reply_markup = reply_markup)
				db.add_msg(msg['message_id'], msg['text'])
		else:
			msg = bot.editMessageText(Lang.Lang['English']['TXT_USER_APPROVED'], chat_id=query.message.chat.id,
					message_id=query.message.message_id, reply_markup = reply_markup)
			db.add_msg(msg['message_id'], msg['text'])

	elif query.data.split(" ")[1] == 'delete_customer':
		telegram_id = query.data.split(" ")[0]
		if int(telegram_id) not in menu.ADMINS:
			db.delete_customer_by_tel_id(telegram_id)
			bot.editMessageText(Lang.Lang['English']['TXT_CUST_DELETED'], chat_id=query.message.chat.id,
				message_id=query.message.message_id)
			bot.send_message(telegram_id, text=Lang.Lang['English']['TXT_DELETE_CUST_TEXT']
				,reply_markup = menu.main_menu_unregistered(bot, update))
		else:				
			bot.send_message(chat_id = query.message.chat.id, text=Lang.Lang['English']['TXT_UNABLE_DELETE'])

	elif query.data.split(" ")[1] == 'like':
		item_id = query.data.split(" ")[0]
		if db.like_item(query.from_user.id, item_id):
			bot.editMessageReplyMarkup(chat_id = query.message.chat.id, message_id = query.message.message_id,
				reply_markup = reviews.reply_markup(db, item_id))

	elif query.data.split(" ")[1] == 'dislike':
		item_id = query.data.split(" ")[0]
		if db.dislike_item(query.from_user.id, item_id):
			bot.editMessageReplyMarkup(chat_id = query.message.chat.id, message_id = query.message.message_id,
				reply_markup = reviews.reply_markup(db, item_id))

	elif query.data.split(" ")[1] == 'review':
		for item in db.get_items().fetchall():
			if query.data.split(" ")[0] == str(item[0]):
				msg =Lang.Lang['English']['TXT_ITEM_DISP_1'].format(item[1],item[7],item[6])
				msg += Lang.Lang['English']['TXT_ITEM_DISP_2']
				msg = bot.send_photo(chat_id = config.ITEMS_CHANNEL, photo=open(item[2],'rb'),
					caption=msg, reply_markup=reviews.reply_markup(db, item[0]),
					parse_mode = telegram.ParseMode.MARKDOWN)

	elif query.data.split(" ")[1] == 'on':
		item_id = query.data.split(" ")[0]
		db.change_item_status(item_id, '1')
		items = db.get_items().fetchall()
		if len(items) > 0:
			bot.editMessageReplyMarkup(chat_id = query.message.chat.id, message_id = query.message.message_id,
				reply_markup = product.order_option_reply_markup(items))
		else:
			bot.editMessageText(Lang.Lang['English']['TXT_NO_PRODUCT'], chat_id=query.message.chat.id, message_id=query.message.message_id)

	elif query.data.split(" ")[1] == 'off':
		item_id = query.data.split(" ")[0]
		db.change_item_status(item_id, '0')
		items = db.get_items().fetchall()
		if len(items) > 0:
			bot.editMessageReplyMarkup(chat_id = query.message.chat.id, message_id = query.message.message_id,
				reply_markup = product.order_option_reply_markup(items))
		else:
			bot.editMessageText(Lang.Lang['English']['TXT_NO_PRODUCT'], chat_id=query.message.chat.id, message_id=query.message.message_id)

	elif query.data.split(" ")[1] == 'block':
		tel_id = query.data.split(" ")[0]
		db.block_user(tel_id)
		users = db.get_all_custs().fetchall()
		msg = bot.send_message(tel_id, text=Lang.Lang['English']['TXT_BLOCKED_CUST']
		   , reply_markup = menu.main_menu(bot, update, user_id=int(tel_id)))
		db.add_msg(msg['message_id'], msg['text'])
		bot.editMessageReplyMarkup(chat_id = query.message.chat.id, message_id = query.message.message_id,
		reply_markup = settings.block_reply_markup(users))

	elif query.data.split(" ")[1] == 'unblock':
		tel_id = query.data.split(" ")[0]			
		db.unblock_user(tel_id)
		users = db.get_all_custs().fetchall()
		msg = bot.send_message(tel_id, text=Lang.Lang['English']['TXT_UNBLOCKED_CUST']
			, reply_markup = menu.main_menu(bot, update, user_id=int(tel_id)))
		db.add_msg(msg['message_id'], msg['text'])
		bot.editMessageReplyMarkup(chat_id = query.message.chat.id, message_id = query.message.message_id,
		reply_markup = settings.block_reply_markup(users))

	elif query.data.split(" ")[1] == 'order':
		typ = query.data.split(" ")[2]
		counter = 1
		msg = Lang.Lang['English']['TXT_ORDER_LIST']
		if typ =='list_cancelled_orders':
			orders = db.get_orders_by_status('0').fetchall()
			if len(orders)>0:
				msg = bot.send_message(query.message.chat.id, text=msg,
					parse_mode = telegram.ParseMode.MARKDOWN)
				db.add_msg(msg['message_id'], msg['text'])
				for order in orders:
					order_id, item_id, customer_id, phone_num, quantity, location, price_per_quantity, delivery_time, approved, status,item_name,total_quantity,username = order
					msg ='{}. '.format(counter) + Lang.Lang['English']['TXT_CONFIRM_DISP_1'].format(item_name,quantity)
					msg += Lang.Lang['English']['TXT_ORDER_DISP_LINE_2'].format(total_quantity,price_per_quantity)
					if location != 'none':
						msg += Lang.Lang['English']['TXT_LOCATION'].format(location)
					msg +=Lang.Lang['English']['TXT_ORDER_DISP_LINE_5'].format(approved =='1',phone_num,delivery_time)

					counter += 1

					keyboard = [[InlineKeyboardButton(Lang.Lang['English']['TXT_DELETED_FROM_STORE'], callback_data = (order_id + " deleteorder"))]]
					reply_markup = InlineKeyboardMarkup(keyboard)
					msg = bot.send_message(query.message.chat.id, text=msg,
						reply_markup = reply_markup, parse_mode = telegram.ParseMode.MARKDOWN)
					db.add_msg(msg['message_id'], msg['text'])

			else:
				msg = bot.send_message(query.message.chat.id, text=Lang.Lang['English']['TXT_ZERO_ORDERS'],
					parse_mode = telegram.ParseMode.MARKDOWN)
				db.add_msg(msg['message_id'], msg['text'])

		elif typ == 'list_completed_orders':
			orders = db.get_orders_by_status('2').fetchall()
			if len(orders)>0:
				msg = bot.send_message(query.message.chat.id, text=msg,
					parse_mode = telegram.ParseMode.MARKDOWN)
				db.add_msg(msg['message_id'], msg['text'])
				for order in orders:
					order_id, item_id, customer_id, phone_num, quantity, location, price_per_quantity, delivery_time, approved, status,item_name,total_quantity,username = order
					msg ='{}. '.format(counter) + Lang.Lang['English']['TXT_CONFIRM_DISP_1'].format(item_name,quantity)
					msg += Lang.Lang['English']['TXT_ORDER_DISP_LINE_2'].format(total_quantity,price_per_quantity)
					if location != 'none':
						msg += Lang.Lang['English']['TXT_LOCATION'].format(location)
					msg +=Lang.Lang['English']['TXT_ORDER_DISP_LINE_5'].format(approved =='1',phone_num,delivery_time)

					counter += 1

					keyboard = [[InlineKeyboardButton(Lang.Lang['English']['TXT_DELETED_FROM_STORE'], callback_data = (order_id + " deleteorder"))]]
					reply_markup = InlineKeyboardMarkup(keyboard)
					msg = bot.send_message(query.message.chat.id, text=msg,
						reply_markup = reply_markup, parse_mode = telegram.ParseMode.MARKDOWN)
					db.add_msg(msg['message_id'], msg['text'])
			else:
				msg = bot.send_message(query.message.chat.id, text=Lang.Lang['English']['TXT_ZERO_ORDERS'],
					parse_mode = telegram.ParseMode.MARKDOWN)
				db.add_msg(msg['message_id'], msg['text'])

		elif typ == 'list_pending_orders':
			orders = db.get_orders_by_status('1').fetchall()
			if len(orders)>0:
				msg = bot.send_message(query.message.chat.id, text=msg,
					parse_mode = telegram.ParseMode.MARKDOWN)
				db.add_msg(msg['message_id'], msg['text'])
				for order in orders:
					order_id, item_id, customer_id, phone_num, quantity, location, price_per_quantity, delivery_time, approved, status,item_name,total_quantity,username = order
					msg ='{}. '.format(counter) + Lang.Lang['English']['TXT_CONFIRM_DISP_1'].format(item_name,quantity)
					msg += Lang.Lang['English']['TXT_ORDER_DISP_LINE_2'].format(total_quantity,price_per_quantity)
					if location != 'none':
						msg += Lang.Lang['English']['TXT_LOCATION'].format(location)
					msg +=Lang.Lang['English']['TXT_ORDER_DISP_LINE_5'].format(approved =='1',phone_num,delivery_time)

					counter += 1
					msg = bot.send_message(query.message.chat.id, text=msg)
					db.add_msg(msg['message_id'], msg['text'])
			else:
				msg = bot.send_message(query.message.chat.id, text=Lang.Lang['English']['TXT_ZERO_ORDERS'],
					parse_mode = telegram.ParseMode.MARKDOWN)
				db.add_msg(msg['message_id'], msg['text'])
		elif typ == 'best_cust':
			orders = db.group_orders_by_id().fetchall()
			qtt = dict()
			file_path = open('Top 20 customers.txt','w')
			if len(orders)>0:
				for order in orders:
					qtt[order[0]] = order[1]

				k = Counter(qtt)
				high = k.most_common(20)
				count = 0
				for i in high:	
					count +=1				
					file_path.writelines(Lang.Lang['English']['TXT_BEST_BUYER'].format(i[0],count,i[1]) + '\n')	
				file_path.close()				
				bot.send_document(query.message.chat.id, document=open('Top Customers.txt','rb'))
			else:
				msg = bot.send_message(query.message.chat.id, text=Lang.Lang['English']['TXT_ZERO_ORDERS'],
					parse_mode = telegram.ParseMode.MARKDOWN)
				db.add_msg(msg['message_id'], msg['text'])

	elif query.data.split(" ")[1] == 'cancelorder':
		order_id = query.data.split(" ")[0]
		order_qtts = []
		item_qtt = 0
		item_ids = []
		location = ''
		item_name = []
		approved ='0'
		new_qtt = 0
		username = ''
		for order in db.get_all_orders(order_id).fetchall():
			order_qtts = order[4]
			item_ids = order[1]
			location = order[5]
			approved = order[8]
			item_name = order[10]
			username = order[12]
		# print(item_ids.replace('[]\'',''))
		# for item_id in item_ids:
		# 	print(item_id)
		# 	for item in db.get_item_by_id(item_id).fetchall():
		# 		print(item[3])
		# 		item_qtt = item[3]
		# 	for order_qtt in order_qtts:
		# 		new_qtt = order_qtt + item_qtt
		# 	db.update_item_quantity(new_qtt,item_id)
		if approved =='1':
			msg = bot.send_message(query.message.chat.id, text=Lang.Lang['English']['TXT_CANCEL_FAIL'])
			db.add_msg(msg['message_id'], msg['text'])
		else:
			keyboard = [
				[InlineKeyboardButton(Lang.Lang['English']['TXT_DELETE_ORDER'], callback_data = (order_id + " deleteorder"))]]
			reply_markup = InlineKeyboardMarkup(keyboard)
			msg = Lang.Lang['English']['TXT_CANCELLED_ORDER_TEXT'].format(username,location,order_qtts,item_name)
			bot.send_message(chat_id = config.ORDER_CHANNEL, text =msg
				,reply_markup = reply_markup)
			db.change_order_status(order_id,'0')
			bot.editMessageText(Lang.Lang['English']['TXT_ORDER_CANCELLED'], chat_id=query.message.chat.id, message_id=query.message.message_id)

	elif query.data.split(" ")[1] == 'deleteorder':
		order_id = query.data.split(" ")[0]
		db.del_orders_by_id(order_id)
		bot.editMessageText(Lang.Lang['English']['TXT_DELETED_FROM_STORE'], chat_id=query.message.chat.id, message_id=query.message.message_id)

	elif query.data.split(" ")[1] == 'time':
		time = query.data.split(" ")[2]
		cust_tel_id = query.data.split(" ")[0]

		if time =='0':
			msg = bot.send_message(cust_tel_id, text=Lang.Lang['English']['TXT_MESSENGER_ARRIVE'])
			db.add_msg(msg['message_id'], msg['text'])
		elif time =='15':
			msg = bot.send_message(cust_tel_id, text=Lang.Lang['English']['TXT_15MIN_OUT'])
			db.add_msg(msg['message_id'], msg['text'])
		elif time =='30':
			msg = bot.send_message(cust_tel_id, text=Lang.Lang['English']['TXT_30MIN_OUT'])
			db.add_msg(msg['message_id'], msg['text'])
		elif time =='45':
			msg = bot.send_message(cust_tel_id, text=Lang.Lang['English']['TXT_45MIN_OUT'])
			db.add_msg(msg['message_id'], msg['text'])
		elif time =='1hr':
			msg = bot.send_message(cust_tel_id, text=Lang.Lang['English']['TXT_1HR_OUT'])
			db.add_msg(msg['message_id'], msg['text'])
		elif time =='2hr':
			msg = bot.send_message(cust_tel_id, text=Lang.Lang['English']['TXT_2HR_OUT'])
			db.add_msg(msg['message_id'], msg['text'])
		elif time =='3hr':
			msg = bot.send_message(cust_tel_id, text=Lang.Lang['English']['TXT_3HR_OUT'])
			db.add_msg(msg['message_id'], msg['text'])
		elif time == 'orderdelivered':
			order_id = query.data.split(" ")[0]
			telegram_id = 0
			item_id = ''
			item_name = ''
			total_price = 0
			quantity = 0
			for order in db.get_all_orders(order_id).fetchall():
				telegram_id = order[2]
				item_id = order[1]
				total_price = order[6]
				quantity = order[4]
				item_name = order[10]
			msg = Lang.Lang['English']['TXT_DELIVERED_TEXT_1'].format(item_name,quantity,total_price)
			msg +=Lang.Lang['English']['TXT_DELIVERED_TEXT_2']
			
			msg = bot.send_message(telegram_id, text=msg,parse_mode = telegram.ParseMode.MARKDOWN )
			db.add_msg(msg['message_id'], msg['text'])

			db.change_order_status(order_id,'2')
			keyboard = [
				[InlineKeyboardButton(Lang.Lang['English']['TXT_DELIVERED_TEXT'], callback_data ='None None')],
				[InlineKeyboardButton(Lang.Lang['English']['TXT_DELETE_ORDER'], callback_data = (order_id + " deleteorder"))]]
			reply_markup = InlineKeyboardMarkup(keyboard)
			bot.edit_message_reply_markup(chat_id=query.message.chat.id,
				message_id=query.message.message_id,reply_markup = reply_markup)

	elif query.data.split(" ")[2] == 'approve_order':
		order_id = query.data.split(" ")[0]
		cust_tel_id = query.data.split(" ")[1]
		item_name = []
		qtt = []
		total_price = 0
		status =''
		for order in db.get_all_orders(order_id).fetchall():
			item_name = order[10]
			status = order[9]
			qtt = order[4]
			total_price = order[6]
		if status !='0':
			if not menu.is_approved_order(order_id):
				db.approve_order(order_id)
				if menu.is_approved_order(order_id):
					msg = Lang.Lang['English']['TXT_ORDER_RECEIVED'].format(str(item_name)[1:-1],qtt,total_price)
					msg = bot.send_message(cust_tel_id, text=msg)
					db.add_msg(msg['message_id'], msg['text'])
					button= [
						[InlineKeyboardButton(Lang.Lang['English']['TXT_NOW'], callback_data = cust_tel_id + ' time 0'),
						InlineKeyboardButton("15{}".format(Lang.Lang['English']['TXT_MINUTE']), callback_data = cust_tel_id + ' time 15'),
						InlineKeyboardButton("30{}".format(Lang.Lang['English']['TXT_MINUTE']), callback_data = cust_tel_id + ' time 30'),
						InlineKeyboardButton("45{}".format(Lang.Lang['English']['TXT_MINUTE']), callback_data = cust_tel_id + ' time 45')],
						[InlineKeyboardButton("1{}".format(Lang.Lang['English']['TXT_HR']), callback_data = cust_tel_id + ' time 1hr'),
						InlineKeyboardButton("2{}".format(Lang.Lang['English']['TXT_HR']), callback_data = cust_tel_id + ' time 2hr'),
						InlineKeyboardButton("3{}".format(Lang.Lang['English']['TXT_HR']), callback_data =cust_tel_id + ' time 3hr'),
						InlineKeyboardButton(Lang.Lang['English']['TXT_DELIVER'], callback_data =order_id + ' time orderdelivered')]]

					reply_markup = InlineKeyboardMarkup(button)
					bot.edit_message_reply_markup(chat_id=query.message.chat.id,
					 message_id=query.message.message_id,reply_markup = reply_markup)
			else:
				keyboard = [[InlineKeyboardButton(Lang.Lang['English']['TXT_ORDER_ALREADY_CONFIRMED'], callback_data ='None None')]]
				reply_markup = InlineKeyboardMarkup(keyboard)
				bot.edit_message_reply_markup(chat_id=query.message.chat.id,
					message_id=query.message.message_id,reply_markup = reply_markup)
		else:
			msg = bot.editMessageText(Lang.Lang['English']['TXT_ORDER_CANCELLED'], chat_id=query.message.chat.id
				,message_id=query.message.message_id)
			db.add_msg(msg['message_id'], msg['text'])

	else:
		print(query.data)

def about(bot, update):
	bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)

	msg = bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_ABOUT_TEXT'])
	db.add_msg(msg['message_id'], msg['text'])

def main():
	updater.dispatcher.add_handler(CommandHandler('start',start))

	customer  = CustomerHandler(bot, db)
	customer_handler  = ConversationHandler(
		entry_points = [RegexHandler(u'^({})$'.format(Lang.Lang['English']['TXT_REGISTER']),customer.new_customer)],
		states = {
			customerHandler.TERMS: [MessageHandler(Filters.text, customer.terms_n_condition)],
			customerHandler.CUSTOMER_NAME: [MessageHandler(Filters.text, customer.name)],
			customerHandler.CUSTOMER_PHONE: [MessageHandler(Filters.contact, customer.order_phone)],
			# customerHandler.CUSTOMER_ID_NUMBER: [MessageHandler(Filters.text, customer.id_number)],
			customerHandler.CUSTOMER_PHOTO: [MessageHandler(Filters.photo, customer.photo)],
			# customerHandler.CUSTOMER_ID_CARD: [MessageHandler(Filters.photo, customer.photo_id_card)],
			# customerHandler.CUSTOMER_LINK: [MessageHandler(Filters.text, customer.facebook_link)],
			customerHandler.CUSTOMER_LOC: [MessageHandler(Filters.text, customer.save_location)],
			customerHandler.REGISTER: [MessageHandler(Filters.text, customer.register)],
		},
		fallbacks=[CommandHandler(Lang.Lang['English']['TXT_CANCEL'], customer.cancel)
			, CommandHandler(Lang.Lang['English']['TXT_REGISTER_CUST'],customer.register)]
	)
	updater.dispatcher.add_handler(customer_handler)

	'''
	The bot order invitation'''
	order  = OrderHandler(db)
	order_handler  = ConversationHandler(
		entry_points = [RegexHandler('^({})$'.format(Lang.Lang['English']['TXT_ORDER']), order.entry_point), RegexHandler(u'^({})$'.format(Lang.Lang['English']['TXT_MY_ORDERS']), order.list_customer_orders)],
		states = {
			orderHandler.START: [MessageHandler(Filters.text, order.entry_point)],
			orderHandler.START: [MessageHandler(Filters.text, order.start)],
			orderHandler.ORDER_PHONE: [MessageHandler(Filters.contact, order.order_phone)],
			orderHandler.ORDER_ADDRESS: [MessageHandler(Filters.text, order.order_address)],
			orderHandler.ORDER_PICKUP: [MessageHandler(Filters.text, order.order_pickup)],
			orderHandler.ORDER_COLLECTION: [MessageHandler(Filters.text, order.order_collection)],
			orderHandler.QUANTITY: [MessageHandler(Filters.text, order.order_quantity)],
			orderHandler.ORDER_TIME: [MessageHandler(Filters.text, order.order_time)],
			orderHandler.ADD_ITEM: [MessageHandler(Filters.text, order.add_item)],
			orderHandler.ORDER_SELFIE: [MessageHandler(Filters.photo, order.photo)],
			orderHandler.ORDER_CONFIRM: [MessageHandler(Filters.text, order.order_confirm)],
			orderHandler.COMMENTS: [MessageHandler(Filters.text, order.comments)],
			orderHandler.ADD_ITEM: [MessageHandler(Filters.text, order.add_item)],
		},
		fallbacks=[CommandHandler(Lang.Lang['English']['TXT_CANCEL'], order.cancel)
			, CommandHandler(Lang.Lang['English']['TXT_ADD'],order.load_items)]
	)
	updater.dispatcher.add_handler(order_handler)

	'''
	The bot send to everyone'''

	send = Send(db)
	msg_handler  = ConversationHandler(
		entry_points = [RegexHandler('^({})$'.format(Lang.Lang['English']['TXT_BROADCAST']), send.broadcast)],
		states = {
			settingsHandler.SEND: [MessageHandler(Filters.text, send.send)],
		},
		fallbacks=[CommandHandler(Lang.Lang['English']['TXT_CANCEL'], send.cancel)]
	)
	updater.dispatcher.add_handler(msg_handler)

	admin = NewAdmin(db)
	adminHandler  = ConversationHandler(
		entry_points = [RegexHandler('^({})$'.format(Lang.Lang['English']['TXT_ADD_ADMIN']), admin.add)],
		states = {
			managerHandler.CONFIRM_NAME: [MessageHandler(Filters.text, admin.confirm_name)],
		},
		fallbacks=[CommandHandler(Lang.Lang['English']['TXT_CANCEL'], admin.cancel)]
	)
	updater.dispatcher.add_handler(adminHandler)

	removeAdmin = RemoveAdmin(db)
	removeAdminHandler  = ConversationHandler(
		entry_points = [RegexHandler('^({})$'.format(Lang.Lang['English']['TXT_REMOVE_ADMIN']), removeAdmin.add)],
		states = {
			managerHandler.REMOVE_ADMIN: [MessageHandler(Filters.text, removeAdmin.remove_admin)],
		},
		fallbacks=[CommandHandler(Lang.Lang['English']['TXT_CANCEL'], admin.cancel)]
	)
	updater.dispatcher.add_handler(removeAdminHandler)

	editItem = EditItem(db)
	editItemHandler  = ConversationHandler(
		entry_points = [RegexHandler('^({})$'.format(Lang.Lang['English']['TXT_EDIT_ITEM']), editItem.add)],
		states = {
			productHandler.EDIT_ITEM: [MessageHandler(Filters.text, editItem.edit_item)],
			productHandler.ITEM_QUANTITY: [MessageHandler(Filters.text, editItem.item_quantiy)],
		},
		fallbacks=[CommandHandler(Lang.Lang['English']['TXT_CANCEL'], editItem.cancel)]
	)
	updater.dispatcher.add_handler(editItemHandler)

	'''
	The bot send  feedback to admins'''

	feed = FeedBack(db)
	feedback_handler  = ConversationHandler(
		entry_points = [RegexHandler('^({})$'.format(Lang.Lang['English']['TXT_FEEDBACK_BTN']), feed.feedback)],
		states = {
			moreHandler.SHOPPING_EXPERIENCE: [MessageHandler(Filters.text, feed.shopping_experince)],
			moreHandler.QUALITY: [MessageHandler(Filters.text, feed.quality)],
			moreHandler.SERVICES: [MessageHandler(Filters.text, feed.services)],
			moreHandler.PRICE: [MessageHandler(Filters.text, feed.price)],
		},
		fallbacks=[CommandHandler(Lang.Lang['English']['TXT_CANCEL'], feed.cancel)]
	)
	updater.dispatcher.add_handler(feedback_handler)

	# item handler
	item  = ItemHandler(db)
	item_handler  = ConversationHandler(
		entry_points = [RegexHandler('^({})$'.format(Lang.Lang['English']['TXT_ADD_ITEM_BTN']), item.new_item)],
		states = {
			itemHandler.ITEM_NAME: [MessageHandler(Filters.text, item.name)],
			itemHandler.ITEM_PRICE: [MessageHandler(Filters.text, item.item_price)],
			itemHandler.ITEM_PHOTO: [MessageHandler(Filters.photo, item.photo)],
			itemHandler.ITEM_DESCRIPTION: [MessageHandler(Filters.text, item.description)],
			itemHandler.ITEM_QUANTITY: [MessageHandler(Filters.text, item.quantity)],
			itemHandler.REGISTER: [MessageHandler(Filters.text, item.register)],
		},
		fallbacks=[CommandHandler(Lang.Lang['English']['TXT_CANCEL'], item.cancel)
			, CommandHandler(Lang.Lang['English']['TXT_ADD'],item.register)]
	)
	updater.dispatcher.add_handler(item_handler)

	'''
	stop the bot
	'''
	botStop = StopHandler(db, updater)
	stop_handler = ConversationHandler(
		entry_points = [RegexHandler('^({})$'.format(Lang.Lang['English']['TXT_STOP_BOT']), botStop.entry)],
		states = {
			stopHandler.CONFIRM: [MessageHandler(Filters.text, botStop.confirm)]
		},
		fallbacks=[CommandHandler(Lang.Lang['English']['TXT_CANCEL'], botStop.cancel)]
	)
	updater.dispatcher.add_handler(stop_handler)

	updater.dispatcher.add_handler(MessageHandler(Filters.text, button_clicks))
	updater.dispatcher.add_handler(CallbackQueryHandler(inline_button_clicks))

	updater.start_polling()
	updater.idle()

if __name__ == "__main__":
	print('Online')
	main()
