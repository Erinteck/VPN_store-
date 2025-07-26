# VPN_store Telegram Bot 🤖🔒

Welcome to **VPN_store** — a Telegram bot designed to automate subscription management and delivery of VPN access through QR codes.  
Built with [Telethon](https://github.com/LonamiWebs/Telethon), SQLite, and Python asyncio for smooth and efficient user experience.

---

## 🚀 Features

- **User Subscription Purchase Flow**  
  Users enter their info, send payment receipts, and receive VPN access QR codes automatically after admin approval.

- **Admin Panel**  
  Admins can approve or reject payments, upload VPN QR codes in bulk, and monitor subscriptions easily.

- **Support Chat System**  
  Real-time chat between users and support staff with support for text and images — fully integrated in Telegram.

- **Subscription Expiration Reminder**  
  Automatically notifies users 5 days before their subscription expires to encourage renewals.

- **Download VPN Client Links**  
  Quick access to official WireGuard apps for Android and iOS via inline buttons.

---

## ⚙️ How It Works

1. User starts the bot with `/start` command.  
2. User chooses to buy a subscription or download the VPN app.  
3. When buying, user submits family info + last 4 digits of their phone.  
4. User transfers money and uploads payment receipt as photo.  
5. Admin reviews and confirms or rejects the payment.  
6. Upon confirmation, a unique VPN QR code image is sent to the user.  
7. The bot tracks subscription time and reminds the user before expiration.  
8. Support chat available for user-admin communication with photo and text messages.

---

## 📂 Project Structure

- **bot.py** - Main bot script with event handlers and business logic  
- **config.py** - Bot configuration variables (API keys, tokens, admin IDs)  
- **database.py** - SQLAlchemy ORM models and DB session setup  
- **receipts/** - Folder to store payment receipt images  
- **qrcodes/** - Folder containing VPN QR code images  

---

## 🔧 Requirements

- Python 3.8+  
- [Telethon](https://pypi.org/project/telethon/)  
- SQLAlchemy  
- SQLite (default DB)

---

## 🛠 Installation & Usage

1. Clone the repository:  
   ```bash
   git clone https://github.com/matinebadi/VPN_store.git
   cd VPN_store
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Configure your config.py with your Telegram API credentials and bot token.

Run the bot:

bash
Copy
Edit
python bot.py
📩 Support
If you have questions or want to contribute, feel free to open an issue or pull request.

🧑‍💻 Developer
This project is developed and maintained by Matin Ebadi.
Thank you for checking out the project!
