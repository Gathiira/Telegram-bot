import math

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


print(calculate_price(20))