# 🎙️ Missxss Gelişmiş Panel v2.1

Yapay zeka destekli, sesli komutlarla çalışan gelişmiş yayın ve Discord yönetim paneli. Sadece "Miss" diyerek yayın kategorinizi değiştirebilir, klip alabilir, Discord odalarını yönetebilir ve yapay zeka botunuzu kontrol edebilirsiniz.

An advanced, voice-controlled stream and Discord management panel powered by AI. Just say "Miss" to change stream categories, take clips, manage Discord rooms, and control your AI bot.

---

## ✨ Özellikler / Features
* 🗣️ **Sesli Asistan (Voice Assistant):** Sadece konuşarak tüm paneli yönetin (Türkçe ve İngilizce algılama).
* 🎮 **Yayın Kontrolü (Stream Control):** Yayın başlığı, kategori değiştirme, anlık klip alma ve canlı istatistik takibi.
* 📢 **Discord Entegrasyonu (Discord Integration):** Kanala mesaj gönderme, odadaki herkesi tek tuşla/sesle susturma veya odaya çekme.
* 🤖 **Yapay Zeka (AI Chatbot):** Yayınlarınıza entegre çalışan yapay zeka botu için prompt yönetimi.
* 🔄 **Oto-Güncelleme (Auto-Updater):** Yeni bir sürüm çıktığında program kendi kendini arka planda sessizce günceller.
* 🛡️ **Üst Düzey Güvenlik (High Security):** API anahtarlarınız cihazınıza özel olarak şifrelenir (Local Fernet Encryption).
* 📬 **Geri Bildirim (Feedback):** Program içinden doğrudan geliştiriciye Discord üzerinden geri bildirim gönderme sistemi.

---

## 📥 Kullanıcılar İçin Kurulum (For Regular Users)
Kodu derlemekle uğraşmak istemiyorsanız, doğrudan `.exe` dosyasını indirip kullanmaya başlayabilirsiniz:
If you don't want to deal with code, you can download the compiled `.exe` file directly:

1. Sağ taraftaki **[Releases](https://github.com/Bayrogame/Missxss-Panel/releases)** bölümüne tıklayın.
2. En son sürümdeki `Gelişmiş Missxss Panel.exe` dosyasını indirin.
3. Çalıştırın ve keyfini çıkarın! (Program gerekli güvenlik anahtarlarını sizin için ilk açılışta otomatik oluşturacaktır).

---

## 🛠️ Geliştiriciler İçin Kurulum (For Developers)
Bu projeyi kendi bilgisayarınızda açık kaynak olarak derlemek ve geliştirmek isterseniz:
If you want to run and develop this project open-source on your local machine:

1. Projeyi bilgisayarınıza klonlayın / Clone the repository:
   ```bash
   git clone [https://github.com/Bayrogame/Missxss-Panel.git](https://github.com/Bayrogame/Missxss-Panel.git)

2. Gerekli kütüphaneleri kurun / Install requirements:
   ```bash
   pip install -r requirements.txt

3. Güvenlik ayarlarını yapın / Security setup:
Proje klasöründeki .env.example dosyasının adını .env olarak değiştirin.
Opsiyonel: Kendi Discord Webhook URL'nizi geri bildirim sistemi için ekleyebilirsiniz.

4.Programı başlatın / Run the app:
 ```bash
 python seslimissxss.py
