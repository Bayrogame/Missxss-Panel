import customtkinter as ctk
import requests
import os
import sys
import json
import threading
import speech_recognition as sr
import difflib 
from cryptography.fernet import Fernet 
from PIL import Image, ImageTk, ImageSequence, ImageDraw, ImageFont
import webbrowser
import winsound
import pyaudio 
import asyncio
import edge_tts
import warnings 
import subprocess
from dotenv import load_dotenv

try:
    import keyboard 
except ImportError:
    keyboard = None
    print("Lütfen 'pip install keyboard' komutu ile keyboard modülünü kurun!")

# Pygame'in ve Python'un gereksiz uyarılarını gizliyoruz
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
warnings.filterwarnings("ignore", category=UserWarning) 
import pygame

try:
    pygame.mixer.init()
except Exception:
    pass

BASE_URL = "https://api.missxss.com.tr"

# --- GÜNCELLEME SİSTEMİ BİLGİLERİ (BURAYI KENDİNE GÖRE DÜZENLE) ---
APP_VERSION = "2.1"
GITHUB_OWNER = "bayrogame" # GitHub kullanıcı adını buraya yaz
GITHUB_REPO = "Missxss-Panel" # GitHub'da oluşturduğun deponun (repository) adını yaz

def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- GÜVENLİK VE ŞİFRELEME (.env dosyasından çekiliyor) ---
load_dotenv(resource_path(".env"))

gizli_anahtar_str = os.getenv("GIZLI_ANAHTAR")
# Feedback Webhook URL'si
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Eğer yazılımcı .env dosyasını oluşturmayı unutmuşsa uyar ve kapat
if not gizli_anahtar_str or gizli_anahtar_str == "kendi_gizli_anahtarini_buraya_yaz":
    print("⚠️ KRİTİK HATA: Geçerli bir GIZLI_ANAHTAR bulunamadı!")
    print("Lütfen '.env.example' dosyasını kopyalayıp adını '.env' yapın ve içine geçerli bir Fernet anahtarı girin.")
    sys.exit() 

GIZLI_ANAHTAR = gizli_anahtar_str.encode()
sifreleyici = Fernet(GIZLI_ANAHTAR)

OYUN_KISALTMALARI = {
    "gta": "Grand Theft Auto V", "gta 5": "Grand Theft Auto V", "cs": "Counter-Strike 2",
    "valorant": "Valorant", "lol": "League of Legends", "busi": "Business Tour",
    "bizi": "Business Tour", "sohbet": "Just Chatting", "muhabbet": "Just Chatting",
    "ets": "Euro Truck Simulator 2", "ets2": "Euro Truck Simulator 2", "ets 2": "Euro Truck Simulator 2"
}

# --- KOMUT HARİTASI ---
KOMUT_HARITASI = {
    "benim hesaptan yaz": {"endpoint": "/v1/send-message", "dinamik": "message"},
    "yayıncı mesajı": {"endpoint": "/v1/send-message", "dinamik": "message"},
    "kullanıcı mesajı": {"endpoint": "/v1/send-message", "dinamik": "message"},
    "bot mesajı": {"endpoint": "/v1/send-bot-message", "dinamik": "message"},
    "klip al": {"endpoint": "/v1/clip", "payload": {"title": "Harika bir an!", "duration": 30}, "dinamik": "title"},
    "klipal": {"endpoint": "/v1/clip", "payload": {"title": "Harika bir an!", "duration": 30}, "dinamik": "title"},
    "kategori değiştir": {"endpoint": "/v1/game", "dinamik": "game"},
    "kategori": {"endpoint": "/v1/game", "dinamik": "game"},
    "oyun": {"endpoint": "/v1/game", "dinamik": "game"},
    "başlık": {"endpoint": "/v1/title", "dinamik": "title"},
    "başlığı": {"endpoint": "/v1/title", "dinamik": "title"},
    "sohbeti temizle": {"endpoint": "/v1/clear-chat", "payload": None},
    "sohbeti sil": {"endpoint": "/v1/clear-chat", "payload": None},
    "müzik başlat": {"endpoint": "/v1/start-song", "payload": None},
    "müzik dur": {"endpoint": "/v1/stop-song", "payload": None},
    "müzik geç": {"endpoint": "/v1/skip-song", "payload": None},
    "kalkan modunu aç": {"endpoint": "/v1/shield-mode", "payload": {"mode": "on"}},
    "kalkanı aç": {"endpoint": "/v1/shield-mode", "payload": {"mode": "on"}},
    "kalkan aç": {"endpoint": "/v1/shield-mode", "payload": {"mode": "on"}},
    "kalkan modunu kapat": {"endpoint": "/v1/shield-mode", "payload": {"mode": "off"}},
    "kalkanı kapat": {"endpoint": "/v1/shield-mode", "payload": {"mode": "off"}},
    "kalkan kapat": {"endpoint": "/v1/shield-mode", "payload": {"mode": "off"}},
    
    "write from my account": {"endpoint": "/v1/send-message", "dinamik": "message"},
    "streamer message": {"endpoint": "/v1/send-message", "dinamik": "message"},
    "user message": {"endpoint": "/v1/send-message", "dinamik": "message"},
    "bot message": {"endpoint": "/v1/send-bot-message", "dinamik": "message"},
    "take clip": {"endpoint": "/v1/clip", "payload": {"title": "Awesome moment!", "duration": 30}, "dinamik": "title"},
    "take a clip": {"endpoint": "/v1/clip", "payload": {"title": "Awesome moment!", "duration": 30}, "dinamik": "title"},
    "change category": {"endpoint": "/v1/game", "dinamik": "game"},
    "category": {"endpoint": "/v1/game", "dinamik": "game"},
    "game": {"endpoint": "/v1/game", "dinamik": "game"},
    "change title": {"endpoint": "/v1/title", "dinamik": "title"},
    "title": {"endpoint": "/v1/title", "dinamik": "title"},
    "clear chat": {"endpoint": "/v1/clear-chat", "payload": None},
    "delete chat": {"endpoint": "/v1/clear-chat", "payload": None},
    "play music": {"endpoint": "/v1/start-song", "payload": None},
    "start music": {"endpoint": "/v1/start-song", "payload": None},
    "stop music": {"endpoint": "/v1/stop-song", "payload": None},
    "skip music": {"endpoint": "/v1/skip-song", "payload": None},
    "next song": {"endpoint": "/v1/skip-song", "payload": None},
    "shield mode on": {"endpoint": "/v1/shield-mode", "payload": {"mode": "on"}},
    "shield on": {"endpoint": "/v1/shield-mode", "payload": {"mode": "on"}},
    "shield mode off": {"endpoint": "/v1/shield-mode", "payload": {"mode": "off"}},
    "shield off": {"endpoint": "/v1/shield-mode", "payload": {"mode": "off"}},
}

def get_config_path():
    appdata_dir = os.getenv('APPDATA')
    if not appdata_dir: appdata_dir = os.path.expanduser("~") 
    config_dir = os.path.join(appdata_dir, "MissxssPanel_v4")
    if not os.path.exists(config_dir): os.makedirs(config_dir)
    return os.path.join(config_dir, "ayar.json")

CONFIG_FILE = get_config_path()

def load_ayar():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def save_ayar(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

def load_api_key():
    data = load_ayar()
    kayitli_veri = data.get("api_key", "")
    if kayitli_veri:
        try: return sifreleyici.decrypt(kayitli_veri.encode()).decode()
        except Exception: return kayitli_veri
    return ""

def save_api_key(key):
    sifrelenmis_key = sifreleyici.encrypt(key.encode()).decode()
    data = load_ayar()
    data["api_key"] = sifrelenmis_key
    save_ayar(data)

def create_fa_icon(unicode_char, font_path, size=20, color="white"):
    try:
        render_size = size * 4  
        font_size = int(render_size * 0.7) 
        font = ImageFont.truetype(font_path, font_size)
        img = Image.new("RGBA", (render_size, render_size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        try:
            draw.text((render_size/2, render_size/2), unicode_char, font=font, fill=color, anchor="mm")
        except Exception:
            draw.text((render_size*0.15, render_size*0.15), unicode_char, font=font, fill=color)
        return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
    except Exception as e:
        return None

# --- DİL SÖZLÜĞÜ ---
LANG_DICT = {
    "tr": {
        "api_key": " API Key Ayarı", "api_ph": "API Anahtarınızı Girin...", "save": " Kaydet",
        "mic": " Mikrofon Ayarı", "def_mic": "Varsayılan Mikrofon", "success_snd": "Başarı Sesi (Bip)",
        "voice_conf": "Sesli Onay (Asistan)", "auto_start": "Otomatik Başlat",
        "ast_open": " ASİSTANI AÇ\n(Tetikleyici: 'Miss')", "ast_close": " ASİSTANI KAPAT",
        "c_cmd": " Özel Komutlar", "guide": " Komut Kılavuzu", "hotkey": " Kısayol Tuşları",
        "feedback": " Geri Bildirim", "fb_title": "Geri Bildirim / Öneri Gönder", "fb_ph": "Bulduğunuz bir hatayı, önerinizi veya mesajınızı buraya yazın...", "fb_send": " Gönder", "fb_sent": "✅ Geri bildiriminiz başarıyla iletildi! Teşekkürler.", "fb_err": "⚠️ Mesaj iletilemedi, internet bağlantınızı kontrol edin.", "fb_empty": "⚠️ Lütfen boş mesaj göndermeyin.",
        "prod": "Yapımcı : Bayrogame  ", "lang_lbl": " Dil / Language",
        "tab_main": "Ana Panel", "tab_dc": "Discord Kontrolcü", "tab_stream": "Yayın Kontrolcü",
        "msg_title": " Mesajlaşma", "pub_msg": "Yayıncı Mesajı", "bot_msg": "Bot Mesajı", 
        "msg_ph": "Gönderilecek mesajı buraya yazın...", "send": " Gönder",
        "stream_info": " Yayın Bilgisi", "new_cat": "Yeni Kategori (Örn: sohbet, valorant)",
        "new_title": "Yeni Yayın Başlığı", "update": " Güncelle", "clip": " Detaylı Klip Alma",
        "clip_ph": "Klip Başlığı (Boş bırakılabilir)", "dur_ph": "Süre (5-180 sn)",
        "take_clip": " KLİP AL", "reji": " Reji, Müzik & Temizlik", "play": " BAŞLAT",
        "pause": " DURDUR", "skip": " GEÇ", "clear_chat": " SOHBETİ TEMİZLE",
        "mod": " Manuel Moderasyon", "shield": "Kalkan Modu", "usr_ph": "İşlem yapılacak kullanıcı adı...",
        "ban": " BANLA", "timeout": " SUSTUR", "unban": " BAN KALDIR", "load_id": " Son ID'leri Yükle",
        "srv_stat": " Sunucu Durumu Sorgula", "srv_ph": "Sunucu (Guild) ID...", "query": " Sorgula",
        "dc_msg": " Discord Kanala Mesaj Gönder", "ch_ph": "Kanal ID (Zorunlu)", "n_msg_ph": "Normal Mesaj Metni...",
        "emb_title": "Embed Başlığı", "emb_desc": "Embed Açıklaması...", "color_ph": "Renk Kodu",
        "mute_all_title": " Kanaldaki Herkesi Sustur / Aç", "vc_ph": "İşlem Yapılacak Ses Kanalı ID'si...",
        "mute_all": " Herkesi Sustur", "unmute_all": " Herkesin Sesini Aç", "pull_title": " Herkesi Bu Kanala Çek",
        "pull_ph": "Herkesin Çekileceği Hedef Ses Kanalı ID'si...", "pull_btn": " Herkesi Çek",
        "live_stats": " Canlı Yayın İstatistikleri", "live_track": "Canlı Takip (30sn)",
        "viewers": "İzleyici:", "followers": "Takipçi:", "category": "Kategori:",
        "get_meta": " Yayın Bilgilerini Getir", "get_meta_btn": " Bilgileri Sorgula",
        "get_subs": " Kick Abonelerini Getir", "inc_exp": "Süresi Bitenleri Dahil Et",
        "lim_ph": "Limit (Örn: 20)", "off_ph": "Offset (Örn: 0)", "get_act": " Son Aktiviteleri Getir",
        "get_mod": " Moderasyon Kayıtlarını Getir", "ai_title": " AI Chatbot Kontrolü",
        "ai_clear": " Hafızayı Temizle", "ai_send": " Seçili Prompt'u Gönder", "sys_log": " Sistem Kayıtları",
        "eula_title": "YASAL UYARI / LEGAL WARNING", 
        "eula_txt": "Bu yazılımın yasa dışı veya kötü amaçlı kullanımından\nkaynaklanan her türlü hukuki ve cezai sorumluluk\ntamamen kullanıcıya aittir.\n\nAny legal and penal responsibility arising from\nthe illegal or malicious use of this software\nbelongs entirely to the user.",
        "eula_btn": "Onaylıyorum / Accept", "palette": " Renk Paleti", "ready_colors": "Hazır Renkler",
        "close": "Kapat", "query_res": "Sorgu Sonucu: ", "err_api": "⚠️ Lütfen önce soldaki menüden API anahtarınızı girip kaydedin!",
        "start_msg": f"Missxss Gelişmiş Panel v{APP_VERSION} başlatıldı. Bayrogame gururla sunar...", "loading": "Yükleniyor...", "no_prompt": "Gömülü prompt bulunamadı",
        "hk_toggle_mic": "Sesli Asistan Aç/Kapat", "hk_clear_chat": "Sohbeti Temizle", "hk_take_clip": "Hızlı Klip Al (30 Saniye)",
        "hk_toggle_shield": "Kalkan Modu Aç/Kapat", "hk_play_music": "Müzik Başlat", "hk_stop_music": "Müzik Durdur",
        "hk_skip_music": "Müzik Geç", "hk_clear_ai": "AI Hafızasını Temizle", "hk_desc": "Oyun içindeyken bile programı kontrol etmenizi sağlar.",
        "hk_set": "Tuş Ata", "hk_del": "Sil", "hk_unassigned": "Atanmadı", "hk_press": "Tuşa Basın...",
        "c_cmd_desc": "Asistan kelimeyi yanlış anlıyorsa veya farklı bir kelime kullanmak istiyorsan eşleştir.",
        "c_cmd_ph": "Söylenen (Örn: kılıf al / kesit al)", "c_cmd_add": "Ekle", "c_cmd_triggers": "tetikler:",
        "cmd_klip_al": "klip al", "cmd_kategori_değiştir": "kategori değiştir", "cmd_başlık": "başlık",
        "cmd_sohbeti_temizle": "sohbeti temizle", "cmd_müzik_başlat": "müzik başlat", "cmd_müzik_dur": "müzik dur",
        "cmd_müzik_geç": "müzik geç", "cmd_kalkanı_aç": "kalkanı aç", "cmd_kalkanı_kapat": "kalkanı kapat",
        "cmd_herkesi_sustur": "herkesi sustur", "cmd_herkesin_sesini_aç": "herkesin sesini aç", "cmd_herkesi_bu_kanala_çek": "herkesi bu kanala çek",
        "log_msg_sent": "Mesaj Gönderiliyor", "log_title_upd": "Başlık Güncelleniyor",
        "log_cat_upd": "Kategori Güncelleniyor", "log_clip": "Klip Alınıyor",
        "log_clear": "Sohbet Temizleniyor", "log_play": "Şarkı Başlatılıyor",
        "log_stop": "Şarkı Durduruluyor", "log_skip": "Şarkı Geçiliyor",
        "log_ban": "Banlanıyor", "log_timeout": "Susturuluyor", "log_unban": "Ban Kaldırılıyor",
        "log_shield_on": "Kalkan Modu Açılıyor", "log_shield_off": "Kalkan Modu Kapatılıyor",
        "log_discord_msg": "Discord Mesajı", "log_discord_mute": "Herkes Susturuluyor",
        "log_discord_unmute": "Herkesin Sesi Açılıyor", "log_discord_pull": "Herkes Çekiliyor",
        "log_ai_char": "AI Karakteri Değişiyor", "log_ai_clear": "AI Hafızası Temizleniyor",
        "upd_title": "GÜNCELLEME İNDİRİLİYOR / UPDATING",
        "upd_done": "Güncelleme hazır! Program kapanıyor, lütfen yeniden açın.\n(Update ready! Closing... Please reopen manually.)",
        "guide_text": """Asistanı uyandırmak için cümlenize daima "Miss" diyerek başlamalısınız (Mis, mış, miş olarak da algılayabilir).

💬 MESAJLAŞMA KOMUTLARI
• Kendi profilinizden yazmak için: "Miss benim hesaptan yaz [mesajınız]"
• Bot profilinden yazmak için: "Miss bot mesajı [mesajınız]"

🎮 YAYIN BİLGİSİ KOMUTLARI
• Oyun/Kategori değiştirmek için: "Miss oyun [oyun adı]" veya "Miss kategori [oyun adı]"
• Yayının başlığını değiştirmek için: "Miss başlık [yeni başlık]"

🎵 REJİ VE AKSİYON KOMUTLARI
• Klip almak için: "Miss klip al [varsa başlık]" (Varsayılan 30 sn)
• Müziği yönetmek için: "Miss müzik başlat", "Miss müzik dur", "Miss müzik geç"
• Sohbeti temizlemek için: "Miss sohbeti temizle"

📢 DİSCORD SESLİ KOMUTLARI (Panelde Kanal ID girilmiş olmalıdır!)
• Herkesi susturmak için: "Miss kanaldaki herkesi sustur" veya "Miss toplu sustur"
• Sesleri açmak için: "Miss herkesin sesini aç" veya "Miss sesleri aç"
• Herkesi bir odaya çekmek için: "Miss herkesi bu kanala çek" veya "Miss odaya çek"

🛡️ GÜVENLİK VE KALKAN
• Kalkan modunu aç/kapat için: "Miss kalkan modunu aç" veya "Miss kalkanı kapat"
• ⚠️ ÖNEMLİ UYARI: "Ban" ve "Sustur/Time Out" komutları yanlışlıkla kullanım riskine karşı SESLİ KOMUTA KAPALIDIR."""
    },
    "en": {
        "api_key": " API Key Settings", "api_ph": "Enter your API Key...", "save": " Save",
        "mic": " Microphone Config", "def_mic": "Default Microphone", "success_snd": "Success Sound (Beep)",
        "voice_conf": "Voice Confirm (Assistant)", "auto_start": "Auto Start",
        "ast_open": " OPEN ASSISTANT\n(Trigger: 'Miss')", "ast_close": " CLOSE ASSISTANT",
        "c_cmd": " Custom Commands", "guide": " Command Guide", "hotkey": " Hotkeys",
        "feedback": " Feedback", "fb_title": "Send Feedback / Suggestion", "fb_ph": "Type your suggestions, bug reports, or thoughts here...", "fb_send": " Send", "fb_sent": "✅ Feedback sent successfully! Thank you.", "fb_err": "⚠️ Failed to send. Please check your internet connection.", "fb_empty": "⚠️ Please do not send an empty message.",
        "prod": "Producer : Bayrogame  ", "lang_lbl": " Language / Dil",
        "tab_main": "Main Panel", "tab_dc": "Discord Control", "tab_stream": "Stream Control",
        "msg_title": " Messaging", "pub_msg": "Streamer Msg", "bot_msg": "Bot Msg", 
        "msg_ph": "Type your message here...", "send": " Send",
        "stream_info": " Stream Info", "new_cat": "New Category (e.g. Just Chatting)",
        "new_title": "New Stream Title", "update": " Update", "clip": " Detailed Clipping",
        "clip_ph": "Clip Title (Optional)", "dur_ph": "Duration (5-180 s)",
        "take_clip": " TAKE CLIP", "reji": " Director, Music & Clean", "play": " PLAY",
        "pause": " PAUSE", "skip": " SKIP", "clear_chat": " CLEAR CHAT",
        "mod": " Manual Moderation", "shield": "Shield Mode", "usr_ph": "Target username...",
        "ban": " BAN", "timeout": " TIMEOUT", "unban": " UNBAN", "load_id": " Load Last IDs",
        "srv_stat": " Server Status Query", "srv_ph": "Server (Guild) ID...", "query": " Query",
        "dc_msg": " Send Discord Message", "ch_ph": "Channel ID (Required)", "n_msg_ph": "Normal Message Text...",
        "emb_title": "Embed Title", "emb_desc": "Embed Description...", "color_ph": "Color Code",
        "mute_all_title": " Mute / Unmute All in Channel", "vc_ph": "Target Voice Channel ID...",
        "mute_all": " Mute All", "unmute_all": " Unmute All", "pull_title": " Pull Everyone Here",
        "pull_ph": "Target Voice Channel ID to pull to...", "pull_btn": " Pull Everyone",
        "live_stats": " Live Stream Stats", "live_track": "Live Tracking (30s)",
        "viewers": "Viewers:", "followers": "Followers:", "category": "Category:",
        "get_meta": " Get Stream Meta", "get_meta_btn": " Query Info",
        "get_subs": " Get Kick Subscribers", "inc_exp": "Include Expired",
        "lim_ph": "Limit (e.g. 20)", "off_ph": "Offset (e.g. 0)", "get_act": " Get Recent Activity",
        "get_mod": " Get Moderation Logs", "ai_title": " AI Chatbot Control",
        "ai_clear": " Clear Memory", "ai_send": " Send Selected Prompt", "sys_log": " System Logs",
        "eula_title": "LEGAL WARNING / YASAL UYARI", 
        "eula_txt": "Any legal and penal responsibility arising from\nthe illegal or malicious use of this software\nbelongs entirely to the user.\n\nBu yazılımın yasa dışı veya kötü amaçlı kullanımından\nkaynaklanan her türlü hukuki ve cezai sorumluluk\ntamamen kullanıcıya aittir.",
        "eula_btn": "Accept / Onaylıyorum", "palette": " Color Palette", "ready_colors": "Ready Colors",
        "close": "Close", "query_res": "Query Result: ", "err_api": "⚠️ Please enter and save your API key from the left menu first!",
        "start_msg": f"Missxss Advanced Panel v{APP_VERSION} started. Proudly presented by Bayrogame...", "loading": "Loading...", "no_prompt": "No embedded prompt found",
        "hk_toggle_mic": "Toggle Voice Assistant", "hk_clear_chat": "Clear Chat", "hk_take_clip": "Quick Clip (30 Seconds)",
        "hk_toggle_shield": "Toggle Shield Mode", "hk_play_music": "Play Music", "hk_stop_music": "Stop Music",
        "hk_skip_music": "Skip Music", "hk_clear_ai": "Clear AI Memory", "hk_desc": "Allows you to control the program even while in-game.",
        "hk_set": "Set Key", "hk_del": "Del", "hk_unassigned": "Unassigned", "hk_press": "Press Key...",
        "c_cmd_desc": "Map a word if the assistant misunderstands or if you want to use a custom word.",
        "c_cmd_ph": "Voice (e.g. record this)", "c_cmd_add": "Add", "c_cmd_triggers": "triggers:",
        "cmd_klip_al": "take clip", "cmd_kategori_değiştir": "change category", "cmd_başlık": "change title",
        "cmd_sohbeti_temizle": "clear chat", "cmd_müzik_başlat": "play music", "cmd_müzik_dur": "stop music",
        "cmd_müzik_geç": "skip music", "cmd_kalkanı_aç": "shield on", "cmd_kalkanı_kapat": "shield off",
        "cmd_herkesi_sustur": "mute all", "cmd_herkesin_sesini_aç": "unmute all", "cmd_herkesi_bu_kanala_çek": "pull everyone",
        "log_msg_sent": "Sending Message", "log_title_upd": "Updating Title",
        "log_cat_upd": "Updating Category", "log_clip": "Taking Clip",
        "log_clear": "Clearing Chat", "log_play": "Playing Song",
        "log_stop": "Stopping Song", "log_skip": "Skipping Song",
        "log_ban": "Banning", "log_timeout": "Timing out", "log_unban": "Unbanning",
        "log_shield_on": "Shield Mode ON", "log_shield_off": "Shield Mode OFF",
        "log_discord_msg": "Discord Message", "log_discord_mute": "Muting Everyone",
        "log_discord_unmute": "Unmuting Everyone", "log_discord_pull": "Pulling Everyone",
        "log_ai_char": "Changing AI Role", "log_ai_clear": "Clearing AI Memory",
        "upd_title": "GÜNCELLENİYOR / UPDATING",
        "upd_done": "Update ready! Closing program, please reopen it manually.\n(Güncelleme hazır! Kapanıyor...)",
        "guide_text": """To wake up the assistant, always start your sentence with "Miss".

💬 MESSAGING COMMANDS
• Write from your profile: "Miss write from my account [message]"
• Write from bot profile: "Miss bot message [message]"

🎮 STREAM INFO COMMANDS
• Change category: "Miss change category [game]" or "Miss game [game]"
• Change title: "Miss change title [new title]"

🎵 DIRECTOR AND ACTION COMMANDS
• Take a clip: "Miss take clip [optional title]" (Default 30s)
• Manage music: "Miss play music", "Miss stop music", "Miss skip music"
• Clear chat: "Miss clear chat"

📢 DISCORD VOICE COMMANDS (Channel ID must be set in Panel!)
• Mute all: "Miss mute all"
• Unmute all: "Miss unmute all"
• Pull everyone: "Miss pull everyone"

🛡️ SECURITY AND SHIELD
• Shield on/off: "Miss shield on" or "Miss shield off"
• ⚠️ WARNING: "Ban" and "Timeout" are disabled for voice commands."""
    }
}

ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

class MissxssPanel(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        
        self.current_lang = load_ayar().get("language", "tr")

        self.title("Missxss Gelişmiş Panel")
        self.geometry("1050x800") 
        self.resizable(False, False)

        self.dinleme_aktif = False
        self.ses_thread = None
        self.kilavuz_penceresi = None 
        self.sonuc_penceresi = None
        self.kisayol_penceresi = None
        self.renk_penceresi = None 
        self.ozel_komut_penceresi = None
        self.guncelleme_penceresi = None
        self.feedback_penceresi = None
        
        self.gif_kareleri = []
        self.mevcut_kare_index = 0
        self.animasyon_id = None

        self.prompts_klasoru_tr = resource_path("ai_prompts_tr")
        self.prompts_klasoru_en = resource_path("ai_prompts_en")
        self.fa_font_path = resource_path("fa-solid.otf")

        self.ikonlar = {}
        if os.path.exists(self.fa_font_path):
            self.ikonlar["save"] = create_fa_icon("\uf0c7", self.fa_font_path, color="#ffffff")
            self.ikonlar["mic"] = create_fa_icon("\uf130", self.fa_font_path, size=24, color="#ffffff")
            self.ikonlar["mic_off"] = create_fa_icon("\uf131", self.fa_font_path, size=24, color="#ffffff")
            self.ikonlar["book"] = create_fa_icon("\uf02d", self.fa_font_path, color="#34dbeb")
            self.ikonlar["keyboard"] = create_fa_icon("\uf11c", self.fa_font_path, color="#f1c40f")
            self.ikonlar["send"] = create_fa_icon("\uf1d8", self.fa_font_path, color="#00d2ff")
            self.ikonlar["refresh"] = create_fa_icon("\uf021", self.fa_font_path, color="#2ecc71")
            self.ikonlar["play"] = create_fa_icon("\uf04b", self.fa_font_path, color="#53fc18")
            self.ikonlar["pause"] = create_fa_icon("\uf04c", self.fa_font_path, color="#ff4757")
            self.ikonlar["skip"] = create_fa_icon("\uf051", self.fa_font_path, color="#f1c40f")
            self.ikonlar["palette"] = create_fa_icon("\uf53f", self.fa_font_path, color="#f368e0")
            self.ikonlar["brain"] = create_fa_icon("\uf5dc", self.fa_font_path, color="#000000")
            self.ikonlar["clip"] = create_fa_icon("\uf008", self.fa_font_path, color="#ffffff") 
            self.ikonlar["broom"] = create_fa_icon("\uf51a", self.fa_font_path, color="#ffffff") 
            self.ikonlar["hammer"] = create_fa_icon("\uf0e3", self.fa_font_path, color="#ffffff") 
            self.ikonlar["clock"] = create_fa_icon("\uf017", self.fa_font_path, color="#ffffff") 
            self.ikonlar["unlock"] = create_fa_icon("\uf09c", self.fa_font_path, color="#ffffff")
            self.ikonlar["mute_all"] = create_fa_icon("\uf6a9", self.fa_font_path, color="#ffffff") 
            self.ikonlar["unmute_all"] = create_fa_icon("\uf028", self.fa_font_path, color="#ffffff") 
            self.ikonlar["magnet"] = create_fa_icon("\uf076", self.fa_font_path, color="#2c3e50") 
            self.ikonlar["signal"] = create_fa_icon("\uf51e", self.fa_font_path, color="#2c3e50") 
            self.ikonlar["star"] = create_fa_icon("\uf005", self.fa_font_path, color="#000000") 
            self.ikonlar["gear"] = create_fa_icon("\uf013", self.fa_font_path, color="#9b59b6") 
            self.ikonlar["globe"] = create_fa_icon("\uf0ac", self.fa_font_path, size=22, color="#bdc3c7")
            self.ikonlar["envelope"] = create_fa_icon("\uf0e0", self.fa_font_path, color="#f1c40f") # Feedback ikonu
            
            self.ikonlar["lbl_key"] = create_fa_icon("\uf084", self.fa_font_path, size=22, color="#f1c40f") 
            self.ikonlar["lbl_mic"] = create_fa_icon("\uf130", self.fa_font_path, size=22, color="#43B581") 
            self.ikonlar["lbl_chat"] = create_fa_icon("\uf086", self.fa_font_path, size=22, color="#3498db") 
            self.ikonlar["lbl_game"] = create_fa_icon("\uf11b", self.fa_font_path, size=22, color="#9b59b6") 
            self.ikonlar["lbl_clip"] = create_fa_icon("\uf008", self.fa_font_path, size=22, color="#e74c3c") 
            self.ikonlar["lbl_music"] = create_fa_icon("\uf001", self.fa_font_path, size=22, color="#e67e22") 
            self.ikonlar["lbl_shield"] = create_fa_icon("\uf3ed", self.fa_font_path, size=22, color="#ff4757") 
            self.ikonlar["lbl_search"] = create_fa_icon("\uf002", self.fa_font_path, size=22, color="#7289da") 
            self.ikonlar["lbl_mega"] = create_fa_icon("\uf0a1", self.fa_font_path, size=22, color="#ffa502") 
            self.ikonlar["lbl_magnet"] = create_fa_icon("\uf076", self.fa_font_path, size=22, color="#00d2ff") 
            self.ikonlar["lbl_signal"] = create_fa_icon("\uf519", self.fa_font_path, size=22, color="#00d2ff") 
            self.ikonlar["lbl_star"] = create_fa_icon("\uf005", self.fa_font_path, size=22, color="#53fc18") 
            self.ikonlar["lbl_bell"] = create_fa_icon("\uf0f3", self.fa_font_path, size=22, color="#f1c40f") 
            self.ikonlar["lbl_robot"] = create_fa_icon("\uf544", self.fa_font_path, size=22, color="#a29bfe") 
            self.ikonlar["lbl_term"] = create_fa_icon("\uf120", self.fa_font_path, size=22, color="#43B581") 
            self.ikonlar["lbl_chart"] = create_fa_icon("\uf080", self.fa_font_path, size=22, color="#e74c3c") 
        else:
            print("FontAwesome dosyası bulunamadı, ikonlar yüklenmeyecek.")

        ayar = load_ayar()
        self.kisayollar = ayar.get("kisayollar", {})
        
        self.kisayol_tanimlari = {
            "asistan_toggle": {"isim_key": "hk_toggle_mic", "fonksiyon": self.ses_gecis_yap_kisayol},
            "sohbet_temizle": {"isim_key": "hk_clear_chat", "fonksiyon": self.sohbeti_temizle},
            "klip_al": {"isim_key": "hk_take_clip", "fonksiyon": self.hizli_klip_al_kisayol},
            "kalkan_toggle": {"isim_key": "hk_toggle_shield", "fonksiyon": self.kalkan_toggle_kisayol},
            "muzik_baslat": {"isim_key": "hk_play_music", "fonksiyon": self.sarki_baslat},
            "muzik_durdur": {"isim_key": "hk_stop_music", "fonksiyon": self.sarki_durdur},
            "muzik_gec": {"isim_key": "hk_skip_music", "fonksiyon": self.sarki_gec},
            "ai_temizle": {"isim_key": "hk_clear_ai", "fonksiyon": self.ai_hafiza_temizle}
        }
        
        self.gercek_komutlar_keys = ["klip al", "kategori değiştir", "başlık", "sohbeti temizle", "müzik başlat", "müzik dur", "müzik geç", "kalkanı aç", "kalkanı kapat", "herkesi sustur", "herkesin sesini aç", "herkesi bu kanala çek"]

        try:
            self.iconbitmap(resource_path("missxss.ico"))
        except Exception: pass

        self.arayuzu_olustur()
        self.bind_all("<Button-1>", self.bosluga_tiklama_kontrolu)
        
        if load_ayar().get("eula_accepted", False):
            self.after(0, self.deiconify)
            self.after(250, self.guvenli_ikon_yukle)
            self.gif_animasyonunu_baslat()
            self.kisayollari_uygula()
            
            if load_ayar().get("oto_baslat", False):
                self.after(1000, self.ses_gecis_yap) 
        else:
            self.yasal_uyari_goster()

        self.canli_istatistik_dongusu()
        self.otomatik_guncelleme_kontrolu()

    # --- SESSİZ OTOMATİK GÜNCELLEME SİSTEMİ ---
    def otomatik_guncelleme_kontrolu(self):
        def check():
            try:
                url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    latest_version_tag = data.get("tag_name", "") 
                    
                    latest_clean = latest_version_tag.replace("v", "").replace("V", "").strip()
                    current_clean = APP_VERSION.strip()
                    
                    if latest_clean and latest_clean != current_clean:
                        try:
                            if float(latest_clean) > float(current_clean):
                                download_url = ""
                                for asset in data.get("assets", []):
                                    if asset.get("name", "").lower().endswith(".exe"):
                                        download_url = asset.get("browser_download_url")
                                        break
                                
                                if download_url:
                                    self.after(2000, lambda: self.sessiz_guncelleme_baslat(latest_version_tag, download_url))
                        except ValueError:
                            pass 
            except Exception:
                pass 
        
        threading.Thread(target=check, daemon=True).start()

    def sessiz_guncelleme_baslat(self, yeni_surum, link):
        self.guncelleme_penceresi = ctk.CTkToplevel(self)
        self.guncelleme_penceresi.title(self.T("upd_title"))
        self.guncelleme_penceresi.geometry("450x200")
        self.guncelleme_penceresi.resizable(False, False)
        self.guncelleme_penceresi.attributes("-topmost", True)
        self.guncelleme_penceresi.protocol("WM_DELETE_WINDOW", lambda: None) 
        
        self.guncelleme_penceresi.grab_set()
        self.guncelleme_penceresi.focus_force()
        
        try: self.guncelleme_penceresi.iconbitmap(resource_path("missxss.ico"))
        except: pass

        ctk.CTkLabel(self.guncelleme_penceresi, text="⬇️", font=ctk.CTkFont(size=40)).pack(pady=(20, 5))
        
        durum_metni = f"v{yeni_surum.replace('v', '')} indiriliyor, lütfen bekleyin...\n(Downloading update...)"
        self.lbl_guncelleme_durum = ctk.CTkLabel(self.guncelleme_penceresi, text=durum_metni, font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_guncelleme_durum.pack(pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(self.guncelleme_penceresi, width=350, progress_color="#3498db")
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)

        threading.Thread(target=self._dosyayi_indir_ve_kur, args=(link,), daemon=True).start()

    def _dosyayi_indir_ve_kur(self, link):
        try:
            if not getattr(sys, 'frozen', False):
                self.after(0, lambda: self.lbl_guncelleme_durum.configure(text="Sadece .EXE dosyaları güncellenebilir!\n(.py dosyası korumaya alındı)", text_color="#f1c40f"))
                self.after(4000, lambda: self.guncelleme_penceresi.destroy() if self.guncelleme_penceresi else None)
                return

            exe_yolu = sys.executable
            mevcut_dizin = os.path.dirname(exe_yolu)
            mevcut_exe_adi = os.path.basename(exe_yolu)
            yeni_exe_yolu = os.path.join(mevcut_dizin, mevcut_exe_adi + ".update")

            response = requests.get(link, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(yeni_exe_yolu, 'wb') as file:
                downloaded_size = 0
                for data in response.iter_content(chunk_size=4096):
                    downloaded_size += len(data)
                    file.write(data)
                    if total_size > 0:
                        progress = downloaded_size / total_size
                        self.after(0, lambda p=progress: self.progress_bar.set(p))

            self.after(0, lambda: self.lbl_guncelleme_durum.configure(text=self.T("upd_done"), text_color="#2ecc71"))
            
            temp_dir = os.environ.get('TEMP', mevcut_dizin)
            bat_yolu = os.path.join(temp_dir, "missxss_updater.bat")
            
            bat_icerik = f"""@echo off
cd /d "{mevcut_dizin}"
:dongu
timeout /t 1 /nobreak > NUL
del "{mevcut_exe_adi}"
if exist "{mevcut_exe_adi}" goto dongu
ren "{mevcut_exe_adi}.update" "{mevcut_exe_adi}"

set _MEIPASS2=
set _MEIPASS1=
set _MEIPASS=
set PYINSTALLER_STRICT_ENV=

del "%~f0"
"""
            with open(bat_yolu, "w", encoding="utf-8") as bat_file:
                bat_file.write(bat_icerik)
            
            temiz_env = os.environ.copy()
            for k in list(temiz_env.keys()):
                if 'MEIPASS' in k or 'PYINSTALLER' in k or 'PYI' in k:
                    temiz_env.pop(k, None)
                    
            if getattr(sys, 'frozen', False):
                meipass = sys._MEIPASS
                if 'PATH' in temiz_env:
                    paths = temiz_env['PATH'].split(os.pathsep)
                    paths = [p for p in paths if os.path.normpath(p) != os.path.normpath(meipass)]
                    temiz_env['PATH'] = os.pathsep.join(paths)
            
            subprocess.Popen(bat_yolu, shell=True, creationflags=subprocess.CREATE_NO_WINDOW, env=temiz_env)
            
            self.after(4000, self.tamamen_kapat)
            
        except Exception as e:
            self.after(0, lambda: self.lbl_guncelleme_durum.configure(text=f"Hata / Error: {str(e)}", text_color="#ff4757"))
            self.after(3000, lambda: self.guncelleme_penceresi.destroy() if self.guncelleme_penceresi else None)

    # --- FEEDBACK / GERİ BİLDİRİM SİSTEMİ ---
    def feedback_penceresi_ac(self):
        if self.feedback_penceresi is not None and self.feedback_penceresi.winfo_exists():
            self.feedback_penceresi.focus()
            return
            
        if not WEBHOOK_URL or WEBHOOK_URL == "webhook_linkini_buraya_yapistir":
            self.log_yaz("⚠️ Feedback sistemi kapalı (.env içinde DISCORD_WEBHOOK_URL ayarlanmamış).")
            return

        self.feedback_penceresi = ctk.CTkToplevel(self)
        self.feedback_penceresi.title(self.T("fb_title"))
        self.feedback_penceresi.geometry("500x350")
        self.feedback_penceresi.attributes("-topmost", True)
        self.feedback_penceresi.resizable(False, False)
        
        try: self.feedback_penceresi.after(200, lambda: self.feedback_penceresi.iconbitmap(resource_path("missxss.ico")))
        except: pass

        ctk.CTkLabel(self.feedback_penceresi, text=self.T("fb_title"), image=self.ikonlar.get("envelope"), compound="left", font=ctk.CTkFont(size=18, weight="bold"), text_color="#f1c40f").pack(pady=(20, 10))
        
        self.fb_textbox = ctk.CTkTextbox(self.feedback_penceresi, width=450, height=180, font=ctk.CTkFont(size=13))
        self.fb_textbox.pack(padx=20, pady=10)
        self.fb_textbox.insert("0.0", self.T("fb_ph"))
        
        # Placeholder silme efekti
        def clear_placeholder(event):
            if self.fb_textbox.get("0.0", "end-1c") == self.T("fb_ph"):
                self.fb_textbox.delete("0.0", "end")
        self.fb_textbox.bind("<FocusIn>", clear_placeholder)

        ctk.CTkButton(self.feedback_penceresi, text=self.T("fb_send"), image=self.ikonlar.get("send"), font=ctk.CTkFont(weight="bold"), fg_color="#3498db", hover_color="#2980b9", command=self.feedback_gonder_btn, width=200, height=40).pack(pady=(5, 20))

    def feedback_gonder_btn(self):
        mesaj = self.fb_textbox.get("0.0", "end-1c").strip()
        if not mesaj or mesaj == self.T("fb_ph"):
            self.log_yaz(self.T("fb_empty"))
            return
            
        def yolla():
            data = {
                "username": "Missxss Panel Feedback",
                "embeds": [{
                    "title": "📬 Yeni Geri Bildirim",
                    "description": mesaj,
                    "color": 15844367, # Altın Sarısı
                    "footer": {"text": f"Sürüm: v{APP_VERSION}"}
                }]
            }
            try:
                requests.post(WEBHOOK_URL, json=data, timeout=5)
                self.log_yaz(self.T("fb_sent"))
                self.after(0, lambda: self.feedback_penceresi.destroy() if self.feedback_penceresi else None)
            except Exception as e:
                self.log_yaz(f"{self.T('fb_err')} ({e})")
                
        self.fb_textbox.configure(state="disabled")
        threading.Thread(target=yolla, daemon=True).start()

    def T(self, key):
        return LANG_DICT.get(self.current_lang, LANG_DICT["tr"]).get(key, key)

    def dil_degistir(self, secim):
        yeni_dil = "tr" if secim == "Türkçe" else "en"
        if self.current_lang != yeni_dil:
            self.current_lang = yeni_dil
            ayar = load_ayar()
            ayar["language"] = yeni_dil
            save_ayar(ayar)
            for widget in self.winfo_children(): widget.destroy()
            self.arayuzu_olustur()
            self.log_yaz("🌍 Dil başarıyla değiştirildi / Language changed successfully.")
            self.log_yaz("🎙️ Ses Motoru Dili / Voice Engine Language: " + ("Türkçe (tr-TR)" if yeni_dil == "tr" else "English (en-US)"))

    def guvenli_ikon_yukle(self):
        try: self.iconbitmap(resource_path("missxss.ico"))
        except Exception: pass

    def yasal_uyari_goster(self):
        self.uyari_penceresi = ctk.CTkToplevel(self)
        self.uyari_penceresi.title(self.T("eula_title"))
        self.uyari_penceresi.geometry("600x300")
        self.uyari_penceresi.resizable(False, False)
        self.uyari_penceresi.attributes("-topmost", True)
        self.uyari_penceresi.protocol("WM_DELETE_WINDOW", self.tamamen_kapat)

        try: self.uyari_penceresi.iconbitmap(resource_path("missxss.ico"))
        except: pass

        ctk.CTkLabel(self.uyari_penceresi, text=self.T("eula_title"), image=self.ikonlar.get("lbl_shield"), compound="left", font=ctk.CTkFont(size=22, weight="bold"), text_color="#ff4757").pack(pady=(20, 10))
        ctk.CTkLabel(self.uyari_penceresi, text=self.T("eula_txt"), font=ctk.CTkFont(size=14)).pack(pady=(10, 20))
        
        def kabul_et():
            ayar = load_ayar()
            ayar["eula_accepted"] = True
            save_ayar(ayar)
            self.uyari_penceresi.destroy()
            self.deiconify() 
            self.after(250, self.guvenli_ikon_yukle)
            self.gif_animasyonunu_baslat() 
            self.kisayollari_uygula()
            if load_ayar().get("oto_baslat", False): self.after(1000, self.ses_gecis_yap)
            
        ctk.CTkButton(self.uyari_penceresi, text=self.T("eula_btn"), font=ctk.CTkFont(size=14, weight="bold"), fg_color="#43B581", hover_color="#3ca374", command=kabul_et, width=240, height=45).pack()

    def tamamen_kapat(self):
        self.destroy()
        sys.exit(0)

    def bosluga_tiklama_kontrolu(self, event):
        try:
            if event.widget.winfo_class() not in ("Entry", "Text", "TCombobox"):
                self.focus_set()
        except: pass

    def gif_animasyonunu_baslat(self):
        try:
            gif_yolu = resource_path("missxss.gif")
            if not os.path.exists(gif_yolu): return
            pil_gif = Image.open(gif_yolu)
            self.gif_kareleri = []
            for kare in ImageSequence.Iterator(pil_gif):
                kare_duzenli = kare.resize((100, 100), Image.Resampling.LANCZOS)
                tk_kare = ctk.CTkImage(light_image=kare_duzenli, dark_image=kare_duzenli, size=(100, 100))
                self.gif_kareleri.append(tk_kare)
            if len(self.gif_kareleri) <= 1: return
            try: self.kare_suresi = pil_gif.info['duration']
            except: self.kare_suresi = 100 
            self.mevcut_kare_index = 0
            self.gif_karelerini_guncelle()
        except Exception: pass

    def gif_karelerini_guncelle(self):
        if self.gif_kareleri:
            kare = self.gif_kareleri[self.mevcut_kare_index]
            self.logo_label.configure(image=kare)
            self.mevcut_kare_index = (self.mevcut_kare_index + 1) % len(self.gif_kareleri)
            self.animasyon_id = self.after(self.kare_suresi, self.gif_karelerini_guncelle)

    def oto_baslat_degisti(self):
        ayar = load_ayar()
        ayar["oto_baslat"] = self.oto_baslat_var_mi.get()
        save_ayar(ayar)

    def basari_sesi_cal(self, is_voice_command=False):
        if self.ses_efekti_var_mi.get(): threading.Thread(target=lambda: winsound.Beep(1200, 150), daemon=True).start()
        if self.sesli_yanit_var_mi.get() and is_voice_command: threading.Thread(target=self._sesli_yanit_motoru, daemon=True).start()

    def _sesli_yanit_motoru(self):
        try:
            ayar_klasoru = os.path.dirname(CONFIG_FILE)
            if self.current_lang == "en":
                metin = "Command confirmed"
                ses_model = "en-US-AriaNeural"
                dosya_adi = "aria_confirmed.mp3"
            else:
                metin = "Komut onaylandı"
                ses_model = "tr-TR-EmelNeural"
                dosya_adi = "emel_onaylandi.mp3"
                
            ses_dosyasi = os.path.join(ayar_klasoru, dosya_adi)
            asyncio.run(self._edge_tts_indir_ve_cal(metin, ses_model, ses_dosyasi))
        except Exception as e: self.log_yaz(f"⚠️ AI Ses Hatası: {e}")

    async def _edge_tts_indir_ve_cal(self, metin, ses, dosya_yolu):
        if not os.path.exists(dosya_yolu):
            try:
                communicate = edge_tts.Communicate(metin, ses)
                await communicate.save(dosya_yolu)
            except Exception: return
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(dosya_yolu)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy(): pygame.time.Clock().tick(10)
        except Exception: pass

    def kisayollari_uygula(self):
        if not keyboard: return
        try: keyboard.unhook_all() 
        except: pass
        for islem_anahtari, atanan_tus in self.kisayollar.items():
            if atanan_tus and self.T("hk_unassigned") not in atanan_tus and islem_anahtari in self.kisayol_tanimlari:
                fonksiyon = self.kisayol_tanimlari[islem_anahtari]["fonksiyon"]
                try: keyboard.add_hotkey(atanan_tus.strip(), fonksiyon, suppress=False)
                except Exception as e: print(f"Kısayol bağlanamadı ({atanan_tus}): {e}")

    def kisayol_penceresi_ac(self):
        if not keyboard:
            self.log_yaz("⚠️ Kısayol sistemi çalışmıyor. 'pip install keyboard' modülü kurulu mu?")
            return
        if self.kisayol_penceresi is not None and self.kisayol_penceresi.winfo_exists():
            self.kisayol_penceresi.focus()
            return
        self.kisayol_penceresi = ctk.CTkToplevel(self)
        self.kisayol_penceresi.title(self.T("hotkey").strip())
        self.kisayol_penceresi.geometry("640x650")
        self.kisayol_penceresi.attributes("-topmost", True) 
        self.kisayol_penceresi.resizable(False, False)
        try: self.kisayol_penceresi.after(200, lambda: self.kisayol_penceresi.iconbitmap(resource_path("missxss.ico")))
        except: pass
        ctk.CTkLabel(self.kisayol_penceresi, text=self.T("hotkey").upper(), image=self.ikonlar.get("lbl_key"), compound="left", font=ctk.CTkFont(size=20, weight="bold"), text_color="#f1c40f").pack(pady=(20, 5))
        ctk.CTkLabel(self.kisayol_penceresi, text=self.T("hk_desc"), text_color="#a0a0a0").pack(pady=(0, 15))
        
        liste_frame = ctk.CTkScrollableFrame(self.kisayol_penceresi, width=560, height=450)
        liste_frame.pack(padx=20, pady=10, fill="both", expand=True)

        for anahtar, veri in self.kisayol_tanimlari.items():
            satir = ctk.CTkFrame(liste_frame, fg_color="transparent")
            satir.pack(fill="x", pady=8)
            ctk.CTkLabel(satir, text=self.T(veri["isim_key"]), font=ctk.CTkFont(size=14, weight="bold"), width=220, anchor="w").pack(side="left")
            mevcut_tus = self.kisayollar.get(anahtar, self.T("hk_unassigned"))
            lbl_durum = ctk.CTkLabel(satir, text=mevcut_tus, font=ctk.CTkFont(size=14, weight="bold"), text_color="#00d2ff" if self.T("hk_unassigned") not in mevcut_tus else "#ff4757", anchor="w")
            lbl_durum.pack(side="left", padx=10, fill="x", expand=True)
            btn_degistir = ctk.CTkButton(satir, text=self.T("hk_set"), width=70, fg_color="#3498db", hover_color="#2980b9", command=lambda k=anahtar, l=lbl_durum: self.tusa_basilmasini_bekle(k, l))
            btn_degistir.pack(side="left", padx=5)
            btn_sil = ctk.CTkButton(satir, text=self.T("hk_del"), width=50, fg_color="#e74c3c", hover_color="#c0392b", command=lambda k=anahtar, l=lbl_durum: self.kisayol_sil(k, l))
            btn_sil.pack(side="left", padx=5)

        ctk.CTkButton(self.kisayol_penceresi, text=self.T("close"), font=ctk.CTkFont(weight="bold"), fg_color="#43B581", hover_color="#3ca374", command=self.kisayol_penceresi.destroy, width=200).pack(pady=(10, 20))

    def tusa_basilmasini_bekle(self, islem_anahtari, label_widget):
        if getattr(self, "bekleyen_kisayol_aktif", False): return
        self.bekleyen_kisayol_aktif = True
        label_widget.configure(text=self.T("hk_press"), text_color="#f1c40f")
        def dinleyici_thread():
            try:
                alinan_tus = keyboard.read_hotkey(suppress=False)
                if label_widget.winfo_exists(): label_widget.configure(text=alinan_tus, text_color="#00d2ff")
                self.kisayollar[islem_anahtari] = alinan_tus
                ayar = load_ayar()
                ayar["kisayollar"] = self.kisayollar
                save_ayar(ayar)
                self.kisayollari_uygula()
            except Exception: pass
            finally: self.bekleyen_kisayol_aktif = False
        threading.Thread(target=dinleyici_thread, daemon=True).start()

    def kisayol_sil(self, islem_anahtari, label_widget):
        if islem_anahtari in self.kisayollar: del self.kisayollar[islem_anahtari]
        if label_widget.winfo_exists(): label_widget.configure(text=self.T("hk_unassigned"), text_color="#ff4757")
        ayar = load_ayar()
        ayar["kisayollar"] = self.kisayollar
        save_ayar(ayar)
        self.kisayollari_uygula()

    def ses_gecis_yap_kisayol(self): self.after(0, self.ses_gecis_yap)
    def hizli_klip_al_kisayol(self): self.after(0, lambda: self.api_istegi_yap(f"{self.T('log_clip')} (30s)", "/v1/clip", {"title": "Kısayol ile alındı", "duration": 30}, is_voice_command=True))
    def kalkan_toggle_kisayol(self):
        mevcut = self.kalkan_durumu.get()
        self.kalkan_durumu.set("on" if mevcut == "off" else "off")
        self.after(0, self.kalkan_tetikle)

    def ozel_komut_penceresi_ac(self):
        if self.ozel_komut_penceresi is not None and self.ozel_komut_penceresi.winfo_exists():
            self.ozel_komut_penceresi.focus()
            return
        self.ozel_komut_penceresi = ctk.CTkToplevel(self)
        self.ozel_komut_penceresi.title(self.T("c_cmd").strip())
        self.ozel_komut_penceresi.geometry("640x550")
        self.ozel_komut_penceresi.attributes("-topmost", True)
        self.ozel_komut_penceresi.resizable(False, False)
        try: self.ozel_komut_penceresi.after(200, lambda: self.ozel_komut_penceresi.iconbitmap(resource_path("missxss.ico")))
        except: pass

        ctk.CTkLabel(self.ozel_komut_penceresi, text=self.T("c_cmd").upper(), image=self.ikonlar.get("lbl_robot"), compound="left", font=ctk.CTkFont(size=20, weight="bold"), text_color="#a29bfe").pack(pady=(20, 5))
        ctk.CTkLabel(self.ozel_komut_penceresi, text=self.T("c_cmd_desc"), text_color="#a0a0a0").pack(pady=(0, 15))

        yeni_frame = ctk.CTkFrame(self.ozel_komut_penceresi)
        yeni_frame.pack(fill="x", padx=20, pady=10)
        self.yeni_komut_entry = ctk.CTkEntry(yeni_frame, placeholder_text=self.T("c_cmd_ph"), width=200)
        self.yeni_komut_entry.pack(side="left", padx=10, pady=10)
        ctk.CTkLabel(yeni_frame, text=" ➡️ ", font=ctk.CTkFont(size=16)).pack(side="left")
        
        disp_vals = [self.T(f"cmd_{k.replace(' ', '_')}") for k in self.gercek_komutlar_keys]
        self.gercek_komut_combo = ctk.CTkOptionMenu(yeni_frame, values=disp_vals, width=180)
        self.gercek_komut_combo.pack(side="left", padx=10, pady=10)
        ctk.CTkButton(yeni_frame, text=self.T("c_cmd_add"), width=70, fg_color="#3498db", hover_color="#2980b9", command=self.ozel_komut_ekle).pack(side="left", padx=10, pady=10)

        self.ozel_liste_frame = ctk.CTkScrollableFrame(self.ozel_komut_penceresi, width=560, height=250)
        self.ozel_liste_frame.pack(padx=20, pady=10, fill="both", expand=True)
        self.ozel_komut_listesini_ciz()

    def ozel_komut_ekle(self):
        soylenen = self.yeni_komut_entry.get().strip().lower()
        secilen_disp = self.gercek_komut_combo.get()
        
        gercek = "klip al" 
        for k in self.gercek_komutlar_keys:
            if self.T(f"cmd_{k.replace(' ', '_')}") == secilen_disp:
                gercek = k
                break
                
        if soylenen:
            ayar = load_ayar()
            ok = ayar.get("ozel_komutlar", {})
            ok[soylenen] = gercek
            ayar["ozel_komutlar"] = ok
            save_ayar(ayar)
            self.yeni_komut_entry.delete(0, "end")
            self.ozel_komut_listesini_ciz()

    def ozel_komut_sil(self, soylenen):
        ayar = load_ayar()
        ok = ayar.get("ozel_komutlar", {})
        if soylenen in ok:
            del ok[soylenen]
            ayar["ozel_komutlar"] = ok
            save_ayar(ayar)
            self.ozel_komut_listesini_ciz()

    def ozel_komut_listesini_ciz(self):
        for widget in self.ozel_liste_frame.winfo_children(): widget.destroy()
        ok = load_ayar().get("ozel_komutlar", {})
        for soylenen, gercek in ok.items():
            satir = ctk.CTkFrame(self.ozel_liste_frame, fg_color="transparent")
            satir.pack(fill="x", pady=5)
            ctk.CTkLabel(satir, text=f'"{soylenen}"', font=ctk.CTkFont(weight="bold", slant="italic"), text_color="#f1c40f", width=200, anchor="w").pack(side="left")
            ctk.CTkLabel(satir, text=self.T("c_cmd_triggers"), width=80).pack(side="left")
            
            gercek_disp = self.T(f"cmd_{gercek.replace(' ', '_')}")
            ctk.CTkLabel(satir, text=f"[{gercek_disp}]", font=ctk.CTkFont(weight="bold"), text_color="#00d2ff", anchor="w").pack(side="left", padx=10, fill="x", expand=True)
            ctk.CTkButton(satir, text=self.T("hk_del"), width=50, fg_color="#e74c3c", hover_color="#c0392b", command=lambda s=soylenen: self.ozel_komut_sil(s)).pack(side="right")

    def kilavuz_penceresi_ac(self):
        if self.kilavuz_penceresi is not None and self.kilavuz_penceresi.winfo_exists():
            self.kilavuz_penceresi.focus()
            return
        self.kilavuz_penceresi = ctk.CTkToplevel(self)
        self.kilavuz_penceresi.title(self.T("guide").strip())
        self.kilavuz_penceresi.geometry("650x550")
        self.kilavuz_penceresi.resizable(False, False)
        self.kilavuz_penceresi.attributes("-topmost", True) 
        try: self.kilavuz_penceresi.after(200, lambda: self.kilavuz_penceresi.iconbitmap(resource_path("missxss.ico")))
        except: pass
        ctk.CTkLabel(self.kilavuz_penceresi, text=self.T("guide"), image=self.ikonlar.get("lbl_mic"), compound="left", font=ctk.CTkFont(size=20, weight="bold"), text_color="#00d2ff").pack(pady=(20, 10))

        kilavuz_metni = self.T("guide_text")
        textbox = ctk.CTkTextbox(self.kilavuz_penceresi, width=600, height=380, font=ctk.CTkFont(size=13), wrap="word")
        textbox.pack(padx=20, pady=10)
        textbox.insert("0.0", kilavuz_metni)
        textbox.configure(state="disabled") 
        ctk.CTkButton(self.kilavuz_penceresi, text=self.T("close"), font=ctk.CTkFont(weight="bold"), fg_color="#43B581", hover_color="#3ca374", command=self.kilavuz_penceresi.destroy, width=200).pack(pady=(5, 20))

    def renk_paleti_ac(self):
        if self.renk_penceresi is not None and self.renk_penceresi.winfo_exists():
            self.renk_penceresi.focus()
            return
        self.renk_penceresi = ctk.CTkToplevel(self)
        self.renk_penceresi.title(self.T("ready_colors"))
        self.renk_penceresi.geometry("300x420")
        self.renk_penceresi.attributes("-topmost", True)
        self.renk_penceresi.resizable(False, False)
        try: self.renk_penceresi.after(200, lambda: self.renk_penceresi.iconbitmap(resource_path("missxss.ico")))
        except: pass
        ctk.CTkLabel(self.renk_penceresi, text=self.T("palette"), image=self.ikonlar.get("palette"), compound="left", font=ctk.CTkFont(size=18, weight="bold"), text_color="#00d2ff").pack(pady=(15, 5))
        
        if self.current_lang == "en":
            renkler = {
                "Kick Green": "#53fc18", "Discord Blue": "#5865F2", "Success (Green)": "#57F287",
                "Error (Red)": "#ED4245", "Warning (Yellow)": "#FEE75C", "Twitch Purple": "#9146FF",
                "AI (Purple)": "#a29bfe", "YouTube Red": "#FF0000", "Turquoise": "#1abc9c",
                "Dark (Black)": "#23272A", "White": "#FFFFFF"
            }
        else:
            renkler = {
                "Kick Yeşili": "#53fc18", "Discord Mavisi": "#5865F2", "Başarı (Yeşil)": "#57F287",
                "Hata (Kırmızı)": "#ED4245", "Uyarı (Sarı)": "#FEE75C", "Twitch Moru": "#9146FF",
                "Yapay Zeka (Mor)": "#a29bfe", "YouTube Kırmızısı": "#FF0000", "Turkuaz": "#1abc9c",
                "Karanlık (Siyah)": "#23272A", "Beyaz": "#FFFFFF"
            }
            
        scroll = ctk.CTkScrollableFrame(self.renk_penceresi, width=250, height=300)
        scroll.pack(padx=10, pady=10, fill="both", expand=True)
        for isim, kod in renkler.items():
            btn_tc = "black" if kod in ["#FFFFFF", "#FEE75C", "#53fc18", "#57F287", "#1abc9c"] else "white"
            btn = ctk.CTkButton(scroll, text=f"{isim}", font=ctk.CTkFont(weight="bold"), fg_color=kod, text_color=btn_tc, hover_color=kod, command=lambda k=kod: self.renk_sec(k))
            btn.pack(pady=5, fill="x", padx=10)
            
    def renk_sec(self, kod):
        self.dc_msg_emb_color.delete(0, "end")
        self.dc_msg_emb_color.insert(0, kod)
        self.save_discord_ids() 
        if self.renk_penceresi and self.renk_penceresi.winfo_exists(): self.renk_penceresi.destroy()

    def arayuzu_olustur(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#18191D")
        self.sidebar_frame.pack(side="left", fill="y")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="")
        self.logo_label.pack(pady=(20, 10))

        self.title_label = ctk.CTkLabel(self.sidebar_frame, text="MISSXSS PANEL", font=ctk.CTkFont(size=22, weight="bold"), text_color="#00d2ff")
        self.title_label.pack(pady=(0, 15))

        self.lang_label = ctk.CTkLabel(self.sidebar_frame, text=self.T("lang_lbl"), image=self.ikonlar.get("globe"), compound="left", font=ctk.CTkFont(size=12, weight="bold"))
        self.lang_label.pack(anchor="w", padx=20, pady=(5, 5))
        self.lang_menu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Türkçe", "English"], command=self.dil_degistir)
        self.lang_menu.set("Türkçe" if self.current_lang == "tr" else "English")
        self.lang_menu.pack(fill="x", padx=20, pady=(0, 15))

        self.api_label = ctk.CTkLabel(self.sidebar_frame, text=self.T("api_key"), image=self.ikonlar.get("lbl_key"), compound="left", font=ctk.CTkFont(size=12, weight="bold"))
        self.api_label.pack(anchor="w", padx=20, pady=(5, 5))
        self.api_entry = ctk.CTkEntry(self.sidebar_frame, show="*", placeholder_text=self.T("api_ph"))
        self.api_entry.insert(0, load_api_key())
        self.api_entry.pack(fill="x", padx=20, pady=(0, 10))
        self.api_btn = ctk.CTkButton(self.sidebar_frame, text=self.T("save"), image=self.ikonlar.get("save"), command=self.api_kaydet, fg_color="#43B581", hover_color="#3ca374")
        self.api_btn.pack(fill="x", padx=20, pady=(0, 15))

        self.mikrofon_label = ctk.CTkLabel(self.sidebar_frame, text=self.T("mic"), image=self.ikonlar.get("lbl_mic"), compound="left", font=ctk.CTkFont(size=12, weight="bold"))
        self.mikrofon_label.pack(anchor="w", padx=20, pady=(0, 5))

        try:
            p = pyaudio.PyAudio()
            temiz_secenekler = []
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                if info.get('maxInputChannels', 0) > 0 and info.get('hostApi') == 0:
                    isim = info.get('name', '')
                    isim_lower = isim.lower()
                    if "mapper" in isim_lower or "microsoft ses" in isim_lower or "fã" in isim_lower: continue
                    temiz_secenekler.append(f"{i}: {isim}")
            p.terminate()
            self.mikrofon_secenekleri = [self.T("def_mic")] + temiz_secenekler
        except Exception:
            self.mikrofon_secenekleri = [self.T("def_mic")]

        self.mikrofon_secici = ctk.CTkOptionMenu(self.sidebar_frame, values=self.mikrofon_secenekleri, width=210)
        self.mikrofon_secici.pack(fill="x", padx=20, pady=(0, 10))

        self.ses_efekti_var_mi = ctk.BooleanVar(value=False) 
        self.ses_efekti_switch = ctk.CTkSwitch(self.sidebar_frame, text=self.T("success_snd"), variable=self.ses_efekti_var_mi, onvalue=True, offvalue=False, font=ctk.CTkFont(size=12, weight="bold"))
        self.ses_efekti_switch.pack(fill="x", padx=20, pady=(0, 5))

        self.sesli_yanit_var_mi = ctk.BooleanVar(value=False) 
        self.sesli_yanit_switch = ctk.CTkSwitch(self.sidebar_frame, text=self.T("voice_conf"), variable=self.sesli_yanit_var_mi, onvalue=True, offvalue=False, font=ctk.CTkFont(size=12, weight="bold"), progress_color="#8e44ad")
        self.sesli_yanit_switch.pack(fill="x", padx=20, pady=(0, 5))

        self.oto_baslat_var_mi = ctk.BooleanVar(value=load_ayar().get("oto_baslat", False))
        self.oto_baslat_switch = ctk.CTkSwitch(self.sidebar_frame, text=self.T("auto_start"), variable=self.oto_baslat_var_mi, onvalue=True, offvalue=False, font=ctk.CTkFont(size=12, weight="bold"), progress_color="#e67e22", command=self.oto_baslat_degisti)
        self.oto_baslat_switch.pack(fill="x", padx=20, pady=(0, 15))

        self.ses_buton = ctk.CTkButton(self.sidebar_frame, text=self.T("ast_open"), image=self.ikonlar.get("mic"), command=self.ses_gecis_yap, font=ctk.CTkFont(size=14, weight="bold"), fg_color="#ff00a0", hover_color="#c8007e", height=45)
        self.ses_buton.pack(fill="x", padx=20, pady=(0, 5))

        self.ozel_komut_btn = ctk.CTkButton(self.sidebar_frame, text=self.T("c_cmd"), image=self.ikonlar.get("gear"), command=self.ozel_komut_penceresi_ac, font=ctk.CTkFont(size=13, weight="bold"), fg_color="#2b2b2b", hover_color="#3d3d3d", height=30)
        self.ozel_komut_btn.pack(fill="x", padx=20, pady=(0, 5))

        self.kilavuz_buton = ctk.CTkButton(self.sidebar_frame, text=self.T("guide"), image=self.ikonlar.get("book"), command=self.kilavuz_penceresi_ac, font=ctk.CTkFont(size=13, weight="bold"), fg_color="#2b2b2b", hover_color="#3d3d3d", height=30)
        self.kilavuz_buton.pack(fill="x", padx=20, pady=(0, 5))

        self.kisayol_buton = ctk.CTkButton(self.sidebar_frame, text=self.T("hotkey"), image=self.ikonlar.get("keyboard"), command=self.kisayol_penceresi_ac, font=ctk.CTkFont(size=13, weight="bold"), fg_color="#2b2b2b", hover_color="#3d3d3d", height=30)
        self.kisayol_buton.pack(fill="x", padx=20, pady=(0, 5))

        # --- YENİ: FEEDBACK BUTONU EKLENDİ ---
        self.feedback_buton = ctk.CTkButton(self.sidebar_frame, text=self.T("feedback"), image=self.ikonlar.get("envelope"), command=self.feedback_penceresi_ac, font=ctk.CTkFont(size=13, weight="bold"), fg_color="#2b2b2b", hover_color="#3d3d3d", height=30)
        self.feedback_buton.pack(fill="x", padx=20, pady=(0, 5))

        self.yapimci_label = ctk.CTkLabel(self.sidebar_frame, text=self.T("prod"), font=ctk.CTkFont(size=13, slant="italic", weight="bold"), text_color="#A0A0A0", cursor="hand2")
        self.yapimci_label.pack(side="bottom", pady=15, padx=20)
        self.yapimci_label.bind("<Enter>", lambda e: self.yapimci_label.configure(text_color="#00d2ff"))
        self.yapimci_label.bind("<Leave>", lambda e: self.yapimci_label.configure(text_color="#A0A0A0"))
        self.yapimci_label.bind("<Button-1>", lambda e: webbrowser.open("https://kick.com/bayrogame"))

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=(0, 20))

        self.tabview = ctk.CTkTabview(self.main_frame, fg_color="transparent")
        self.tabview.pack(fill="both", expand=True, padx=0, pady=(0, 0))

        self.tab_ana = self.tabview.add(self.T("tab_main"))
        self.tab_dc = self.tabview.add(self.T("tab_dc"))
        self.tab_yayin = self.tabview.add(self.T("tab_stream"))

        # ==========================================
        # 1. SEKME: ANA PANEL İÇERİĞİ
        # ==========================================
        self.mesaj_frame = ctk.CTkFrame(self.tab_ana, corner_radius=10)
        self.mesaj_frame.pack(fill="x", pady=(0, 10)) 
        ctk.CTkLabel(self.mesaj_frame, text=self.T("msg_title"), image=self.ikonlar.get("lbl_chat"), compound="left", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 0))
        self.mesaj_inner = ctk.CTkFrame(self.mesaj_frame, fg_color="transparent")
        self.mesaj_inner.pack(fill="x", padx=15, pady=10)
        self.mesaj_tipleri = ctk.CTkOptionMenu(self.mesaj_inner, values=[self.T("pub_msg"), self.T("bot_msg")], width=150)
        self.mesaj_tipleri.pack(side="left", padx=(0, 10))
        self.mesaj_entry = ctk.CTkEntry(self.mesaj_inner, placeholder_text=self.T("msg_ph"))
        self.mesaj_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(self.mesaj_inner, text=self.T("send"), image=self.ikonlar.get("send"), fg_color="#2b2b2b", hover_color="#3d3d3d", width=100, command=self.mesaj_gonder).pack(side="left")

        self.yayin_frame = ctk.CTkFrame(self.tab_ana, corner_radius=10)
        self.yayin_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(self.yayin_frame, text=self.T("stream_info"), image=self.ikonlar.get("lbl_game"), compound="left", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 0))
        self.yayin_inner = ctk.CTkFrame(self.yayin_frame, fg_color="transparent")
        self.yayin_inner.pack(fill="x", padx=15, pady=10)
        self.oyun_entry = ctk.CTkEntry(self.yayin_inner, placeholder_text=self.T("new_cat"), width=220)
        self.oyun_entry.pack(side="left", padx=(0, 10))
        self.baslik_entry = ctk.CTkEntry(self.yayin_inner, placeholder_text=self.T("new_title"))
        self.baslik_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(self.yayin_inner, text=self.T("update"), image=self.ikonlar.get("refresh"), fg_color="#2b2b2b", hover_color="#3d3d3d", width=100, command=self.bilgi_degistir).pack(side="left")

        self.klip_frame = ctk.CTkFrame(self.tab_ana, corner_radius=10)
        self.klip_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(self.klip_frame, text=self.T("clip"), image=self.ikonlar.get("lbl_clip"), compound="left", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 0))
        self.klip_inner = ctk.CTkFrame(self.klip_frame, fg_color="transparent")
        self.klip_inner.pack(fill="x", padx=15, pady=10)
        self.klip_baslik_entry = ctk.CTkEntry(self.klip_inner, placeholder_text=self.T("clip_ph"), width=220)
        self.klip_baslik_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.klip_sure_entry = ctk.CTkEntry(self.klip_inner, placeholder_text=self.T("dur_ph"), width=120)
        self.klip_sure_entry.pack(side="left", padx=(0, 10))
        ctk.CTkButton(self.klip_inner, text=self.T("take_clip"), image=self.ikonlar.get("clip"), fg_color="#8e44ad", hover_color="#9b59b6", width=100, command=self.klip_al).pack(side="left")

        self.muzik_frame = ctk.CTkFrame(self.tab_ana, corner_radius=10)
        self.muzik_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(self.muzik_frame, text=self.T("reji"), image=self.ikonlar.get("lbl_music"), compound="left", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 0))
        self.muzik_inner = ctk.CTkFrame(self.muzik_frame, fg_color="transparent")
        self.muzik_inner.pack(fill="x", padx=15, pady=10)
        ctk.CTkButton(self.muzik_inner, text=self.T("play"), image=self.ikonlar.get("play"), fg_color="#2b2b2b", hover_color="#3d3d3d", command=self.sarki_baslat).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(self.muzik_inner, text=self.T("pause"), image=self.ikonlar.get("pause"), fg_color="#2b2b2b", hover_color="#3d3d3d", command=self.sarki_durdur).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(self.muzik_inner, text=self.T("skip"), image=self.ikonlar.get("skip"), fg_color="#2b2b2b", hover_color="#3d3d3d", command=self.sarki_gec).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(self.muzik_inner, text=self.T("clear_chat"), image=self.ikonlar.get("broom"), fg_color="#2b2b2b", hover_color="#3d3d3d", command=self.sohbeti_temizle).pack(side="left", expand=True, padx=5)

        self.mod_frame = ctk.CTkFrame(self.tab_ana, corner_radius=10, border_width=1, border_color="#ff4757")
        self.mod_frame.pack(fill="x", pady=(0, 10))
        self.mod_top_inner = ctk.CTkFrame(self.mod_frame, fg_color="transparent")
        self.mod_top_inner.pack(fill="x", padx=15, pady=(10, 0))
        ctk.CTkLabel(self.mod_top_inner, text=self.T("mod"), image=self.ikonlar.get("lbl_shield"), compound="left", font=ctk.CTkFont(size=14, weight="bold"), text_color="#ff4757").pack(side="left")
        self.kalkan_durumu = ctk.StringVar(value="off")
        self.kalkan_switch = ctk.CTkSwitch(self.mod_top_inner, text=self.T("shield"), variable=self.kalkan_durumu, onvalue="on", offvalue="off", command=self.kalkan_tetikle, font=ctk.CTkFont(size=12, weight="bold"), button_color="#ffffff", progress_color="#ff4757")
        self.kalkan_switch.pack(side="right")
        self.mod_inner = ctk.CTkFrame(self.mod_frame, fg_color="transparent")
        self.mod_inner.pack(fill="x", padx=15, pady=10)
        self.kullanici_entry = ctk.CTkEntry(self.mod_inner, placeholder_text=self.T("usr_ph"))
        self.kullanici_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(self.mod_inner, text=self.T("ban"), image=self.ikonlar.get("hammer"), fg_color="#ff4757", hover_color="#ff6b81", width=90, command=self.kullanici_banla).pack(side="left", padx=(0, 10))
        ctk.CTkButton(self.mod_inner, text=self.T("timeout"), image=self.ikonlar.get("clock"), fg_color="#ffa502", hover_color="#eccc68", width=100, command=self.kullanici_sustur).pack(side="left", padx=(0, 10))
        ctk.CTkButton(self.mod_inner, text=self.T("unban"), image=self.ikonlar.get("unlock"), fg_color="#43B581", hover_color="#3ca374", width=110, command=self.kullanici_unban).pack(side="left")

        # ==========================================
        # 2. SEKME: DİSCORD KONTROLCÜ
        # ==========================================
        self.dc_top_frame = ctk.CTkFrame(self.tab_dc, fg_color="transparent")
        self.dc_top_frame.pack(fill="x", padx=10, pady=(5, 0))
        ctk.CTkButton(self.dc_top_frame, text=self.T("load_id"), image=self.ikonlar.get("refresh"), font=ctk.CTkFont(weight="bold"), fg_color="#e67e22", hover_color="#d35400", command=self.discord_son_idleri_yukle, width=150).pack(side="right")

        self.dc_status_frame = ctk.CTkFrame(self.tab_dc, corner_radius=10)
        self.dc_status_frame.pack(fill="x", pady=(10, 10), padx=10)
        ctk.CTkLabel(self.dc_status_frame, text=self.T("srv_stat"), image=self.ikonlar.get("lbl_search"), compound="left", font=ctk.CTkFont(size=14, weight="bold"), text_color="#7289da").pack(anchor="w", padx=15, pady=(10, 0))
        self.dc_status_inner = ctk.CTkFrame(self.dc_status_frame, fg_color="transparent")
        self.dc_status_inner.pack(fill="x", padx=15, pady=10)
        self.dc_status_guild = ctk.CTkEntry(self.dc_status_inner, placeholder_text=self.T("srv_ph"), width=200)
        self.dc_status_guild.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(self.dc_status_inner, text=self.T("query"), image=self.ikonlar.get("refresh"), fg_color="#7289da", hover_color="#5b6eae", width=100, command=self.discord_durum_sorgula).pack(side="left")

        self.dc_msg_frame = ctk.CTkFrame(self.tab_dc, corner_radius=10)
        self.dc_msg_frame.pack(fill="x", pady=(0, 10), padx=10)
        ctk.CTkLabel(self.dc_msg_frame, text=self.T("dc_msg"), image=self.ikonlar.get("lbl_chat"), compound="left", font=ctk.CTkFont(size=14, weight="bold"), text_color="#7289da").pack(anchor="w", padx=15, pady=(10, 0))
        self.dc_msg_top = ctk.CTkFrame(self.dc_msg_frame, fg_color="transparent")
        self.dc_msg_top.pack(fill="x", padx=15, pady=(5, 5))
        self.dc_msg_channel = ctk.CTkEntry(self.dc_msg_top, placeholder_text=self.T("ch_ph"), width=150)
        self.dc_msg_channel.pack(side="left", padx=(0, 10))
        self.dc_msg_text = ctk.CTkEntry(self.dc_msg_top, placeholder_text=self.T("n_msg_ph"))
        self.dc_msg_text.pack(side="left", fill="x", expand=True)
        
        self.dc_msg_bottom = ctk.CTkFrame(self.dc_msg_frame, fg_color="transparent")
        self.dc_msg_bottom.pack(fill="x", padx=15, pady=(0, 10))
        self.dc_msg_emb_title = ctk.CTkEntry(self.dc_msg_bottom, placeholder_text=self.T("emb_title"), width=150)
        self.dc_msg_emb_title.pack(side="left", padx=(0, 10))
        self.dc_msg_emb_desc = ctk.CTkEntry(self.dc_msg_bottom, placeholder_text=self.T("emb_desc"))
        self.dc_msg_emb_desc.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.dc_msg_emb_color = ctk.CTkEntry(self.dc_msg_bottom, placeholder_text=self.T("color_ph"), width=110)
        self.dc_msg_emb_color.pack(side="left", padx=(0, 5))
        ctk.CTkButton(self.dc_msg_bottom, text="", image=self.ikonlar.get("palette"), width=30, fg_color="#2b2b2b", hover_color="#3d3d3d", command=self.renk_paleti_ac).pack(side="left", padx=(0, 10))
        ctk.CTkButton(self.dc_msg_bottom, text=self.T("send"), image=self.ikonlar.get("send"), fg_color="#7289da", hover_color="#5b6eae", width=100, command=self.discord_mesaj_gonder).pack(side="left")

        self.dc_mute_all_frame = ctk.CTkFrame(self.tab_dc, corner_radius=10)
        self.dc_mute_all_frame.pack(fill="x", pady=(0, 10), padx=10)
        ctk.CTkLabel(self.dc_mute_all_frame, text=self.T("mute_all_title"), image=self.ikonlar.get("lbl_mega"), compound="left", font=ctk.CTkFont(size=14, weight="bold"), text_color="#ffa502").pack(anchor="w", padx=15, pady=(10, 0))
        self.dc_mute_all_inner = ctk.CTkFrame(self.dc_mute_all_frame, fg_color="transparent")
        self.dc_mute_all_inner.pack(fill="x", padx=15, pady=10)
        self.dc_mute_all_entry = ctk.CTkEntry(self.dc_mute_all_inner, placeholder_text=self.T("vc_ph"))
        self.dc_mute_all_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(self.dc_mute_all_inner, text=self.T("mute_all"), image=self.ikonlar.get("mute_all"), fg_color="#ffa502", hover_color="#eccc68", width=120, command=lambda: self.discord_ses_mute_all("on")).pack(side="left", padx=(0, 10))
        ctk.CTkButton(self.dc_mute_all_inner, text=self.T("unmute_all"), image=self.ikonlar.get("unmute_all"), fg_color="#43B581", hover_color="#3ca374", width=120, command=lambda: self.discord_ses_mute_all("off")).pack(side="left")

        self.dc_pull_all_frame = ctk.CTkFrame(self.tab_dc, corner_radius=10)
        self.dc_pull_all_frame.pack(fill="x", pady=(0, 10), padx=10)
        ctk.CTkLabel(self.dc_pull_all_frame, text=self.T("pull_title"), image=self.ikonlar.get("lbl_magnet"), compound="left", font=ctk.CTkFont(size=14, weight="bold"), text_color="#00d2ff").pack(anchor="w", padx=15, pady=(10, 0))
        self.dc_pull_all_inner = ctk.CTkFrame(self.dc_pull_all_frame, fg_color="transparent")
        self.dc_pull_all_inner.pack(fill="x", padx=15, pady=10)
        self.dc_pull_all_entry = ctk.CTkEntry(self.dc_pull_all_inner, placeholder_text=self.T("pull_ph"))
        self.dc_pull_all_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(self.dc_pull_all_inner, text=self.T("pull_btn"), image=self.ikonlar.get("magnet"), fg_color="#00d2ff", text_color="black", hover_color="#00a8cc", width=130, command=self.discord_ses_pull_all).pack(side="left")

        # ==========================================
        # 3. SEKME: YAYIN KONTROLCÜ 
        # ==========================================
        self.stat_frame = ctk.CTkFrame(self.tab_yayin, corner_radius=10)
        self.stat_frame.pack(fill="x", pady=(10, 10), padx=10)
        
        self.stat_top = ctk.CTkFrame(self.stat_frame, fg_color="transparent")
        self.stat_top.pack(fill="x", padx=15, pady=(10, 0))
        ctk.CTkLabel(self.stat_top, text=self.T("live_stats"), image=self.ikonlar.get("lbl_chart"), compound="left", font=ctk.CTkFont(size=14, weight="bold"), text_color="#e74c3c").pack(side="left")
        
        self.canli_takip_var_mi = ctk.BooleanVar(value=load_ayar().get("canli_takip_acik", False))
        self.canli_takip_switch = ctk.CTkSwitch(self.stat_top, text=self.T("live_track"), variable=self.canli_takip_var_mi, onvalue=True, offvalue=False, font=ctk.CTkFont(size=12, weight="bold"), progress_color="#e74c3c")
        self.canli_takip_switch.pack(side="right")

        self.stat_inner = ctk.CTkFrame(self.stat_frame, fg_color="transparent")
        self.stat_inner.pack(fill="x", padx=15, pady=10)
        
        self.lbl_izleyici = ctk.CTkLabel(self.stat_inner, text=f"{self.T('viewers')} -", font=ctk.CTkFont(size=18, weight="bold"), text_color="#3498db")
        self.lbl_izleyici.pack(side="left", expand=True)
        self.lbl_takipci = ctk.CTkLabel(self.stat_inner, text=f"{self.T('followers')} -", font=ctk.CTkFont(size=18, weight="bold"), text_color="#2ecc71")
        self.lbl_takipci.pack(side="left", expand=True)
        self.lbl_kategori = ctk.CTkLabel(self.stat_inner, text=f"{self.T('category')} -", font=ctk.CTkFont(size=18, weight="bold"), text_color="#9b59b6")
        self.lbl_kategori.pack(side="left", expand=True)

        self.stream_meta_frame = ctk.CTkFrame(self.tab_yayin, corner_radius=10)
        self.stream_meta_frame.pack(fill="x", pady=(0, 10), padx=10)
        ctk.CTkLabel(self.stream_meta_frame, text=self.T("get_meta"), image=self.ikonlar.get("lbl_signal"), compound="left", font=ctk.CTkFont(size=14, weight="bold"), text_color="#00d2ff").pack(anchor="w", padx=15, pady=(10, 0))
        self.stream_meta_inner = ctk.CTkFrame(self.stream_meta_frame, fg_color="transparent")
        self.stream_meta_inner.pack(fill="x", padx=15, pady=10)
        ctk.CTkButton(self.stream_meta_inner, text=self.T("get_meta_btn"), image=self.ikonlar.get("signal"), fg_color="#00d2ff", text_color="black", hover_color="#00a8cc", width=150, command=self.yayin_bilgisi_getir).pack(side="left")

        self.kick_subs_frame = ctk.CTkFrame(self.tab_yayin, corner_radius=10)
        self.kick_subs_frame.pack(fill="x", pady=(0, 10), padx=10)
        ctk.CTkLabel(self.kick_subs_frame, text=self.T("get_subs"), image=self.ikonlar.get("lbl_star"), compound="left", font=ctk.CTkFont(size=14, weight="bold"), text_color="#53fc18").pack(anchor="w", padx=15, pady=(10, 0))
        self.kick_subs_inner = ctk.CTkFrame(self.kick_subs_frame, fg_color="transparent")
        self.kick_subs_inner.pack(fill="x", padx=15, pady=10)
        self.subs_expired_var = ctk.IntVar(value=0)
        self.subs_expired_switch = ctk.CTkSwitch(self.kick_subs_inner, text=self.T("inc_exp"), variable=self.subs_expired_var, onvalue=1, offvalue=0, progress_color="#53fc18")
        self.subs_expired_switch.pack(side="left", padx=(0, 10))
        self.subs_limit_entry = ctk.CTkEntry(self.kick_subs_inner, placeholder_text=self.T("lim_ph"), width=100)
        self.subs_limit_entry.insert(0, "20") 
        self.subs_limit_entry.pack(side="left", padx=(0, 10))
        self.subs_offset_entry = ctk.CTkEntry(self.kick_subs_inner, placeholder_text=self.T("off_ph"), width=100)
        self.subs_offset_entry.insert(0, "0") 
        self.subs_offset_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(self.kick_subs_inner, text=self.T("query"), image=self.ikonlar.get("star"), fg_color="#53fc18", text_color="black", hover_color="#45d113", width=120, command=self.kick_aboneleri_getir).pack(side="left")

        self.recent_activity_frame = ctk.CTkFrame(self.tab_yayin, corner_radius=10)
        self.recent_activity_frame.pack(fill="x", pady=(0, 10), padx=10)
        ctk.CTkLabel(self.recent_activity_frame, text=self.T("get_act"), image=self.ikonlar.get("lbl_bell"), compound="left", font=ctk.CTkFont(size=14, weight="bold"), text_color="#f1c40f").pack(anchor="w", padx=15, pady=(10, 0))
        self.recent_activity_inner = ctk.CTkFrame(self.recent_activity_frame, fg_color="transparent")
        self.recent_activity_inner.pack(fill="x", padx=15, pady=10)
        self.activity_limit_entry = ctk.CTkEntry(self.recent_activity_inner, placeholder_text=self.T("lim_ph"), width=150)
        self.activity_limit_entry.insert(0, "5") 
        self.activity_limit_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(self.recent_activity_inner, text=self.T("query"), image=self.ikonlar.get("refresh"), fg_color="#f1c40f", text_color="black", hover_color="#d4ac0d", width=120, command=self.son_aktiviteleri_getir).pack(side="left")

        self.mod_log_frame = ctk.CTkFrame(self.tab_yayin, corner_radius=10)
        self.mod_log_frame.pack(fill="x", pady=(0, 10), padx=10)
        ctk.CTkLabel(self.mod_log_frame, text=self.T("get_mod"), image=self.ikonlar.get("lbl_shield"), compound="left", font=ctk.CTkFont(size=14, weight="bold"), text_color="#ff4757").pack(anchor="w", padx=15, pady=(10, 0))
        self.mod_log_inner = ctk.CTkFrame(self.mod_log_frame, fg_color="transparent")
        self.mod_log_inner.pack(fill="x", padx=15, pady=10)
        self.mod_log_type_var = ctk.StringVar(value="all")
        self.mod_log_type = ctk.CTkOptionMenu(self.mod_log_inner, values=["all", "ban", "timeout", "shield"], variable=self.mod_log_type_var, width=100)
        self.mod_log_type.pack(side="left", padx=(0, 10))
        self.mod_log_limit_entry = ctk.CTkEntry(self.mod_log_inner, placeholder_text="Limit", width=100)
        self.mod_log_limit_entry.insert(0, "25")
        self.mod_log_limit_entry.pack(side="left", padx=(0, 10))
        self.mod_log_offset_entry = ctk.CTkEntry(self.mod_log_inner, placeholder_text="Offset", width=100)
        self.mod_log_offset_entry.insert(0, "0")
        self.mod_log_offset_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(self.mod_log_inner, text=self.T("query"), image=self.ikonlar.get("refresh"), fg_color="#ff4757", text_color="white", hover_color="#ff6b81", width=120, command=self.moderasyon_kayitlarini_getir).pack(side="left")

        self.ai_bot_frame = ctk.CTkFrame(self.tab_yayin, corner_radius=10)
        self.ai_bot_frame.pack(fill="x", pady=(0, 10), padx=10)
        ctk.CTkLabel(self.ai_bot_frame, text=self.T("ai_title"), image=self.ikonlar.get("lbl_robot"), compound="left", font=ctk.CTkFont(size=14, weight="bold"), text_color="#a29bfe").pack(anchor="w", padx=15, pady=(10, 0))
        self.ai_prompt_inner = ctk.CTkFrame(self.ai_bot_frame, fg_color="transparent")
        self.ai_prompt_inner.pack(fill="x", padx=15, pady=(10, 10))
        self.ai_prompt_combo = ctk.CTkOptionMenu(self.ai_prompt_inner, values=[self.T("loading")], width=250)
        self.ai_prompt_combo.pack(side="left", padx=(0, 10))
        ctk.CTkButton(self.ai_prompt_inner, text=self.T("ai_send"), image=self.ikonlar.get("brain"), fg_color="#a29bfe", text_color="black", hover_color="#8c82fc", width=180, command=self.ai_prompt_guncelle).pack(side="left", padx=(0, 10))
        ctk.CTkButton(self.ai_prompt_inner, text=self.T("ai_clear"), image=self.ikonlar.get("broom"), fg_color="#a29bfe", text_color="black", hover_color="#8c82fc", width=130, command=self.ai_hafiza_temizle).pack(side="left")
        self.after(200, self.prompt_listesini_guncelle)

        # ==========================================
        # LOG EKRANI
        # ==========================================
        ctk.CTkLabel(self.main_frame, text=self.T("sys_log"), image=self.ikonlar.get("lbl_term"), compound="left", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.log_kutusu = ctk.CTkTextbox(self.main_frame, height=160, font=ctk.CTkFont("Consolas", size=12), text_color="#43B581")
        self.log_kutusu.pack(fill="both", expand=True) 
        self.log_kutusu.configure(state="disabled") 

        if not self.api_entry.get(): self.log_yaz(self.T("err_api"))
        else: self.log_yaz(self.T("start_msg"))

    def canli_istatistik_dongusu(self):
        if getattr(self, "canli_takip_var_mi", None) and self.canli_takip_var_mi.get():
            threading.Thread(target=self._sessiz_stat_cek, daemon=True).start()
        self.after(30000, self.canli_istatistik_dongusu)

    def _sessiz_stat_cek(self):
        guncel_api_key = self.api_entry.get().strip()
        if not guncel_api_key: return
        headers = {"Authorization": f"Bearer {guncel_api_key}", "Content-Type": "application/json"}
        try:
            response = requests.post(f"{BASE_URL}/v1/get-stream-meta", headers=headers, json={})
            if response.status_code in [200, 201]:
                veri = response.json()
                
                izleyici = veri.get("viewer_count", veri.get("viewers", "-"))
                takipci = veri.get("followers_count", veri.get("follower_count", veri.get("followers", "-")))
                kategori = veri.get("category", veri.get("game", "-"))
                
                self.after(0, lambda: self.lbl_izleyici.configure(text=f"{self.T('viewers')} {izleyici}"))
                self.after(0, lambda: self.lbl_takipci.configure(text=f"{self.T('followers')} {takipci}"))
                self.after(0, lambda: self.lbl_kategori.configure(text=f"{self.T('category')} {kategori}"))
        except Exception: pass

    def _veriyi_turkcelestir(self, data, indent=0):
        if isinstance(data, list):
            lines = []
            for idx, item in enumerate(data):
                lines.append("  " * indent + f"--- Data {idx+1} ---" if self.current_lang == "en" else f"--- Kayıt {idx+1} ---")
                lines.extend(self._veriyi_turkcelestir(item, indent + 1))
            return lines
            
        elif isinstance(data, dict):
            lines = []
            sozluk = {
                "Id": "ID", "User Id": "Kullanıcı ID", "Username": "Kullanıcı Adı", "Name": "İsim",
                "Slug": "Kanal Adı (Slug)", "Is Live": "Yayında Mı?", "Title": "Yayın Başlığı",
                "Game": "Kategori/Oyun", "Category": "Kategori", "Viewers": "İzleyici Sayısı",
                "Viewer Count": "İzleyici Sayısı", "Followers": "Takipçi Sayısı", 
                "Subscribers": "Abone Sayısı", "Type": "İşlem Tipi", "Reason": "Sebep",
                "Duration": "Süre (sn)", "Moderator": "Moderatör", "Follower": "Takip Eden",
                "Subscriber": "Abone Olan", "Language": "Dil", "Tier": "Abonelik Seviyesi",
                "Months": "Ay (Süre)", "Guild Id": "Sunucu ID", "Channel Id": "Kanal ID",
                "Log Channel Id": "Log Kanalı ID", "Status": "Durum", "Bot Connected": "Bot Bağlantısı",
                "Permissions": "Yetkiler", "Message": "Mesaj", "Action": "Aksiyon", 
                "Target": "Hedef", "Count": "Adet/Sayı", "Amount": "Miktar", "Currency": "Para Birimi",
                "Is Gift": "Hediye Mi?", "Gifter": "Hediye Eden", "Total": "Toplam",
                "Active": "Aktif", "Expired": "Süresi Biten", "Broadcaster": "Yayıncı",
                "Streamer": "Yayıncı", "Role": "Rol", "Created At": "Oluşturulma Tarihi", 
                "Updated At": "Güncelleme Tarihi", "Banned At": "Banlanma Tarihi", 
                "Banned By": "Banlayan", "Avatar": "Profil Fotoğrafı",
                "Banner": "Afiş", "Bio": "Hakkında", "Socials": "Sosyal Medya", "Links": "Linkler",
                "Platform": "Platform"
            }
            for key, value in data.items():
                k_lower = key.lower()
                if k_lower in ["date", "created_at", "updated_at", "timestamp", "time"]: continue
                
                k_duzenli = key.replace("_", " ").title()
                k_gosterim = sozluk.get(k_duzenli, k_duzenli) if self.current_lang == "tr" else k_duzenli
                
                if isinstance(value, str):
                    val_lower = value.lower()
                    if val_lower == "true": value = "Evet" if self.current_lang == "tr" else "True"
                    elif val_lower == "false": value = "Hayır" if self.current_lang == "tr" else "False"
                    elif val_lower == "ban": value = "Ban"
                    elif val_lower == "timeout": value = "Zaman Aşımı (Timeout)" if self.current_lang == "tr" else "Timeout"
                    elif val_lower == "kick": 
                        if k_lower == "platform": value = "Kick"
                        else: value = "Sesten/Yayından Atma (Kick)" if self.current_lang == "tr" else "Kick"
                    elif val_lower == "mute": value = "Susturma" if self.current_lang == "tr" else "Mute"
                elif isinstance(value, bool):
                    if self.current_lang == "tr": value = "Evet" if value else "Hayır"
                    else: value = "True" if value else "False"
                
                if isinstance(value, (dict, list)):
                    lines.append("  " * indent + f"📌 {k_gosterim}:")
                    lines.extend(self._veriyi_turkcelestir(value, indent + 1))
                else: lines.append("  " * indent + f"🔹 {k_gosterim}: {value}")
            return lines
        else: return ["  " * indent + str(data)]

    def sonuclari_pencerede_goster(self, baslik, ham_veri):
        if self.sonuc_penceresi is not None and self.sonuc_penceresi.winfo_exists(): self.sonuc_penceresi.destroy()

        self.sonuc_penceresi = ctk.CTkToplevel(self)
        self.sonuc_penceresi.title(f"{self.T('query_res')}{baslik}")
        self.sonuc_penceresi.geometry("600x500")
        self.sonuc_penceresi.attributes("-topmost", True)
        self.sonuc_penceresi.resizable(False, False) 
        
        try: self.sonuc_penceresi.after(200, lambda: self.sonuc_penceresi.iconbitmap(resource_path("missxss.ico")))
        except: pass

        ctk.CTkLabel(self.sonuc_penceresi, text=f"📊 {baslik}", font=ctk.CTkFont(size=18, weight="bold"), text_color="#00d2ff").pack(pady=(15, 10))

        sonuc_kutusu = ctk.CTkTextbox(self.sonuc_penceresi, width=560, height=380, font=ctk.CTkFont("Consolas", size=13))
        sonuc_kutusu.pack(padx=20, pady=10)
        
        try:
            islenmis_satirlar = self._veriyi_turkcelestir(ham_veri)
            formatli_metin = "\n".join(islenmis_satirlar)
            if not formatli_metin.strip(): formatli_metin = "Data not found / Veri bulunamadı."
        except Exception as e:
            formatli_metin = f"Error formatting data:\n{str(e)}\n\nRaw Data:\n{str(ham_veri)}"

        sonuc_kutusu.insert("0.0", formatli_metin)
        sonuc_kutusu.configure(state="disabled")

        ctk.CTkButton(self.sonuc_penceresi, text=self.T("close"), command=self.sonuc_penceresi.destroy, fg_color="#ff4757", hover_color="#ff6b81", width=120).pack(pady=(5, 10))

    def log_yaz(self, mesaj): self.after(0, self._log_yaz_gorsel, mesaj)
    def _log_yaz_gorsel(self, mesaj):
        self.log_kutusu.configure(state="normal")
        self.log_kutusu.insert("end", mesaj + "\n")
        self.log_kutusu.see("end")
        self.log_kutusu.configure(state="disabled")

    def api_kaydet(self):
        yeni_key = self.api_entry.get().strip()
        if yeni_key: 
            save_api_key(yeni_key)
            self.log_yaz("💾 API Key saved!" if self.current_lang == "en" else "💾 API Anahtarı şifrelenerek gizli konuma kaydedildi!")
            self.basari_sesi_cal(is_voice_command=False) 
        else: self.log_yaz("⚠️ API Key cannot be empty!" if self.current_lang == "en" else "⚠️ API Anahtarı boş olamaz!")

    def api_istegi_yap(self, islem_adi, endpoint, payload=None, is_voice_command=False):
        guncel_api_key = self.api_entry.get().strip()
        if not guncel_api_key: self.log_yaz("❌ Hata: API Key missing!"); return

        headers = {"Authorization": f"Bearer {guncel_api_key}", "Content-Type": "application/json"}
        url = f"{BASE_URL}{endpoint}"
        try:
            req_text = "Request" if self.current_lang == "en" else "İstek"
            self.log_yaz(f"{req_text}: {islem_adi}...")
            response = requests.post(url, headers=headers, json=payload if payload else {})
            if response.status_code in [200, 201]: 
                ozel_sorgular = ["/v1/get-stream-meta", "/v1/get-kick-subscribers", "/v1/get-recent-activity", "/v1/get-moderation-log", "/v1/discord-status"]
                if endpoint in ozel_sorgular and response.text:
                    try:
                        veri = response.json()
                        self.log_yaz("✅ Ok!")
                        self.after(0, lambda: self.sonuclari_pencerede_goster(islem_adi, veri))
                    except: self.log_yaz(f"⚠️ JSON Error")
                else: self.log_yaz(f"✅ Ok!")
                self.basari_sesi_cal(is_voice_command=is_voice_command) 
            else: 
                err_text = response.text
                try:
                    err_json = response.json()
                    if "error" in err_json:
                        err_text = err_json["error"]
                        if self.current_lang == "tr" and "type must be one of" in err_text:
                            err_text = err_text.replace("type must be one of", "Kayıt türü şunlardan biri olmalıdır")
                except: pass
                err_prefix = "Error" if self.current_lang == "en" else "Hata"
                self.log_yaz(f"❌ {err_prefix} ({response.status_code}): {err_text}")
        except Exception as e: 
            err_conn = "Connection Error" if self.current_lang == "en" else "Bağlantı Hatası"
            self.log_yaz(f"⚠️ {err_conn}: {str(e)}")

    def save_discord_ids(self):
        ayar = load_ayar()
        dc_ids = ayar.get("discord_ids", {})
        
        guild_id = self.dc_status_guild.get().strip()
        if guild_id: dc_ids["guild_id"] = guild_id
        msg_channel = self.dc_msg_channel.get().strip()
        if msg_channel: dc_ids["msg_channel"] = msg_channel
        mute_channel = self.dc_mute_all_entry.get().strip()
        if mute_channel: dc_ids["mute_channel"] = mute_channel
        pull_channel = self.dc_pull_all_entry.get().strip()
        if pull_channel: dc_ids["pull_channel"] = pull_channel
        
        ayar["discord_ids"] = dc_ids
        save_ayar(ayar)

    def discord_son_idleri_yukle(self):
        ayar = load_ayar()
        dc_ids = ayar.get("discord_ids", {})
        
        if "guild_id" in dc_ids:
            self.dc_status_guild.delete(0, "end")
            self.dc_status_guild.insert(0, dc_ids["guild_id"])
        if "msg_channel" in dc_ids:
            self.dc_msg_channel.delete(0, "end")
            self.dc_msg_channel.insert(0, dc_ids["msg_channel"])
        if "mute_channel" in dc_ids:
            self.dc_mute_all_entry.delete(0, "end")
            self.dc_mute_all_entry.insert(0, dc_ids["mute_channel"])
        if "pull_channel" in dc_ids:
            self.dc_pull_all_entry.delete(0, "end")
            self.dc_pull_all_entry.insert(0, dc_ids["pull_channel"])
        
        self.log_yaz("✅ Discord IDs loaded." if self.current_lang == "en" else "✅ Son kullanılan Discord ID'leri yüklendi.")

    def discord_durum_sorgula(self):
        guild_id = self.dc_status_guild.get().strip()
        payload = {}
        if guild_id: payload["guild_id"] = guild_id
        self.api_istegi_yap(self.T("srv_stat").strip(), "/v1/discord-status", payload)
        self.save_discord_ids()
        self.focus_set()

    def discord_mesaj_gonder(self):
        channel_id = self.dc_msg_channel.get().strip()
        msg = self.dc_msg_text.get().strip()
        e_title = self.dc_msg_emb_title.get().strip()
        e_desc = self.dc_msg_emb_desc.get().strip()
        e_color = self.dc_msg_emb_color.get().strip()
        if not channel_id:
            self.log_yaz("⚠️ Channel ID is required!" if self.current_lang == "en" else "⚠️ Kanal ID zorunludur!")
            return
        payload = {"channel_id": channel_id}
        if msg: payload["message"] = msg
        if e_title: payload["embed_title"] = e_title
        if e_desc: payload["embed_description"] = e_desc
        if e_color: payload["embed_color"] = e_color
        self.api_istegi_yap(f"{self.T('log_discord_msg')} -> {channel_id}", "/v1/discord-send-message", payload)
        self.save_discord_ids()
        self.dc_msg_text.delete(0, "end") 
        self.dc_msg_emb_title.delete(0, "end") 
        self.dc_msg_emb_desc.delete(0, "end") 
        self.focus_set()

    def discord_ses_mute_all(self, mode):
        channel_id = self.dc_mute_all_entry.get().strip()
        if not channel_id:
            self.log_yaz("⚠️ Target Voice Channel ID is required!" if self.current_lang == "en" else "⚠️ Hedef Ses Kanalı ID'si boş olamaz!")
            return
        islem_adi = f"{self.T('log_discord_mute')} ({channel_id})" if mode == "on" else f"{self.T('log_discord_unmute')} ({channel_id})"
        endpoint = "/v1/discord-voice-mute-all" if mode == "on" else "/v1/discord-voice-unmute-all"
        self.api_istegi_yap(islem_adi, endpoint, {"channel_id": channel_id})
        self.save_discord_ids()
        self.focus_set()

    def discord_ses_pull_all(self):
        target_channel_id = self.dc_pull_all_entry.get().strip()
        if not target_channel_id:
            self.log_yaz("⚠️ Target Channel ID is required!" if self.current_lang == "en" else "⚠️ Hedef Ses Kanalı ID'si boş olamaz!")
            return
        self.api_istegi_yap(f"{self.T('log_discord_pull')} ({target_channel_id})", "/v1/discord-voice-pull-all", {"target_channel_id": target_channel_id})
        self.save_discord_ids()
        self.focus_set()

    def yayin_bilgisi_getir(self):
        self.api_istegi_yap(self.T("get_meta_btn").strip(), "/v1/get-stream-meta", payload=None)
        self.focus_set()

    def kick_aboneleri_getir(self):
        include_expired = self.subs_expired_var.get()
        limit_str = self.subs_limit_entry.get().strip()
        offset_str = self.subs_offset_entry.get().strip()
        try:
            limit = int(limit_str) if limit_str else 20
            offset = int(offset_str) if offset_str else 0
        except ValueError:
            self.log_yaz("⚠️ Limit & Offset must be numbers!" if self.current_lang == "en" else "⚠️ Limit ve Offset rakam olmalıdır!")
            return
        payload = {"include_expired": include_expired, "limit": limit, "offset": offset}
        self.api_istegi_yap(f"{self.T('get_subs').strip()} (L:{limit}, O:{offset})", "/v1/get-kick-subscribers", payload)
        self.focus_set()

    def son_aktiviteleri_getir(self):
        limit_str = self.activity_limit_entry.get().strip()
        try: limit = int(limit_str) if limit_str else 5
        except ValueError:
            self.log_yaz("⚠️ Limit must be a number!" if self.current_lang == "en" else "⚠️ Limit rakam olmalıdır!")
            return
        self.api_istegi_yap(f"{self.T('get_act').strip()} (L: {limit})", "/v1/get-recent-activity", {"limit": limit})
        self.focus_set()

    def moderasyon_kayitlarini_getir(self):
        log_type = self.mod_log_type_var.get()
        limit_str = self.mod_log_limit_entry.get().strip()
        offset_str = self.mod_log_offset_entry.get().strip()
        try:
            limit = int(limit_str) if limit_str else 25
            offset = int(offset_str) if offset_str else 0
        except ValueError:
            self.log_yaz("⚠️ Limit & Offset must be numbers!" if self.current_lang == "en" else "⚠️ Limit ve Offset rakam olmalıdır!")
            return
        payload = {"type": log_type, "limit": limit, "offset": offset}
        self.api_istegi_yap(f"{self.T('get_mod').strip()} ({log_type})", "/v1/get-moderation-log", payload)
        self.focus_set()

    def prompt_listesini_guncelle(self):
        klasor = self.prompts_klasoru_en if self.current_lang == "en" else self.prompts_klasoru_tr
        try:
            if not os.path.exists(klasor):
                self.ai_prompt_combo.configure(values=[self.T("no_prompt")])
                self.ai_prompt_combo.set(self.T("no_prompt"))
                return
            dosyalar = [f for f in os.listdir(klasor) if f.endswith(".txt")]
            if not dosyalar:
                self.ai_prompt_combo.configure(values=[self.T("no_prompt")])
                self.ai_prompt_combo.set(self.T("no_prompt"))
            else:
                gosterilecek_isimler = [f.replace(".txt", "") for f in dosyalar]
                self.ai_prompt_combo.configure(values=gosterilecek_isimler)
                self.ai_prompt_combo.set(gosterilecek_isimler[0])
        except Exception as e: self.log_yaz(f"⚠️ Prompt error: {e}")

    def ai_prompt_guncelle(self):
        secilen_isim = self.ai_prompt_combo.get()
        if secilen_isim in [self.T("no_prompt"), self.T("loading")]:
            self.log_yaz("⚠️ No valid prompt selected!" if self.current_lang == "en" else "⚠️ Geçerli bir prompt seçilmedi!")
            return
        
        klasor = self.prompts_klasoru_en if self.current_lang == "en" else self.prompts_klasoru_tr
        dosya_yolu = os.path.join(klasor, secilen_isim + ".txt")
        try:
            with open(dosya_yolu, "r", encoding="utf-8") as f: prompt_metni = f.read().strip()
            if not prompt_metni:
                self.log_yaz(f"⚠️ Error: Prompt file is empty!" if self.current_lang == "en" else f"⚠️ Hata: Prompt dosyası boş!")
                return
            self.api_istegi_yap(f"{self.T('log_ai_char')} ({secilen_isim})", "/v1/ai-bot", {"ai_text": prompt_metni})
            self.focus_set()
        except Exception as e: self.log_yaz(f"⚠️ File error: {e}")

    def ai_hafiza_temizle(self):
        self.api_istegi_yap(self.T("log_ai_clear"), "/v1/clear-ai", payload=None)
        self.focus_set()

    def kalkan_tetikle(self):
        secili_mod = self.kalkan_durumu.get() 
        islem_adi = self.T("log_shield_on") if secili_mod == "on" else self.T("log_shield_off")
        self.api_istegi_yap(islem_adi, "/v1/shield-mode", {"mode": secili_mod})
        self.focus_set()

    def mesaj_gonder(self):
        mesaj = self.mesaj_entry.get().strip()
        if mesaj: 
            ep = "/v1/send-bot-message" if self.mesaj_tipleri.get() in ["Bot Mesajı", "Bot Msg"] else "/v1/send-message"
            self.api_istegi_yap(self.T("log_msg_sent"), ep, {"message": mesaj})
            self.mesaj_entry.delete(0, "end") 
            self.focus_set() 

    def bilgi_degistir(self):
        oyun = self.oyun_entry.get().strip().lower()
        baslik = self.baslik_entry.get().strip()
        if oyun: 
            tam_isim = OYUN_KISALTMALARI.get(oyun, oyun.title())
            self.api_istegi_yap(f"{self.T('log_cat_upd')} -> {tam_isim}", "/v1/game", {"game": tam_isim})
            self.oyun_entry.delete(0, "end")
        if baslik: 
            self.api_istegi_yap(self.T("log_title_upd"), "/v1/title", {"title": baslik})
            self.baslik_entry.delete(0, "end")
        self.focus_set() 

    def klip_al(self):
        baslik = self.klip_baslik_entry.get().strip()
        sure_str = self.klip_sure_entry.get().strip()
        if not baslik: baslik = "Awesome moment!" if self.current_lang == "en" else "Harika bir an!"
        sure = 30 
        if sure_str.isdigit():
            sure = int(sure_str)
            if sure < 5: sure = 5
            elif sure > 180: sure = 180
        self.api_istegi_yap(f"{self.T('log_clip')} ({sure}s)", "/v1/clip", {"title": baslik, "duration": sure})
        self.klip_baslik_entry.delete(0, "end")
        self.klip_sure_entry.delete(0, "end")
        self.focus_set()

    def sohbeti_temizle(self): self.api_istegi_yap(self.T("log_clear"), "/v1/clear-chat")
    def sarki_baslat(self): self.api_istegi_yap(self.T("log_play"), "/v1/start-song")
    def sarki_durdur(self): self.api_istegi_yap(self.T("log_stop"), "/v1/stop-song")
    def sarki_gec(self): self.api_istegi_yap(self.T("log_skip"), "/v1/skip-song")

    def kullanici_banla(self):
        kullanici = self.kullanici_entry.get().strip()
        if not kullanici: return
        self.api_istegi_yap(f"{self.T('log_ban')} {kullanici}", "/v1/ban", {"username": kullanici, "reason": "Panel"})
        self.kullanici_entry.delete(0, "end")
        self.focus_set()

    def kullanici_sustur(self):
        kullanici = self.kullanici_entry.get().strip()
        if not kullanici: return
        self.api_istegi_yap(f"{self.T('log_timeout')} {kullanici}", "/v1/timeout", {"username": kullanici, "duration": 5, "reason": "Panel"})
        self.kullanici_entry.delete(0, "end")
        self.focus_set()

    def kullanici_unban(self):
        kullanici = self.kullanici_entry.get().strip()
        if not kullanici: return
        self.api_istegi_yap(f"{self.T('log_unban')} {kullanici}", "/v1/unban-user", {"username": kullanici})
        self.kullanici_entry.delete(0, "end")
        self.focus_set()

    def ses_gecis_yap(self):
        if not self.dinleme_aktif:
            self.dinleme_aktif = True
            self.ses_buton.configure(text=self.T("ast_close"), fg_color="#ff4757", hover_color="#ff6b81", image=self.ikonlar.get("mic_off"))
            self.log_yaz("🎤 Mic is ON. Trigger: 'Miss'" if self.current_lang == "en" else "🎤 Mikrofon açık. Tetikleyici: 'Miss'")
            self.ses_thread = threading.Thread(target=self.ses_dinle_dongusu, daemon=True)
            self.ses_thread.start()
        else:
            self.dinleme_aktif = False
            self.ses_buton.configure(text=self.T("ast_open"), fg_color="#ff00a0", hover_color="#c8007e", image=self.ikonlar.get("mic"))
            self.log_yaz("🛑 Voice Assistant closed." if self.current_lang == "en" else "🛑 Sesli Asistan kapalı.")

    def ses_dinle_dongusu(self):
        secili_mikrofon = self.mikrofon_secici.get()
        dev_idx = None
        if secili_mikrofon != self.T("def_mic"):
            try: dev_idx = int(secili_mikrofon.split(":")[0])
            except: pass
        r = sr.Recognizer()
        r.energy_threshold = 150; r.dynamic_energy_threshold = True; r.pause_threshold = 1.2; r.phrase_threshold = 0.3 
        try:
            with sr.Microphone(device_index=dev_idx) as source:
                r.adjust_for_ambient_noise(source, duration=2.0) 
                while self.dinleme_aktif:
                    try:
                        audio = r.listen(source, timeout=1, phrase_time_limit=6)
                        lang_code = "en-US" if self.current_lang == "en" else "tr-TR"
                        soylenen = r.recognize_google(audio, language=lang_code).lower()
                        self.sesli_komutu_isle(soylenen)
                    except sr.RequestError as e:
                        if "Not Found" in str(e) or "404" in str(e): pass
                        else:
                            if self.dinleme_aktif: self.log_yaz(f"⚠️ Google API Error: {e}")
                    except (sr.WaitTimeoutError, sr.UnknownValueError): continue
                    except Exception as e:
                        if self.dinleme_aktif: self.log_yaz(f"⚠️ System Error: {e}")
        except Exception as e:
            self.log_yaz(f"⚠️ Mic Error: {e}")
            self.after(0, self.ses_gecis_yap) 

    def sesli_komutu_isle(self, soylenen):
        tetikleyiciler = ["miss", "mis", "mış", "miş"]
        tetiklendi = False; kullanilan_tetikleyici = ""
        for t in tetikleyiciler:
            if soylenen.startswith(t): tetiklendi = True; kullanilan_tetikleyici = t; break
        if not tetiklendi: return 
        
        self.log_yaz(f"🗣️ Voice Command: '{soylenen}'" if self.current_lang == "en" else f"🗣️ Asistan Uyandı: '{soylenen}'")
        asil_komut = soylenen.replace(kullanilan_tetikleyici, "", 1).strip()
        
        ayar = load_ayar()
        ozel_komutlar = ayar.get("ozel_komutlar", {})
        if asil_komut in ozel_komutlar:
            self.log_yaz(f"🔄 Custom Command: '{asil_komut}' -> '{ozel_komutlar[asil_komut]}'")
            asil_komut = ozel_komutlar[asil_komut]

        if any(k in asil_komut for k in ["herkesi sustur", "toplu sustur", "odadaki herkesi sustur", "mute all", "mute everyone"]):
            self.after(0, lambda: self.discord_ses_mute_all("on"))
            return
        elif any(k in asil_komut for k in ["herkesin sesini aç", "sesleri aç", "susturmayı kaldır", "unmute all", "unmute everyone"]):
            self.after(0, lambda: self.discord_ses_mute_all("off"))
            return
        elif any(k in asil_komut for k in ["herkesi bu kanala çek", "herkesi çek", "toplu çek", "odaya çek", "pull everyone", "pull all"]):
            self.after(0, self.discord_ses_pull_all)
            return
            
        moderasyon_kelimeleri = ["ban", "sustur", "uçur", "timeout", "kick", "mute user"]
        for mod_kelime in moderasyon_kelimeleri:
            if mod_kelime in asil_komut:
                self.log_yaz(f"⚠️ Warning: Ban/Timeout disabled for voice.")
                return

        eslesen_anahtar = None; komut_verisi = None
        for anahtar, veri in KOMUT_HARITASI.items():
            if asil_komut.startswith(anahtar): eslesen_anahtar = anahtar; komut_verisi = veri; break
            
        if not eslesen_anahtar:
            for anahtar, veri in KOMUT_HARITASI.items():
                karsilastirma_kismi = asil_komut[:len(anahtar)]
                benzerlik = difflib.SequenceMatcher(None, karsilastirma_kismi, anahtar).ratio()
                if benzerlik >= 0.75: 
                    eslesen_anahtar = anahtar; komut_verisi = veri
                    self.log_yaz(f"🧠 Fuzzy Match: '{karsilastirma_kismi}' -> '{anahtar}'")
                    break
        
        if eslesen_anahtar and komut_verisi:
            payload = komut_verisi["payload"].copy() if komut_verisi.get("payload") is not None else {}
            if komut_verisi["endpoint"] == "/v1/shield-mode": self.kalkan_durumu.set(payload["mode"])
            if "dinamik" in komut_verisi:
                silinecek_kisim = asil_komut[:len(eslesen_anahtar)]
                iletilecek_metin = asil_komut.replace(silinecek_kisim, "", 1).strip()
                if iletilecek_metin:
                    param_adi = komut_verisi["dinamik"]
                    if param_adi == "game": iletilecek_metin = OYUN_KISALTMALARI.get(iletilecek_metin, iletilecek_metin.title())
                    if param_adi == "username": iletilecek_metin = iletilecek_metin.replace(" ", "")
                    payload[param_adi] = iletilecek_metin
            self.api_istegi_yap(f"🎙️ Voice: {eslesen_anahtar}", komut_verisi["endpoint"], payload, is_voice_command=True)
        else: self.log_yaz(f"⚠️ Not Understood: {asil_komut}" if self.current_lang == "en" else f"⚠️ Komut anlaşılamadı: {asil_komut}")

if __name__ == "__main__":
    app = MissxssPanel()
    app.mainloop()