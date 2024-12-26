from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext

# Bot tokeningiz
TOKEN = "7606138212:AAG_9LkT5tbSsiHFYOyApPPDhhO9I_AUxGw"

# Adminning Telegram ID raqami
admin_id = "7298632202"  # Sizning Telegram ID raqamingiz

# Foydalanuvchilarning ma'lumotlari
user_data = {}

# /start komandasi
async def start(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    if user_id not in user_data:
        user_data[user_id] = {"free_used": False, "balance": 0}

    message = (
        "Assalomu alaykum! Ushbu bot slaydlar, referatlar va mustaqil ishlarni tayyorlab beradi.\n\n"
        "Siz bir marta bepul foydalanishingiz mumkin. Xizmat buyurtma qilish uchun quyidagi tugmani bosing."
    )

    buttons = [
        [InlineKeyboardButton("Mustaqil ish tayyorlash", callback_data="request_service")],
        [InlineKeyboardButton("Balans", callback_data="check_balance")],
        [InlineKeyboardButton("To'lov qilish", callback_data="make_payment")]
    ]
    
    await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(buttons))

# Xizmat buyurtma qilish
async def request_service(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    if not user_data[user_id]["free_used"]:
        user_data[user_id]["free_used"] = True
        await query.edit_message_text(
            "Mavzuni kiriting va keyin bet sonini tanlang: \n\n10 bet \n15 bet \n20 bet."
        )
        # Mustaqil ish tayyorlash uchun mavzu kiritishni kutamiz
        context.user_data['awaiting_topic'] = True
    else:
        await query.edit_message_text(
            "Sizning bepul huquqingiz tugagan. Xizmatdan foydalanishni davom ettirish uchun quyidagi kartaga pul tashlang.\n\n"
            "💳 Karta: 5614 6835 1192 6941\n"
            "👤 Ism: Javohirbek Xakimjonov\n\n"
            "To'lovni amalga oshirgandan so'ng, /chek komandasini yuboring va tasdiqni kuting."
        )

# Mustaqil ish tayyorlash
async def prepare_assignment(update: Update, context: CallbackContext):
    user_id = update.message.chat_id

    if context.user_data.get('awaiting_topic'):
        context.user_data['topic'] = update.message.text
        context.user_data['awaiting_topic'] = False

        # Bet sonini tanlash tugmalari
        buttons = [
            [InlineKeyboardButton("10 bet", callback_data="10")],
            [InlineKeyboardButton("15 bet", callback_data="15")],
            [InlineKeyboardButton("20 bet", callback_data="20")]
        ]
        await update.message.reply_text("Bet sonini tanlang:", reply_markup=InlineKeyboardMarkup(buttons))
    elif context.user_data.get('awaiting_page_count'):
        page_count = int(update.message.text)
        topic = context.user_data.get('topic')
        context.user_data['awaiting_page_count'] = False

        # Kontentni yaratish (bu qismini sun'iy intellekt yordamida to'ldiring)
        assignment_content = f"Mavzu: {topic}\nBetlar soni: {page_count}\n\nMustaqil ish tayyorlandi!"

        # Foydalanuvchiga yuborish
        await update.message.reply_text(assignment_content)
    else:
        await update.message.reply_text("Iltimos, oldin mavzu yoki bet sonini tanlang.")

# To'lovni amalga oshirish uchun xabar
async def request_payment(update: Update, context: CallbackContext):
    query = update.callback_query
    if query:
        message = (
            "Sizning to'lovingizni amalga oshirish uchun quyidagi karta ma'lumotlarini ishlating:\n\n"
            "💳 Karta: 5614 6835 1192 6941\n"
            "👤 Ism: Javohirbek Xakimjonov\n\n"
            "To'lovni amalga oshirgandan so'ng, /chek komandasini yuboring va tasdiqni kuting."
        )
        await query.answer()
        await query.edit_message_text(message)

# Foydalanuvchi to'lov chekini yuborganda
async def handle_check(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    
    # Foydalanuvchi rasm yuborganini tekshiramiz
    if update.message.photo:
        # Rasmlarni olish
        photo = update.message.photo[-1]
        file = await photo.get_file()

        # Rasmlarni admin chatiga yuborish
        await context.bot.send_photo(
            chat_id=admin_id,
            photo=file.file_id,
            caption=f"💳 Foydalanuvchi {user_id} to'lov chekini yubordi.\n\n"
                    "Tasdiqlash uchun /confirm {user_id} summa komandasini yuboring.\n"
                    "Agar rad etmoqchi bo'lsangiz, /reject {user_id} komandasini yuboring."
        )

        # Foydalanuvchiga tasdiqlash kutish haqida xabar yuborish
        await update.message.reply_text("Chek adminga yuborildi. Admin tomonidan tasdiqlanishini kuting.")
    else:
        await update.message.reply_text("Chekni yuboring, iltimos.")  # Foydalanuvchi hech narsa yubormagan bo'lsa

# Admin tomonidan tasdiqlash
async def confirm_payment(update: Update, context: CallbackContext):
    if str(update.message.chat_id) == admin_id:
        try:
            args = update.message.text.split()  # Tasdiqlash xabari format: `/confirm 123456789 3000`
            if len(args) < 3:
                raise ValueError("Noto'g'ri format")

            user_id = int(args[1])
            amount = int(args[2])  # To'lov summasi

            if user_id not in user_data:
                await update.message.reply_text("❌ Ushbu foydalanuvchi topilmadi.")
                return

            # Foydalanuvchi balansini yangilash
            user_data[user_id]["balance"] += amount
            user_data[user_id]["free_used"] = False

            # Foydalanuvchiga xabar yuborish
            await context.bot.send_message(
                chat_id=user_id,
                text=f"✅ To'lovingiz tasdiqlandi. Balansingiz: {user_data[user_id]['balance']} so'm /start ni bosing."
            )

            # Admin uchun xabar
            await update.message.reply_text(
                f"✅ Tasdiq muvaffaqiyatli amalga oshirildi! Foydalanuvchining yangi balansi: {user_data[user_id]['balance']} so'm."
            )
        except (IndexError, KeyError, ValueError):
            await update.message.reply_text(
                "❌ Noto‘g‘ri format. To‘g‘ri format: `/confirm foydalanuvchi_id summa`"
            )
    else:
        await update.message.reply_text("Bu buyruq faqat admin tomonidan ishlatilishi mumkin.")

# Admin tomonidan to'lovni rad etish
async def reject_payment(update: Update, context: CallbackContext):
    if str(update.message.chat_id) == admin_id:
        try:
            user_id = int(update.message.text.split()[1])  # Rad etish xabari format: `/reject 123456789`
            await context.bot.send_message(chat_id=user_id, text="❌ To'lovingiz rad etildi. Iltimos, to'g'ri chek yuboring.")
            await update.message.reply_text("✅ To'lov rad etildi va foydalanuvchiga xabar yuborildi.")
        except (IndexError, KeyError, ValueError):
            await update.message.reply_text("❌ Noto‘g‘ri format. To‘g‘ri format: `/reject foydalanuvchi_id`")
    else:
        await update.message.reply_text("Bu buyruq faqat admin tomonidan ishlatilishi mumkin.")

# Balansni tekshirish
async def check_balance(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    if user_id in user_data:
        message = (
            f"💰 Sizning balansingiz:{user_data[user_id]['balance']} so'm\n\n"
            f"💳 Bepul foydalanish huquqi: {'Foydalangan' if user_data[user_id]['free_used'] else 'Foydalanmagan'}\n"
            
        )
        
        # To'lov qilish tugmasi faqat xizmatdan foydalanish bepul bo'lmagan holatda
        buttons = []
        if user_data[user_id]["free_used"]:  # Foydalangan bo'lsa
            buttons.append([InlineKeyboardButton("To'lov qilish", callback_data="make_payment")])

        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(buttons))

# Xabarlarni ushlash
async def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    if context.user_data.get('awaiting_topic') or context.user_data.get('awaiting_page_count'):
        await prepare_assignment(update, context)
    else:
        await update.message.reply_text("Xizmatlardan foydalanish uchun /start ni bosing.")

# Botni ishga tushirish
def main():
    application = Application.builder().token(TOKEN).build()

    # Komanda va xabarlarni qo‘shish
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("confirm", confirm_payment))
    application.add_handler(CommandHandler("reject", reject_payment))
    application.add_handler(CommandHandler("chek", handle_check))  
    application.add_handler(CallbackQueryHandler(request_service, pattern="request_service"))
    application.add_handler(CallbackQueryHandler(request_payment, pattern="make_payment"))
    application.add_handler(CallbackQueryHandler(check_balance, pattern="check_balance"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_check))  

    # Botni ishga tushirish
    application.run_polling()

if __name__ == "__main__":
    main()
