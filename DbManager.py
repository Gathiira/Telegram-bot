"""
Manager class to handle database interactions.
"""

import os
import sqlite3
import pymysql
# import pandas as pd
from pathlib import Path

DB_FILENAME= 'ordering.db'

class DatabaseManager():
    def __init__(self):
        """
        Constructor.

        Args:
            is_first_run (bool): Is this the first DatabaseManager
                created in this run?
        """
        
        # if is_first_run:
        #     try:
        #         os.remove(DB_FILENAME)
        #     except OSError:
        #         pass
        self.conn = sqlite3.connect(DB_FILENAME,check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_messages_table()
        self.create_customers_table()
        self.create_items_table()
        self.create_orders_table()
        self.create_like_dislike_table()
        self.create_feedback_table()

    def create_like_dislike_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS
            like_dislike(user_id number, item_id text, like_dislike text)''')

    def create_messages_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS
            messages(msg_id text, msg text)''')

    def create_feedback_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS
            feedback(telegram_id text, feedback text)''')

    def create_customers_table(self):
        # self.cursor.execute('''DROP TABLE IF EXISTS customers''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS 
            customers(telegram_id number,id number,name text,location text, language text,phone_number text,
            fb_link text, photo text,id_card text, approved text)''')
        self.conn.commit()

    def create_items_table(self):
        # self.cursor.execute('''DROP TABLE IF EXISTS items''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS 
            items(item_id text,name text,photo text,quantity number
            ,price_per_quantity number, status text,description text,kind text)''')
        self.conn.commit()

    def create_orders_table(self):
        # self.cursor.execute('''DROP TABLE IF EXISTS orders''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS 
            orders(order_id number,item_id number,customer_id number,phonenumber number,quantity number,
            location text,price_per_quantity number, delivery_time time, approved text,status text,item_name number,total_quantity number,username text)''')
        self.conn.commit()

    def like_item(self, user_id, item_id):
        if str(user_id) not in [str(review[0]) for review in self.get_item_likes(item_id).fetchall()]:
            sql = "INSERT INTO like_dislike VALUES('"
            sql += str(user_id)+"', '"+str(item_id)+"', '1')"

            self.cursor.execute(sql)
            self.conn.commit()
            if str(user_id) in [str(review[0]) for review in self.get_item_dislikes(item_id).fetchall()]:
                self.del_item_dislike(user_id, item_id)
            return True
        return False

    def dislike_item(self, user_id, item_id):
        if str(user_id) not in [str(review[0]) for review in self.get_item_dislikes(item_id).fetchall()]:
            sql = "INSERT INTO like_dislike VALUES('"
            sql += str(user_id)+"', '"+str(item_id)+"', '0')"

            self.cursor.execute(sql)
            self.conn.commit()
            if str(user_id) in [str(review[0]) for review in self.get_item_likes(item_id).fetchall()]:
                self.del_item_like(user_id, item_id)
            return True
        return False

    def add_customer(self, customer):
        sql_str = "INSERT INTO customers (telegram_id,id,name,location, language,phone_number,fb_link, photo,id_card, approved) VALUES (?,?,?,?,?,?,?,?,?,?)"
        self.cursor.execute(sql_str,(customer.get_telegram_id(),customer.get_id(),customer.get_name()
            ,customer.get_location(),customer.get_language(),customer.get_phone(),customer.get_fb_link()
            ,customer.get_photo(),customer.get_id_card(),customer.approved))
        self.conn.commit()

    def add_item(self, item,description,item_kind):
        sql_str = "INSERT INTO items (item_id,name,photo,quantity,price_per_quantity,status,description,kind) VALUES (?,?,?,?,?,?,?,?)"

        self.cursor.execute(sql_str, (item.get_item_id(),item.get_name(),item.get_photo(),
            item.get_quantity(),item.get_price_per_quantity(),'1',description,item_kind))
        self.conn.commit()

    def add_order(self,order,total_quantity,username):
        sql_str = "INSERT INTO orders (order_id,item_id,customer_id,phonenumber,quantity,location,price_per_quantity, delivery_time, approved,status,item_name,total_quantity,username) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"

        self.cursor.execute(sql_str,(order.id,order.get_item_id(),order.get_cust_id(),order.get_phonenumber()
            ,order.get_quantity(),order.get_location(),order.get_price_per_quantity(),order.get_delivery_time()
            ,order.approved,order.status,order.get_item_name(),total_quantity,username))
        self.conn.commit()

    def add_msg(self, msg_id, msg):
        self.cursor.execute("INSERT INTO messages (msg_id, msg) VALUES(?, ?)",(msg_id, msg))
        self.conn.commit()

    def add_feedback(self,telegram_id,feedback):
        self.cursor.execute("INSERT INTO feedback (telegram_id, feedback) VALUES(?, ?)",(telegram_id, feedback))
        self.conn.commit()

    def get_all_feedback(self):
        return self.cursor.execute("SELECT * FROM feedback")

    def change_item_status(self, item_id, status):
        self.cursor.execute("UPDATE items set status=? where item_id=?", (status,item_id,))
        self.conn.commit()

    def change_order_status(self, order_id, status):
        self.cursor.execute("UPDATE orders set status=? where order_id=?", (status,order_id,))
        self.conn.commit()

    def get_item_likes(self, item_id):
        return self.cursor.execute("SELECT * FROM like_dislike WHERE item_id=? and like_dislike=1",(item_id,))

    def get_item_dislikes(self, item_id):
        return self.cursor.execute("SELECT * FROM like_dislike WHERE item_id=? and like_dislike=0",(item_id,))

    def del_item_like(self, user_id, item_id):
        self.cursor.execute("DELETE FROM like_dislike WHERE user_id=? AND item_id=? AND like_dislike=1",(user_id,item_id,))
        self.conn.commit()

    def del_item_dislike(self, user_id, item_id):
        self.cursor.execute("DELETE FROM like_dislike WHERE user_id=? AND item_id=? AND like_dislike=0",(user_id,item_id,))
        self.conn.commit()

    def get_messages(self):
        return self.cursor.execute("SELECT * FROM messages")

    def get_cust(self, cust_id):
        return self.cursor.execute("SELECT * FROM customers WHERE telegram_id=?", (cust_id,))

    def get_cust_by_phone(self, phone_number):
        return self.cursor.execute("SELECT * FROM customers WHERE phone_number=?", (phone_number,))

    def delete_message(self,message_id):
        self.cursor.execute("DELETE FROM messages WHERE msg_id=?",(message_id,))
        self.conn.commit()

    def get_verified_cust(self):
        return self.cursor.execute("SELECT * FROM customers WHERE approved = '1'")

    def get_all_custs(self):
        return self.cursor.execute("SELECT * from customers")

    def delete_customer_by_tel_id(self,telegram_id):
        self.cursor.execute("DELETE from customers where telegram_id=?", (telegram_id,))
        self.conn.commit()        

    def block_user(self, telegram_id):
        self.cursor.execute("UPDATE customers set approved = '2' where telegram_id=?",(telegram_id,))
        self.conn.commit()

    def unblock_user(self, telegram_id):
        self.cursor.execute("UPDATE customers set approved = '1' where telegram_id=?",(telegram_id,))
        self.conn.commit()

    def del_all_orders(self):
        self.cursor.execute("DELETE FROM orders")
        self.conn.commit()

    def del_orders_by_id(self,order_id):
        self.cursor.execute("DELETE from orders where order_id=?", (order_id,))
        self.conn.commit()

    def get_orders(self):
        return self.cursor.execute("SELECT * FROM orders")

    def get_all_orders(self, order_id):
        return self.cursor.execute("SELECT * from orders WHERE order_id=?", (order_id,))

    def get_orders_by_cust_id(self, cust_id):
        return self.cursor.execute("SELECT * from orders where customer_id=?", (cust_id,))

    def group_orders_by_id(self):
        return self.cursor.execute("SELECT username, sum(total_quantity) total_quantity FROM orders GROUP BY customer_id")

    def get_orders_by_status(self,status='1'):
        return self.cursor.execute("SELECT * FROM orders WHERE status=?", (status,))

    def get_items(self):
        return self.cursor.execute("SELECT * FROM items")

    def change_ordering_option(self,status):
        self.cursor.execute("UPDATE items set status=?", (status,))
        self.conn.commit()

    def get_items_by_status(self,status='1'):
        return self.cursor.execute("SELECT * FROM items WHERE status=?", (status,))

    def get_items_by_quantity(self):
        return self.cursor.execute("SELECT * FROM items WHERE quantity < 3 AND status ='1'")

    def update_item_quantity(self,new_quantity,item_id):
        self.cursor.execute("UPDATE items set quantity=? where item_id=?", (new_quantity,item_id,))
        self.conn.commit()
        
    def get_item_by_name(self, name):
        return self.cursor.execute("SELECT * from items where name=?", (name,))

    def get_item_by_id(self, item_id):
        return self.cursor.execute("SELECT * from items where item_id=?", (item_id,))

    def del_item_by_id(self, item_id):
        self.cursor.execute("DELETE from items where item_id=?", (item_id,))
        self.conn.commit()

    def del_all_items(self):
        self.cursor.execute("DELETE FROM items")
        self.conn.commit()

    def del_all_customers(self):
        self.cursor.execute("DELETE FROM customers")
        self.conn.commit()

    def approve_customer(self, telegram_id):
        sql = "UPDATE customers set approved = '1' where telegram_id = "
        sql += telegram_id
        self.cursor.execute(sql)
        self.conn.commit()

    def approve_order(self, order_id):
        self.cursor.execute("UPDATE orders set approved = '1' where order_id=?", (order_id,))
        self.conn.commit()
        
    def __del__(self):
        """
        Destructor.
        """
        self.conn.close()
