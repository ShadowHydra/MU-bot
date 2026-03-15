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
posted_links = {} # ሊንኩን እና የተለጠፈበትን ሰዓት ለመያዝ

def translate_amharic(text):
    if not text: return ""
    try:
        return GoogleTranslator(source='auto', target='am').translate(text)
    except:
        return text

def get_football_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # ትክክለኛ የዜና ፎቶ መፈለግ
        img_tag = soup.find('meta', property='og:image')
        image_url = img_tag['content'] if img_tag else None
        
        # ሎጎ ከሆነ ውድቅ ማድረግ
        if image_url and ("logo" in image_url.lower() or "crest" in image_url.lower() or "placeholder" in image_url.lower()):
            image_url = None

        # ዝርዝር ጽሁፍ (2 አንቀጽ)
        paragraphs = soup.find_all('p')
        summary = " ".join([p.text for p in paragraphs[:2] if len(p.text) > 40])
        
        return image_url, summary
    except:
        return None, None

def send_news():
    global posted_links
    # አላስፈላጊ የቆዩ ሊንኮችን ከዝርዝር ውስጥ ማጽዳት (ከ24 ሰዓት በላይ የቆዩትን)
    now = datetime.now()
    posted_links = {k: v for k, v in posted_links.items() if v > now - timedelta(days=1)}

    RSS_FEEDS = [
        'https://www.skysports.com/rss/11667',
        'https://www.manchestereveningnews.co.uk/sport/football/manchester-united-fc/?service=rss'
    ]
    
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                # 1. የጊዜ ማጣሪያ (ባለፉት 2 ሰዓት ውስጥ የወጣ ብቻ)
                pub_date = getattr(entry, 'published_parsed', None)
                if pub_date:
                    entry_time = datetime(*pub_date[:6])
                    if entry_time < now - timedelta(hours=2): # ከ 2 ሰዓት በፊት የነበረን አይቀበልም
                        continue

                # 2. ድግግሞሽ መከላከያ
                if entry.link not in posted_links:
                    title_lower = entry.title.lower()
                    
                    # 3. የስም ማጣሪያ (ፖለቲካ ለመከላከል)
                    if "manchester" in title_lower or "united" in title_lower:
                        if any(x in title_lower for x in ['biden', 'trump', 'election', 'police']):
                            continue

                        image_url, full_summary = get_football_content(entry.link)
                        if not full_summary: full_summary = entry.get('summary', '')

                        title_am = translate_amharic(entry.title)
                        summary_am = translate_amharic(full_summary[:450])

                        caption = (
                            f"🔴 **ሰበር የዩናይትድ ዜና**\n\n"
                            f"📌 **{title_am}**\n\n"
                            f"📝 {summary_am}...\n\n"
                            f"🔗 [ሙሉውን ለማንበብ እዚህ ይጫኑ]({entry.link})\n\n"
                            f"ተከታተሉን 👉 {CHANNEL_ID}"
                        )

                        try:
                            if image_url:
                                bot.send_photo(CHANNEL_ID, image_url, caption=caption, parse_mode='Markdown')
                            else:
                                bot.send_message(CHANNEL_ID, caption, parse_mode='Markdown', disable_web_page_preview=False)
                            
                            posted_links[entry.link] = now # የተለጠፈበትን ሰዓት መመዝገብ
                            print(f"✅ ተለጠፈ: {entry.title}")
                            time.sleep(10)
                        except Exception as e:
                            print(f"❌ Send Error: {e}")
        except Exception as e:
            print(f"⚠️ Feed Error: {e}")

if __name__ == "__main__":
    print("🚀 ቦቱ በ 2 ሰዓት የጊዜ ገደብ ስራ ጀምሯል...")
    while True:
        send_news()
        time.sleep(600)
