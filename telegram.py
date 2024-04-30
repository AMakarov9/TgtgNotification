# from aiogram import Bot, Dispatcher, executor, types 
# from aiogram.types.message import ContentType
from tgtg import TgtgClient
from datetime import datetime
from supabase import create_client
import logging, os, signal, requests, pytz
from time import strftime, gmtime, sleep
# from urllib.parse import quote
import alltokens
#import location 
#import format


supabase_url = alltokens.supabase_url
supabase_key = alltokens.supabase_key
supabase = create_client(supabase_url, supabase_key)


BOT_TOKEN = alltokens.BOT_TOKEN
ACCOUNT_EMAIL = alltokens.ACCOUNT_EMAIL

access_token = alltokens.access_token
refresh_token = alltokens.refresh_token
user_id = alltokens.user_id
cookie = alltokens.cookie

# bot = Bot(BOT_TOKEN, parse_mode = "HTML", disable_web_page_preview = True)
# dp = Dispatcher(bot)


user_state = dict()


logging.basicConfig (format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)




def sendM(id, beskjed): 
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={id}&text={beskjed}"
    requests.get(url)


def get_tokens(emaila: str): 
    # Tokens are always new for each session. 
    client = TgtgClient(email = emaila)
    #credentials = client.get_credentials()
    client = TgtgClient(access_token=access_token, refresh_token=refresh_token, user_id=user_id, cookie=cookie)
    return client
client = get_tokens(ACCOUNT_EMAIL)

def get_available_items(client: TgtgClient):
#def get_available_items():
    tid = strftime("%H:%M", gmtime())
    #logging.info("Checking for available bags at %s", tid)
    items = client.get_items()
    #itemTest = items
    ute = []
    for i in items: 
        if len(i) > 12: 
            if i['in_sales_window'] and i['items_available'] > 0: 
                ute.append(i['store']['store_name'])
                logging.info(f"Added {i['store']['store_name']}")
    
    if len(ute) == 0: 
        #logging.info("No bags available")
        return False
    else: 
        return ute
        

def searchingBags():  
    currentOut = [] 
    while True: 
        sleep(10)
        availableBags = get_available_items(client)
        #availableBags = items.items
        logging.info("Fetching available bags.")
        
        current_datetime = datetime.now()
        oslo_timezone = pytz.timezone('Europe/Oslo')
        oslo_datetime = current_datetime.astimezone(oslo_timezone)
        datetime_string = oslo_datetime.strftime('%Y-%m-%d time: %H:%M:%S')

        if availableBags: 
            for i in availableBags: 
                if i not in currentOut: 
                    data, count = supabase.table('users').select('chat_id', 'default_location').execute() 
                    logging.info(type(data))
                    for item in data[1]:
                        try:
                            logging.info("Sending notification")
                            # Assuming `sendM` is a function that takes a chat_id and a message
                            chat_id = item['chat_id']
                            sendM(chat_id, f"{i} {datetime_string}")  
                        except Exception as e:
                            # It's good to handle exceptions to understand what's going wrong
                            logging.error(f"Error while sending message: {e}") 
            currentOut = availableBags
        else: 
            currentOut = []

def runSearchBags(): 
    print("searching bags")
    searchingBags()

def signal_handler(sig, frame): 
    def force_exit(): 
        print("Forcing stop of program")
        os.kill(os.getpid(), signal.SIGILL)
    force_exit()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    # thread = threading.Thread(target = runSearchBags)
    # thread.start()
    runSearchBags()
    # executor.start_polling(dp)
 
    
 



# @dp.message_handler(commands = 'start')
# async def command_start(message: types.Message):
#     user_state[message.chat.id] = 'start'
#     response = supabase.table('users').select('chat_id').eq('chat_id', str(message.chat.id)).execute()
#     logging.info(response)
#     if response['data'] == []:
#         supabase.table('users').insert({'chat_id': message.chat.id, 'first_name': message.chat.first_name}).execute()
#         await message.answer (text = "You have been added as user and will receive notification.")

    
# HELP_COMMAND = '''
# /start - Notification when bag available
# /help - All commands
# ''' 
# @dp.message_handler(commands='help')
# async def help_command(message: types.Message): 
#     user_state[message.chat.id] = 'help'

#     await message.reply(text=HELP_COMMAND)

# @dp.message_handler(commands='setaddress')
# async def set_address(message: types.Message): 
#     user_state[message.chat.id] = 'setaddress'
#     await message.answer ("Send preferred starting point for tgtg pickups.")

# @dp.message_handler(content_types = ContentType.TEXT)
# async def message(message: types.Message):
#     # if message.chat.id == 1778925351: 
#     match user_state[message.chat.id]:
#         case "setaddress":
#             #I save two locations. One for google maps, one for entur api. 
#             logging.info("Setting address")
#             encoded = quote(message.text)
#             supabase.table('users').update({'default_location': encoded}).eq('chat_id', str(message.chat.id)).execute()   
#             logging.info("Address set")   
#     user_state[message.chat.id] = None

# @dp.message_handler(commands = 'status')
# async def command_status(message: types.Message): 
#     user_state[message.chat.id] = 'status'
#     await message.reply(text=f"{currentAvail} available")
