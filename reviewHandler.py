import telegram
from telegram import InlineKeyboardButton,InlineKeyboardMarkup
import config

from Language import Lang

def review_items(db, bot, update):
	items = db.get_items().fetchall()
	if len(items) > 0:
		for item in items:
			likes_count = 0
			dislikes_count = 0
			likes_count = len(db.get_item_likes(item[0]).fetchall())
			dislikes_count = len(db.get_item_dislikes(item[0]).fetchall())
			msg = Lang.Lang['English']['TXT_ITEM_DISP_1'].format(item[1],item[7],item[6])
			msg += Lang.Lang['English']['TXT_ITEM_DISP_2']
			msg += Lang.Lang['English']['TXT_PRODUCT_LIKES'].format(likes_count,dislikes_count)

			keyboard = [[InlineKeyboardButton(Lang.Lang['English']['TXT_POST_ITEM'], callback_data = (item[0] + " review"))]]
			reply_markup = InlineKeyboardMarkup(keyboard)
			bot.send_message(chat_id=update.message.chat_id, text = msg,
				reply_markup=reply_markup, parse_mode = telegram.ParseMode.MARKDOWN)
	else:
		bot.send_message(chat_id=update.message.chat_id, text=Lang.Lang['English']['TXT_NO_PRODUCT'])


def reply_markup(db, item_id):
	likes_count = 0
	dislikes_count = 0
	likes_count = len(db.get_item_likes(item_id).fetchall())
	dislikes_count = len(db.get_item_dislikes(item_id).fetchall())

	button= [
		[InlineKeyboardButton('👍 {}'.format(likes_count), callback_data = (item_id + " like")),
		InlineKeyboardButton("👎 {}".format(dislikes_count), callback_data = (item_id + " dislike"))],
		[InlineKeyboardButton(Lang.Lang['English']['TXT_ORDER'], url = config.BOT_LINK)],
		[InlineKeyboardButton(Lang.Lang['English']['TXT_SERVICE'], url = config.OWNER_LINK)]]
	return InlineKeyboardMarkup(button)