<div align="center">
  <h1>🎙️ Missxss Sesli Kontrol Paneli v2.1</h1>
  <h2>🎙️ Missxss Voice Control Panel v2.1</h2>
  <p><b>Yapay Zeka Destekli Sesli Yayın ve Discord Yönetim Paneli</b></p>
  <p><i>AI-Powered Voice-Controlled Stream and Discord Management Panel</i></p>
</div>

---

## 🌟 Hakkında / About

**🇹🇷 Türkçe:**
Sadece sesinizi kullanarak yayın hayatınızı ve topluluğunuzu yönetmeye hazır mısınız? Missxss Sesli Panel; arka planda oyununuzu oynarken sadece "Miss..." diyerek yayın kategorinizi değiştirebileceğiniz, anında klip alabileceğiniz, Discord odalarını tek kelimeyle susturup yönetebileceğiniz ve yapay zeka entegrasyonuyla sohbeti canlı tutabileceğiniz hepsi bir arada bir otomasyon aracıdır.

**EN English:**
Are you ready to manage your stream and community using only your voice? Missxss Voice Control Panel is an all-in-one automation tool that allows you to change your stream category, take instant clips, manage Discord voice channels, and keep the chat alive with AI integration—all while gaming in the background, just by saying "Miss..."

---

## ✨ Özellikler / Features

* 🗣️ **Sesli Asistan (Voice Assistant):** Sadece konuşarak tüm paneli yönetin (Türkçe ve İngilizce komut algılama).
  *(Manage the entire panel just by speaking. Supports Turkish and English commands.)*

* 🎮 **Yayın Kontrolü (Stream Control):** Yayın başlığı güncelleme, kategori değiştirme, anlık klip alma ve canlı istatistik takibi.
  *(Update stream title, change category, take instant clips, and track live statistics.)*

* 📢 **Discord Entegrasyonu (Discord Integration):** Kanallara özel mesaj gönderme, odadaki herkesi tek komutla susturma/seslerini açma veya herkesi kendi odanıza çekme.
  *(Send custom messages to channels, mute/unmute everyone with a single command, or pull everyone to your voice channel.)*

* 🤖 **Yapay Zeka (AI Chatbot):** Kendi yazdığınız promptlar ile yayınlarınıza entegre çalışan akıllı yapay zeka botu.
  *(A smart AI bot integrated into your streams using your own custom prompts.)*

* 🔄 **Oto-Güncelleme (Auto-Updater):** Yeni bir sürüm yayınlandığında program arka planda kendi kendini sessizce günceller.
  *(The program silently updates itself in the background when a new version is released.)*

* 🛡️ **Üst Düzey Güvenlik (High Security):** API anahtarlarınız cihazınıza özel AES şifreleme (Local Fernet Encryption) ile korunur.
  *(Your API keys are protected with device-specific AES encryption via Local Fernet Encryption.)*

* 📬 **Geri Bildirim (Feedback):** Program içinden doğrudan geliştiriciye Discord üzerinden anlık geri bildirim gönderme sistemi.
  *(A built-in system to send instant feedback directly to the developer via Discord.)*
---

## 🚀 Kurulum / Installation

### 🎮 Normal Kullanıcılar İçin (For Regular Users)

Kodu derlemekle uğraşmak istemiyorsanız, hazır `.exe` dosyasını indirip hemen kullanmaya başlayabilirsiniz:
*(If you don't want to compile the code, you can download the ready-to-use `.exe` file:)*

1. Sağ taraftaki **[Releases](https://github.com/Bayrogame/Missxss-Panel/releases)** bölümüne tıklayın. 
*(Click on the **Releases** section on the right side.)*

2. En son sürümdeki `Gelismis.Missxss.Panel.exe` dosyasını indirin. 
*(Download the `Gelismis.Missxss.Panel.exe` file from the latest release.)*

3. Çalıştırın ve keyfini çıkarın! (Program gerekli güvenlik anahtarlarını cihazınıza özel olarak otomatik üretecektir). 
*(Run it and enjoy! The program will automatically generate the required security keys specifically for your device upon first launch.)*

4. **⬇️ Tek Tıkla Direkt İndirme (.EXE Olarak):** [📥 Gelismis.Missxss.Panel.exe (En Güncel Sürümü İndir)](https://github.com/Bayrogame/Missxss-Panel/releases/latest/download/Gelismis.Missxss.Panel.exe)  
*(Click the link above to directly download the latest .exe file without navigating through GitHub.)*

### 💻 Geliştiriciler İçin (For Developers)

Projeyi bilgisayarınızda açık kaynak olarak derlemek ve geliştirmek isterseniz:
*If you want to run, compile, and develop this project open-source on your local machine:*

**1. Projeyi klonlayın / Clone the repository:**
```bash
git clone [https://github.com/Bayrogame/Missxss-Panel.git](https://github.com/Bayrogame/Missxss-Panel.git)
```
**2. Kütüphaneleri kurun / Install requirements:**
```bash
pip install -r requirements.txt
```
**3. Güvenlik ayarları / Security setup:**
Proje klasöründeki .env.example dosyasının adını .env olarak değiştirin. (Rename the .env.example file to .env in the project folder.)

(Opsiyonel) Kendi Discord Webhook URL'nizi geri bildirim sistemi için .env dosyasına ekleyebilirsiniz. (Optional: You can add your own Discord Webhook URL to the .env file for the feedback system.)

**4. Programı başlatın / Run the app:**
```bash
python seslimissxss.py
```
## 🔑 API Key Nasıl Alınır? / How to Get an API Key?

Programın çalışması ve hesabınıza bağlanabilmesi için Missxss üzerinden bir API anahtarı almanız gerekmektedir.
*(To allow the program to work and connect to your account, you need to get an API key from Missxss.)*

1. [www.missxss.com.tr](https://www.missxss.com.tr/) adresine giderek hesabınıza giriş yapın. 
*(Go to www.missxss.com.tr and log in to your account.)*

2. Menüden **"Bilgi & Raporlar"** sekmesine tıklayın. 
*(Click on the **"Bilgi & Raporlar"** / Info & Reports tab from the menu.)*

3. Açılan listeden **"API Erişim"** bölümüne girin. 
*(Navigate to the **"API Erişim"** / API Access section.)*

4. Buradan kendinize özel API anahtarınızı (API Key) kopyalayın ve programı açtığınızda soldaki menüye yapıştırıp kaydedin. 
*(Copy your unique API Key from there, paste it into the left menu when you open the program, and save it.)*

---

🐛 İletişim & Destek / Contact & Support
Programda herhangi bir hata bulursanız veya yeni bir özellik öneriniz varsa, program içindeki "Geri Bildirim" butonunu kullanabilir veya doğrudan bana ulaşabilirsiniz.
If you encounter any bugs or have feature suggestions, feel free to use the in-app "Feedback" button or contact me directly.

📺 Kick: kick.com/bayrogame

🐙 GitHub: Bayrogame

Code with passion, stream with vision. Developed by Bayrogame.
