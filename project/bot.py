import os
import shutil
from telethon import TelegramClient, events, Button
from config import api_id, api_hash, bot_token, admin_ids
from database import session, Payment, QRCode
import asyncio
from datetime import datetime, timedelta

if not os.path.exists("receipts"):
    os.mkdir("receipts")
if not os.path.exists("qrcodes"):
    os.mkdir("qrcodes")

bot = TelegramClient("bot_session", api_id, api_hash).start(bot_token=bot_token)
user_states = {}

barcode_upload_count = 0  # شمارنده بارکدها

# دکمه‌های کارت (اینلاین)
card_buttons = [
    Button.inline("💳 کارت 6393", b"copy_card1"),
    Button.inline("💳 کارت 5859", b"copy_card2"),
]

# دکمه‌های اصلی اینلاین بدون پشتیبان
main_inline_buttons = [
    [Button.inline("💳 خرید اشتراک", b"buy")],
    [Button.inline("📲 دانلود اپ", b"download_app")],
]

# دکمه پشتیبان به صورت Button.text (غیر اینلاین)
support_button = [Button.text("🛠 پشتیبان", resize=True)]

# دکمه‌های دانلود اپ (اینلاین)
download_buttons = [
    [
        Button.url("🤖 نسخه اندروید", "https://download.wireguard.com/android-client/"),
        Button.url("🍏 نسخه آیفون / آیپد", "https://apps.apple.com/us/app/wireguard/id1441195209"),
    ],
    [
        Button.inline("🔙 بازگشت", b"back_to_main"),
    ],
]

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.respond(
        "سلام خوش آمدید🌟\n\nلطفا یکی از آیتم های زیر را انتخاب کنید 👇",
        buttons=main_inline_buttons
    )
    await event.respond(
        "اگر نیاز به پشتیبان داری روی دکمه پایین بزن:",
        buttons=support_button
    )

@bot.on(events.CallbackQuery(data=b"buy"))
async def buy(event):
    user_states[event.sender_id] = "awaiting_info"
    await event.respond("لطفاً فامیلی + ۴ رقم آخر موبایل را وارد کن (مثال: barari 8264)")
    await event.answer()

@bot.on(events.CallbackQuery(data=b"download_app"))
async def download_app(event):
    await event.respond(
        "لطفا نسخه دانلود خودتان را انتخاب کنید:",
        buttons=download_buttons
    )
    await event.answer()

@bot.on(events.CallbackQuery(data=b"back_to_main"))
async def back_to_main_callback(event):
    await event.edit(
        "به منوی اصلی برگشتید، لطفا یکی از آیتم های زیر را انتخاب کنید 👇",
        buttons=main_inline_buttons
    )
    await event.answer()


######################################################################################
######################################################################################
######################################################################################

support_id = 734514363
user_support_state = {}        # وضعیت انتظار پیام کاربر
support_reply_state = {}       # وضعیت انتظار پیام پشتیبان

@bot.on(events.NewMessage(pattern="🛠 پشتیبان"))
async def support_button_pressed(event):
    user_id = event.sender_id
    user_support_state[user_id] = True  # کاربر وارد حالت ارسال پیام شد

    await event.respond(
        "🧑‍💻 شما در حال ارسال پیام به پشتیبان هستید.\n"
        "لطفاً پیام متنی یا تصویری خود را وارد کنید.\n\n"
        "⚠️ فقط پیام‌های متنی و تصویری مجاز هستند."
    )

@bot.on(events.NewMessage())
async def support_message_handler(event):
    user_id = event.sender_id

    # --- پاسخ پشتیبان به کاربر ---
    if support_reply_state.get(user_id):
        target_user = support_reply_state.pop(user_id)
        try:
            if event.photo or event.document:
                caption = event.text or ""
                full_caption = f"📬 پاسخ پشتیبان:\n\n{caption}" if caption else "📬 پاسخ پشتیبان 🛠️"
                await bot.send_file(
                    target_user,
                    file=event.media,
                    caption=full_caption
                )
            elif event.text:
                await bot.send_message(
                    target_user,
                    f"📬 پاسخ پشتیبان:\n\n{event.text}"
                )
            await event.respond("✅ پاسخ شما برای کاربر ارسال شد.")
        except Exception as e:
            await event.respond("❌ خطا در ارسال پاسخ به کاربر.")
            print(f"❌ خطا در ارسال پیام به کاربر: {e}")
        return

    # --- پیام کاربر برای پشتیبان ---
    if user_support_state.get(user_id):
        # جلوگیری از ارسال مجدد دکمه
        if event.raw_text.strip() == "🛠 پشتیبان":
            return

        del user_support_state[user_id]

        await event.respond("✅ پیام شما برای پشتیبان ارسال شد.")

        # فرستادن پیام تصویری یا متنی برای پشتیبان
        if event.photo or event.document:
            caption = event.text or "بدون کپشن"
            await bot.send_file(
                support_id,
                file=event.media,
                caption=(
                    f"📩 پیام تصویری از کاربر:\n"
                    f"🆔 یوزرنیم: @{event.sender.username or 'ندارد'}\n"
                    f"🧾 آیدی عددی: {user_id}\n\n"
                    f"💬 کپشن:\n{caption}"
                ),
                buttons=[Button.inline("✉️ پاسخ به کاربر", data=f"reply_{user_id}")]
            )
        elif event.text:
            await bot.send_message(
                support_id,
                f"📩 پیام متنی از کاربر:\n"
                f"🆔 یوزرنیم: @{event.sender.username or 'ندارد'}\n"
                f"🧾 آیدی عددی: {user_id}\n\n"
                f"💬 پیام:\n{event.text}",
                buttons=[Button.inline("✉️ پاسخ به کاربر", data=f"reply_{user_id}")]
            )
        else:
            await event.respond("❌ فقط پیام‌های متنی و تصویری پشتیبانی می‌شوند.")

@bot.on(events.CallbackQuery(pattern=b"reply_\d+"))
async def handle_support_reply_button(event):
    if event.sender_id != support_id:
        await event.answer("⛔️ شما اجازه این عملیات را ندارید.", alert=True)
        return

    user_id = int(event.data.decode().split("_")[1])
    support_reply_state[event.sender_id] = user_id

    await event.respond("✍️ لطفاً پیام پاسخ را وارد کنید (متن یا عکس با کپشن):")



######################################################################################
######################################################################################
######################################################################################


@bot.on(events.NewMessage())
async def handle_input(event):
    user_id = event.sender_id

    if user_states.get(user_id) == "awaiting_info":
        user_states[user_id] = "awaiting_receipt"
        user_states[f"{user_id}_info"] = event.raw_text.strip()

        await event.respond(
            "💳 مبلغ مورد نظر رو به یکی از این شماره کارت‌ها واریز کن:\n\n"
            "`6393461040151330`\n"
            "`5859831218487840`\n"
            "(به نام میلاد مغربی)\n\n"
            "سپس رسید پرداخت را به صورت **عکس** ارسال کن 📸",
            parse_mode='markdown',
            buttons=card_buttons
        )
        return

    elif user_states.get(user_id) == "awaiting_receipt" and event.photo:
        filename = f"receipts/{user_id}_{event.id}.jpg"
        await event.download_media(file=filename)
        info = user_states.get(f"{user_id}_info", "نامشخص")

        payment = Payment(
            user_id=user_id,
            username=event.sender.username or "Unknown",
            family_info=info,
            receipt_path=filename,
        )
        session.add(payment)
        session.commit()

        del user_states[user_id]

        await event.respond("✅ رسید ثبت شد و در حال بررسی است.")

        await bot.send_file(
            admin_ids[0],
            file=filename,
            caption=f"🔔 رسید جدید از @{event.sender.username or 'کاربر'}\n{info}",
            buttons=[
                Button.inline("✅ تأیید", f"confirm_{payment.id}"),
                Button.inline("❌ رد", f"reject_{payment.id}")
            ]
        )

@bot.on(events.CallbackQuery(data=b"copy_card1"))
async def copy_card1(event):
    await bot.send_message(event.sender_id, "📇 شماره کارت:\n6393461040151330")
    await event.answer()

@bot.on(events.CallbackQuery(data=b"copy_card2"))
async def copy_card2(event):
    await bot.send_message(event.sender_id, "📇 شماره کارت:\n5859831218487840")
    await event.answer()

@bot.on(events.CallbackQuery(pattern=b"reject_"))
async def reject(event):
    if event.sender_id not in admin_ids:
        return

    payment_id = int(event.data.decode().split("_")[1])
    payment = session.get(Payment, payment_id)
    if not payment:
        await event.respond("❌ پرداخت یافت نشد.")
        return

    session.delete(payment)
    session.commit()

    await event.respond("❌ رسید رد شد.")

    try:
        await bot.send_message(
            payment.user_id,
            "❌ رسید شما توسط ادمین تایید نشد.\nلطفاً دوباره یک عکس واضح از رسید ارسال کنید."
        )
    except Exception as e:
        print(f"خطا در ارسال پیام رد به کاربر: {e}")

@bot.on(events.CallbackQuery(pattern=b"confirm_"))
async def confirm(event):
    if event.sender_id not in admin_ids:
        return

    payment_id = int(event.data.decode().split("_")[1])
    payment = session.get(Payment, payment_id)
    if not payment:
        await event.respond("پرداخت یافت نشد.")
        return

    payment.is_confirmed = True
    session.commit()

    qrcode = session.query(QRCode).filter_by(is_used=False).order_by(QRCode.id).first()
    if not qrcode:
        await bot.send_message(payment.user_id, "❌ بارکدها تمام شدند. لطفاً بعداً دوباره تلاش کنید.")
        await bot.send_message(admin_ids[0], "🚨 بارکدها تمام شدند! لطفاً 20 بارکد جدید آپلود کنید.")
        return

    qrcode.is_used = True
    session.commit()

    await bot.send_file(
        payment.user_id,
        f"qrcodes/{qrcode.filename}",
        caption=(
            "🔒 اشتراک شما فعال شد.\n\n"
            "برای وارد کردن بارکد لطفاً مراحل زیر رو انجام بده:\n"
            "1. با گوشی دیگه از این بارکد عکس بگیر📸\n"
            "2. برنامه Wireguard رو باز کن\n"
            "3. بالا سمت راست روی + بزن ➕\n"
            "4. گزینه 'Scan from QR code' رو انتخاب کن ✅\n"
            "5. عکس رو انتخاب و اسکن کن\n"
            "6. هر اسمی خواستی بزن 📝\n"
            "7. تیک کنار اسم رو روشن کن 🔛\n\n"
        )
    )
    await event.respond("✅ پرداخت تایید و بارکد ارسال شد.")

    remaining = session.query(QRCode).filter_by(is_used=False).count()
    if remaining == 5:
        await bot.send_message(admin_ids[0], "⚠️ فقط ۵ بارکد باقی مانده! لطفاً بارکد های جدید را آماده کنید \n که زمانی پیام اتمام براتون ارسال شد بارکد هارو سریع آپلود کنید.")

@bot.on(events.Album())
async def upload_album(event):
    global barcode_upload_count
    if event.sender_id not in admin_ids:
        return

    messages = event.messages
    count = len(messages)

    if count > 10:
        await event.respond(f"❌ حداکثر ۱۰ عکس در هر نوبت مجاز است (شما {count} ارسال کردید).")
        return

    start_index = barcode_upload_count + 1
    end_index = barcode_upload_count + count

    if end_index > 20:
        await event.respond("❌ بیشتر از ۲۰ بارکد نمی‌توانید آپلود کنید.")
        return

    if barcode_upload_count == 0:
        shutil.rmtree("qrcodes", ignore_errors=True)
        os.makedirs("qrcodes", exist_ok=True)
        session.query(QRCode).delete()
        session.commit()

    for i, msg in enumerate(messages, start=start_index):
        path = f"qrcodes/{i}.png"
        await msg.download_media(file=path)
        session.add(QRCode(id=i, filename=f"{i}.png", is_used=False))

    session.commit()
    barcode_upload_count = end_index

    if barcode_upload_count == 20:
        await event.respond("✅ ۲۰ بارکد با موفقیت آپلود شد.")

    else:
        remaining = 20 - barcode_upload_count
        await event.respond(f"✅ {count} بارکد ذخیره شد. باقی مانده: {remaining} عدد.")

######################################################################################
######################################################################################
######################################################################################


async def check_expiring_subscriptions():
    now = datetime.utcnow()
    threshold = timedelta(days=28)  

    expiring_users = session.query(Payment).filter(
        Payment.is_confirmed == True,
        Payment.created_at <= now - threshold,
        Payment.reminder_sent == False
    ).all()

    for payment in expiring_users:
        try:
            await bot.send_message(
                payment.user_id,
                "سلام 👋\n"
                "اشتراک شما تا ۵ روز دیگه به پایان می‌رسه.\n\n"
                "برای جلوگیری از قطع سرویس، همین حالا می‌تونی تمدیدش کنی✅\n\n"
                "📌 جهت تمدید اشتراک روی دکمه زیر کلیک کن👇",
                buttons=main_inline_buttons
            )
            payment.reminder_sent = True
            session.commit()
        except Exception as e:
            print(f"❌ خطا در ارسال پیام به {payment.user_id}: {e}")


async def schedule_daily_check():
    while True:
        await check_expiring_subscriptions()
        await asyncio.sleep(86400)  # هر ۱۰ ثانیه برای تست

loop = asyncio.get_event_loop()
loop.create_task(schedule_daily_check())


print("🤖 Bot is running...")
bot.run_until_disconnected()
