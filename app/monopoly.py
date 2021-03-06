from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# {
#     chatid : {
#         users : {
#             username : {
#                 wallet : 10,
#                 bankbalance : 100,
#                 inventory : {
#                     item 1 : (quantity, price),
#                     item 2 : (quantity, price)
#                 }
#             }
#         },
#         shop : {
#             item 1 : (quantity, price),
#             item 2 : (quantity, price)
#         },
#         lottery : [username1,username2]
#     }
# }


# todo ============
# gambling
# challenge - two users


shop_template = {
    "chips" : (15,10),
    "coke" : (10,25),
    "cake" : (5,100),
    "laptop" : (5, 1000),
}


# save monopoly data
def save_mono():
    f = open('data/monopoly','w')
    f.write(str(mono))
    f.close()

# load monopoly data
def load_mono():
    f = open('data/monopoly','r')
    data=f.read()
    f.close()
    return eval(data)


# initially load monopoly data
mono = load_mono()

# creating a new user if one doesnt exist
def user_init(chat_id, username):
    mono[chat_id]["users"][username] = {
        "wallet" : 0,
        "bankbalance" : 0,
        "inventory" : {}
    }
    

# initialize mono in a group chat
def mono_init(chat_id, username):
    mono[chat_id] = {
        "users" : {},
        'shop': shop_template,
        "lottery" : []
    }
    user_init(chat_id, username)
    



def check_mono_initialized(chat_id,username):
    if not chat_id in mono:
        mono_init(chat_id, username)
    else:
        if not username in mono[chat_id]["users"]:
            user_init(chat_id, username)


def mono_handler(bot, update, msg_list):
    chat_id = update.message.chat_id
    username = update.message.from_user.username.lower()
    
    # Check if the monopoly has been initialised. (the chat_id and/or the username)
    check_mono_initialized(chat_id, username)

    user = mono[chat_id]["users"][username]




    # pls balance
    # pls deposit 100
    # pls withdraw 500
    # View the balance for User
    if msg_list[1] in ["balance"]:
        if len(msg_list) > 2: username = msg_list[2].replace("@","") 
        user = mono[chat_id]["users"][username]
        wallet = user['wallet']
        bankbalance = user["bankbalance"]
        update.message.reply_text("Balance Information: \n Wallet: "+ str(wallet) + "\n Bank: " + str(bankbalance) )

    
    elif msg_list[1] in ["deposit"]:
        if msg_list[2] == "all":
            user["bankbalance"] += user["wallet"]
            user["wallet"] = 0
            update.message.reply_text("All your money is deposited.")
        else:
            money = int(msg_list[2])
            if money <= user["wallet"]:
                user["bankbalance"] += money
                user["wallet"] -= money
                update.message.reply_text(str(money) + " has been deposited.")
            else:
                update.message.reply_text("You dont have that kind of money in your wallet.")
        

    elif msg_list[1] in ["withdraw"]:
        if msg_list[2] == "all":
            user["wallet"] += user["bankbalance"]
            user["bankbalance"] = 0 
            update.message.reply_text("All your money is withdrawn.")
        else:
            money = int(msg_list[2])
            if money <= user["bankbalance"]:
                user["wallet"] += money
                user["bankbalance"] -= money
                update.message.reply_text(str(money) + " has been withdrawn.")
            else:
                update.message.reply_text("You dont have that kind of money in your bank.")



    # pls shop
    # pls buy coke
    # pls sell chips
    # pls inventory
    # View the Items in the Shop
    elif msg_list[1] in ["shop","market", "store"]:
        shop = mono[chat_id]["shop"]
        items_str = "Shop Items :\n--------------\n"
        for key in shop:
            q,p = shop[key]
            items_str += key + "  ("+ str(q) +") = Rs" + str(p) + "\n"
        update.message.reply_text(items_str)
    
    # Buy items at store
    elif msg_list[1] in ["buy", "purchase"]:
        shop= mono[chat_id]["shop"]
        shop_item = msg_list[2]
        quantity, price = shop[shop_item]
        if quantity > 0:
            if price > user["wallet"]:
                update.message.reply_text("You broke af.")
                return
            shop[shop_item] = quantity - 1, price
            user["wallet"] -= price
            if shop_item in user["inventory"]:
                q,p = user["inventory"][shop_item]
                user["inventory"][shop_item] = q+1,p
            else:
                user["inventory"][shop_item] = (1,price)
            update.message.reply_text("Item " + shop_item + " has been purchased")
        else:   # quantity == 0
            update.message.reply_text("Item is out of stock.")

    
    elif msg_list[1] in ["sell"]:
        shop = mono[chat_id]["shop"]
        shop_item = msg_list[2]
        if not shop_item in user["inventory"]:
            update.message.reply_text("You dont have that item.")
            return
        q, p = user["inventory"][shop_item]
        user["wallet"] += p 
        quantity, price = shop[shop_item]
        shop[shop_item] = quantity + 1, price
        if q==1 :
            user["inventory"].pop(shop_item)
        else:
            user["inventory"][shop_item] = q - 1,p 
        update.message.reply_text("Item has been sold")
        

    elif msg_list[1] in ["inventory"]:
        inventory = user["inventory"]
        items_str = "Inventory Items :\n"
        for key in inventory:
            q,p = inventory[key]
            items_str += key + "  ("+ str(q) +") = Rs" + str(p) + "\n"
        update.message.reply_text(items_str)
    
    

        

    # pls lottery results
    # pls lottery buy
    # pls lottery view 
    elif msg_list[1] in ["lottery"]:
        lottery_users = mono[chat_id]["lottery"]
        if msg_list[2] in ["buy"]:
            if username in lottery_users:   # participated already
                update.message.reply_text("You have already participated. Use \npls lottery results")
            else:   # participate in lottery
                if mono[chat_id]["users"][username]["wallet"] >= 10:
                    mono[chat_id]["users"][username]["wallet"] -= 10
                    lottery_users.append(username)
                    update.message.reply_text("You have successfully participated in the lottery.")
                else:
                    update.message.reply_text("You dont even have enough money to buy a lottery ticket.")
                
        elif msg_list[2] in ["view"]:
            update.message.reply_text("Lottery Participants :\n" + "\n".join(lottery_users))
        elif msg_list[2] in ["result","results"]:
            
            num = len(lottery_users)
            money = 10 * num * num
            import random 
            n = random.randint(0,len(lottery_users)-1)
            winner = lottery_users[n] # random select
            user = mono[chat_id]["users"][winner]
            user["wallet"] += money
            mono[chat_id]["lottery"] = []
            
            update.message.reply_text(winner + " won the lottery. Prize money : " + str(money))



    # pls gamble all
    # pls gamble 50
    elif msg_list[1] in ["gamble"]:
        if msg_list[2] == "all":
            money = user["wallet"]
            user["wallet"] = 0
        else:
            money = int(msg_list[2])
            user["wallet"] -= money
        import random
        game = random.randint(1,2)
        multiplier =  float(random.randint(80,100) /100)
        if game==2:  # win
            money += money * multiplier
            user["wallet"] += int(money)
            update.message.reply_text("Congrats!!\nYou won this round. You got " + str(money))
        else: # lose
            update.message.reply_text("You lost this round.")




    elif msg_list[1] in ["share","send"]:
        to_user = msg_list[2].replace("@","")
        money = int(msg_list[3])
        if user["wallet"] > money:
            user["wallet"] -= money
            mono[chat_id]["users"][to_user]["wallet"] += money
            update.message.reply_text("Money has been sent.")
        else:
            update.message.reply_text("You dont have so much money to share.")


    elif msg_list[1] in ["steal"]:
        steal_from = msg_list[2].replace("@","")
        import random
        steal_or_not = random.randint(1,2)
        if steal_or_not == 2: # steal successfull
            money = mono[chat_id]["users"][steal_from]["wallet"]
            how_much = random.randint(1,int(money/2))
            mono[chat_id]["users"][steal_from]["wallet"] -= how_much
            user["wallet"] += how_much
            update.message.reply_text("You were able to steal " + str(how_much) + " from " + steal_from)
        else: # caught
            how_much = random.randint(1,int(user["wallet"]/2))
            user["wallet"] -= how_much
            mono[chat_id]["users"][steal_from]["wallet"] += how_much
            update.message.reply_text("Damn! You got caught and paid " + str(how_much) + " to " + steal_from)


    # elif msg_list[1] in ["rich"]:
    #     from collections import OrderedDict
    #     users = mono[chat_id]["users"]
    #     d_desc = OrderedDict(sorted(users.items(), key=lambda kv: users[kv]["wallet"]))
    #     update.message.reply_text("Ranks :\n1. " + max_user1 + "\n2. " + max_user2 + "\n3. "+ max_user3)

    # Finally save the monopoly data
    save_mono()