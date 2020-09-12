import telegram
from DbManager import DatabaseManager
import math

from Language import Lang

ADMINS = [] # add admin ids here

db = DatabaseManager()

def calculate_price(total_quantity):
	price_per_quantity = 20 * total_quantity
	if total_quantity >=10 and total_quantity <15:
		price_per_quantity = 0.95* price_per_quantity
	elif total_quantity >=15 and total_quantity <20:
		price_per_quantity = 0.90* price_per_quantity
	elif total_quantity >=20 and total_quantity <25:
		price_per_quantity = 0.88 * price_per_quantity
	elif total_quantity >=25 and total_quantity <30:
		price_per_quantity = 0.85* price_per_quantity
	elif total_quantity >=30:
		price_per_quantity = 0.80* price_per_quantity
	return int(math.ceil(price_per_quantity / 10.0)) * 10

def is_valid_url(url):
    import re
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and regex.search(url)

def is_registered(bot, update):
	telegram_id = update.message.from_user.id

	return len(db.get_cust(telegram_id).fetchall()) >0

def is_approved(telegram_id):
	approved = False
	for row in db.get_cust(telegram_id):
		approved = (row[9] == '1')
	return approved

def is_blocked(telegram_id):
	blocked = False
	for row in db.get_cust(telegram_id):
		blocked = (row[9] == '2')
	return blocked

def is_approved_order(order_id):
	approved = False
	for row in db.get_all_orders(order_id):
		approved = (row[8] == '1')
	return approved

def main_menu(bot, update, user_id = None):
	telegram.ReplyKeyboardRemove()
	menu = []
	if user_id is None:
		user_id = update.message.from_user.id

	if is_blocked(user_id):
		menu.append([Lang.Lang['English']['TXT_BLOCKED']])
	else:
		if is_approved(user_id):
			menu.append([Lang.Lang['English']['TXT_ORDER']])
		else:
			menu.append([Lang.Lang['English']['TXT_WAIT_APPROVAL']])
		menu.append([Lang.Lang['English']['TXT_MY_ORDERS'], Lang.Lang['English']['TXT_JOKE']])
		menu.append([Lang.Lang['English']['TXT_INVITE'], Lang.Lang['English']['TXT_CHECK_DETAILS']])
		ls = [Lang.Lang['English']['TXT_ABOUT']]

		if user_id not in ADMINS:			
			ls.append(Lang.Lang['English']['TXT_FEEDBACK_BTN'])
		else:
			# admin only
			ls.append(Lang.Lang['English']['TXT_SETTINGS_MENU'])

		menu.append(ls)

	return telegram.ReplyKeyboardMarkup(menu, resize_keyboard=True)

def main_menu_unregistered(bot, update):
	telegram.ReplyKeyboardRemove()
	custom_keyboard = [[Lang.Lang['English']['TXT_REGISTER']], [Lang.Lang['English']['TXT_ABOUT']
	, Lang.Lang['English']['TXT_JOKE']]]

	return telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
