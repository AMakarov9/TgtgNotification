from tgtg import TgtgClient
from datetime import datetime
from supabase import create_client
import logging, os, signal, requests, pytz
from time import sleep
import alltokens

supabase_url = alltokens.supabase_url
supabase_key = alltokens.supabase_key
supabase = create_client(supabase_url, supabase_key)

BOT_TOKEN = alltokens.BOT_TOKEN
ACCOUNT_EMAIL = alltokens.ACCOUNT_EMAIL
access_token = alltokens.access_token
refresh_token = alltokens.refresh_token
user_id = alltokens.user_id
cookie = alltokens.cookie

logging.basicConfig (format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)




def sendM(id, beskjed): 
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={id}&text={beskjed}"
    requests.get(url)


def get_tokens(emaila: str):  
    client = TgtgClient(email = emaila)
    client = TgtgClient(access_token=access_token, refresh_token=refresh_token, user_id=user_id, cookie=cookie)
    return client
client = get_tokens(ACCOUNT_EMAIL)

def get_available_items(client: TgtgClient):

    items = client.get_items()
    
    ute = []
    for i in items: 
        if len(i) > 12: 
            if i['in_sales_window'] and i['items_available'] > 0: 
                ute.append(i['store']['store_name'])
                logging.info(f"Added {i['store']['store_name']}")
    
    if len(ute) == 0: 
        return False
    else: 
        return ute
        

def searchingBags():  
    currentOut = [] 
    while True: 
        sleep(10)
        availableBags = get_available_items(client)
        logging.info("Fetching available bags.")
        
        current_datetime = datetime.now()
        oslo_timezone = pytz.timezone('Europe/Oslo')
        oslo_datetime = current_datetime.astimezone(oslo_timezone)
        datetime_string = oslo_datetime.strftime('%Y-%m-%d time: %H:%M:%S')

        if availableBags: 
            for i in availableBags: 
                if i not in currentOut: 
                    data, count = supabase.table('test').select('chat_id', 'default_location').execute() 
                    logging.info(type(data))
                    for item in data[1]:
                        try:
                            logging.info("Sending notification")   
                            chat_id = item['chat_id']
                            sendM(chat_id, f"{i} {datetime_string}")  
                        
                        except Exception as e:
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
    runSearchBags()
