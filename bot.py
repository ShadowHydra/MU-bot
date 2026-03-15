import telebot
import feedparser
import time
from deep_translator import GoogleTranslator
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# --- ማስተካከያ ---
API_TOKEN = '8683345761:AAGMWkPkvaG1rzh-yAzu6PPRTr9QKo5Bh48'
CHANNEL_ID = '@wewonalot'
# ----------------

bot = telebot.TeleBot(API_TOKEN)
posted_links = set()

# ፖለቲካን ለመለየት የሚያገለግሉ ቃላት
POLITICAL_KEYWORDS = ['biden', 'trump', 'election', 'court', 'police', 'politics', 'senate', 'democrats', 'republicans', 'usa', 'america']

def translate_amharic(text):
    if not text or len(text) < 5: return ""
    try:
        # ለዝርዝር ዜና የተሻለ ትርጉም
        return GoogleTranslator(source='auto', target='am').translate(text)
    except:
        return text

def get_football_data(url):
    """ትክክለኛ ፎቶ እና ዝርዝር መረጃ ከእግር ኳስ ገጾች ለመውሰድ"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 1. ፎቶ ፍለጋ
        img_tag = soup.find('meta', property='og:image') or soup.find('meta', name='twitter:image')
        image_url = img_tag['content'] if img_tag else None
        
        # 2. ዝርዝር ጽሁፍ ፍለጋ (የመጀመሪያዎቹን 3 አንቀጾች መውሰድ)
        paragraphs = soup.find_all('p')
        full_text = ""
        count = 0
        for p in paragraphs:
            if len(p.text.split()) > 10: # አጫጭር ቃላትን ለመዝለል
                full_text += p.text + " "
                count += 1
            if count == 3: break # 3 አንቀጽ ይበቃል
            
        return image_url, full_text.strip()
    except:
        return None, None

def is_political(text):
    """ዜናው ፖለቲካ መሆኑን ቼክ ማድረጊያ"""
    text_lower = text.lower()
    return any(word in text_lower for word in POLITICAL_KEYWORDS)

def send_news():
    global posted_links
    # 100% የእግር ኳስ ምንጮች ብቻ
    FOOTBALL_FEEDS = [
        'https://www.skysports.com/rss/11667',
        'https://www.manchestereveningnews.co.uk/sport/football/manchester-united-fc/?service=rss',
        'https://content.talksport.com/talksport/rss/football/manchester-united'
    ]
    
    for url in FOOTBALL_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                if entry.link not in posted_links:
                    
                    # የፖለቲካ ዜና ከሆነ እለፈው
                    if is_political(entry.title):
                        continue

                    # የዛሬ ዜና መሆኑን አረጋግጥ
                    pub_date = getattr(entry, 'published_parsed', None)
                    if pub_date and datetime(*pub_date[:6]) < datetime.now() - timedelta(hours=24):
                        continue

                    # ዜናው ስለ ማንቸስተር ዩናይትድ መሆኑን አረጋግጥ
                    if "united" in entry.title.lower() or "manchester" in entry.title.lower():
                        
                        image_url, raw_content = get_football_data(entry.link)
                        
                        # ይዘቱ ካልተገኘ በ RSS ላይ ያለውን ተጠቀም
                        if not raw_content: raw_content = entry.get('summary', '')

                        title_am = translate_amharic(entry.title)
                        content_am = translate_amharic(raw_content)
                        
                        if not title_am: continue

                        caption = (
                            f"🔴 **ሰበር የዩናይትድ ዜና**\n\n"
                            f"📌 **{title_am}**\n\n"
                            f"📝 {content_am}\n\n"
                            f"🔗 [ሙሉውን ለማንበብ እዚህ ይጫኑ]({entry.link})\n\n"
                            f"ተከታተሉን 👉 {CHANNEL_ID}"
                        )
                        
                        try:
                            if image_url and "logo" not in image_url.lower():
                                bot.send_photo(CHANNEL_ID, image_url, caption=caption, parse_mode='Markdown')
                            else:
                                # ፎቶው ሎጎ ከሆነ ወይም ከሌለ በጽሁፍ ብቻ ይላክ (Link Preview ፎቶ ያመጣል)
                                bot.send_message(CHANNEL_ID, caption, parse_mode='Markdown', disable_web_page_preview=False)
                            
                            posted_links.add(entry.link)
                            print(f"✅ ተለጠፈ: {entry.title}")
                            time.sleep(10) # ሰርቨሩ እንዳያግደን እረፍት
                        except Exception as e:
                            print(f"❌ Send Error: {e}")
        except Exception as e:
            print(f"⚠️ Feed Error: {e}")

def initialize():
    print("🔄 የቆዩ ዜናዎችን በማጣራት ላይ... እባክህ ታገስ")
    for url in ['https://www.skysports.com/rss/11667']:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            posted_links.add(entry.link)

if __name__ == "__main__":
    initialize()
    print("🚀 ቦቱ በላቀ ብቃት ስራ ጀምሯል...")
    while True:
        send_news()
        time.sleep(600)
