import telebot
import feedparser
import time
from deep_translator import GoogleTranslator
import requests
from bs4 import BeautifulSoup

# --- ማስተካከያ ---
API_TOKEN = '8683345761:AAGMWkPkvaG1rzh-yAzu6PPRTr9QKo5Bh48'
CHANNEL_ID = '@wewonalot'
# ----------------

bot = telebot.TeleBot(API_TOKEN)

# የተለጠፉ ሊንኮችን ለማስታወስ
posted_links = set()

def translate_amharic(text):
    try:
        # ጽሁፉ ከ 200 ፊደል በላይ ከሆነ ለትርጉም ይመቻል
        return GoogleTranslator(source='auto', target='am').translate(text)
    except:
        return text

def get_image(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # ፎቶውን ለማግኘት የተለያዩ የድረ-ገጽ ምልክቶችን መፈለግ
        img = soup.find('meta', property='og:image') or \
              soup.find('meta', name='twitter:image') or \
              soup.find('link', rel='image_src')
              
        if img:
            return img.get('content') or img.get('href')
    except:
        pass
    # ፎቶ ካልተገኘ የሚለጠፍ የዩናይትድ ሎጎ
    return "https://upload.wikimedia.org/wikipedia/en/7/7a/Manchester_United_FC_crest.svg"

def send_news():
    global posted_links
    
    # የዜና ምንጮች (Sky Sports, MEN, እና Fabrizio Romano በ Nitter በኩል)
    RSS_FEEDS = [
        'https://www.skysports.com/rss/11667',
        'https://www.manchestereveningnews.co.uk/sport/football/manchester-united-fc/?service=rss',
        'https://nitter.privacydev.net/FabrizioRomano/rss' # የፋብሪዚዮ ትዊተር በRSS
    ]
    
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            # ከመጀመሪያዎቹ 3 አዳዲስ ዜናዎች ተነሳ
            for entry in feed.entries[:3]:
                if entry.link not in posted_links:
                    
                    # ስለ ዩናይትድ መሆኑን ቼክ አድርግ (ለፋብሪዚዮ ዜናዎች ጠቃሚ ነው)
                    if "united" in entry.title.lower() or "man u" in entry.title.lower():
                        
                        title_am = translate_amharic(entry.title)
                        image_url = get_image(entry.link)
                        
                        # የጽሁፍ ቅርጽ
                        caption = (
                            f"🔴 **ሰበር የዩናይትድ ዜና**\n\n"
                            f"📌 {title_am}\n\n"
                            f"🔗 [ሙሉውን ለማንበብ እዚህ ይጫኑ]({entry.link})\n\n"
                            f"ተከታተሉን 👉 {CHANNEL_ID}"
                        )
                        
                        try:
                            bot.send_photo(CHANNEL_ID, image_url, caption=caption, parse_mode='Markdown')
                        except:
                            bot.send_message(CHANNEL_ID, caption, parse_mode='Markdown', disable_web_page_preview=False)
                        
                        posted_links.add(entry.link)
                        print(f"✅ ተለጠፈ: {entry.title}")
                        time.sleep(5) # በየመሃሉ እረፍት
        except Exception as e:
            print(f"⚠️ Error fetching {url}: {e}")

def initialize():
    print("🔄 የቆዩ ዜናዎችን በመመዝገብ ላይ... እባክህ ታገስ")
    initial_feeds = [
        'https://www.skysports.com/rss/11667',
        'https://www.manchestereveningnews.co.uk/sport/football/manchester-united-fc/?service=rss'
    ]
    for url in initial_feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            posted_links.add(entry.link)
    print(f"✅ {len(posted_links)} የቆዩ ዜናዎች ተመዝግበዋል። አዲስ ሲመጣ ብቻ ይለጠፋል።")

if __name__ == "__main__":
    print("🚀 ቦቱ ስራ ጀምሯል...")
    initialize()
    
    while True:
        try:
            send_news()
        except Exception as e:
            print(f"❌ Loop Error: {e}")
        
        # በየ 10 ደቂቃው አዲስ ዜና ይፈልጋል
        time.sleep(600)
