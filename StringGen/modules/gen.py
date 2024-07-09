import asyncio

from pyrogram import Client, filters
from oldpyro import Client as Client1
from oldpyro.errors import ApiIdInvalid as ApiIdInvalid1
from oldpyro.errors import PasswordHashInvalid as PasswordHashInvalid1
from oldpyro.errors import PhoneCodeExpired as PhoneCodeExpired1
from oldpyro.errors import PhoneCodeInvalid as PhoneCodeInvalid1
from oldpyro.errors import PhoneNumberInvalid as PhoneNumberInvalid1
from oldpyro.errors import SessionPasswordNeeded as SessionPasswordNeeded1
from pyrogram.errors import (
    ApiIdInvalid,
    FloodWait,
    PasswordHashInvalid,
    PhoneCodeExpired,
    PhoneCodeInvalid,
    PhoneNumberInvalid,
    SessionPasswordNeeded,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from telethon import TelegramClient
from telethon.errors import (
    ApiIdInvalidError,
    PasswordHashInvalidError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
)
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from pyromod.listen.listen import ListenerTimeout

from config import SUPPORT_CHAT
from StringGen import Anony
from StringGen.utils import retry_key


async def gen_session(
    message, user_id: int, telethon: bool = False, old_pyro: bool = False
):
    if telethon:
        ty = f"تيرمكس"
    elif old_pyro:
        ty = f"بايروگرام v1"
    else:
        ty = f"بايروگرام v2"

    await message.reply_text(f"» محاولة البدء {ty} انشاء الجلسة...")

    try:
        api_id = await Anony.ask(
            identifier=(message.chat.id, user_id, None),
            text="» يرجى إدخال API IDالخاصة بك للمتابعة :",
            filters=filters.text,
            timeout=300,
        )
    except ListenerTimeout:
        return await Anony.send_message(
            user_id,
            "» تم الوصول إلى الحد الزمني لمدة 5 دقائق.\n\nيرجى البدء في إنشاء الجلسة مرة أخرى.",
            reply_markup=retry_key,
        )

    if await cancelled(api_id):
        return

    try:
        api_id = int(api_id.text)
    except ValueError:
        return await Anony.send_message(
            user_id,
            "» معرف API الذي أرسلته غير صالح. \n\n الرجاء البدء في إنشاء الجلسة مرة أخرى",
            reply_markup=retry_key,
        )

    try:
        api_hash = await Anony.ask(
            identifier=(message.chat.id, user_id, None),
            text="»يرجى إدخال API HASH الخاصة بك للمتابعة:",
            filters=filters.text,
            timeout=300,
        )
    except ListenerTimeout:
        return await Anony.send_message(
            user_id,
            "» تم الوصول إلى الحد الزمني لمدة 5 دقائق.\n\nيرجى البدء في إنشاء الجلسة مرة أخرى.",
            reply_markup=retry_key,
        )

    if await cancelled(api_hash):
        return

    api_hash = api_hash.text

    if len(api_hash) < 30:
        return await Anony.send_message(
            user_id,
            "» معرف API الذي أرسلته غير صالح. \n\n الرجاء البدء في إنشاء الجلسة مرة أخرى",
            reply_markup=retry_key,
        )

    try:
        phone_number = await Anony.ask(
            identifier=(message.chat.id, user_id, None),
            text="» الرجاء إدخال رقم هاتفك للمتابعة :",
            filters=filters.text,
            timeout=300,
        )
    except ListenerTimeout:
        return await Anony.send_message(
            user_id,
            "» معرف API الذي أرسلته غير صالح. \n\n الرجاء البدء في إنشاء الجلسة مرة أخرى",
            reply_markup=retry_key,
        )

    if await cancelled(phone_number):
        return
    phone_number = phone_number.text

    await Anony.send_message(user_id, "» محاولة إرسال OTP على الرقم المحدد...")
    if telethon:
        client = TelegramClient(StringSession(), api_id, api_hash)
    elif old_pyro:
        client = Client1(":memory:", api_id=api_id, api_hash=api_hash)
    else:
        client = Client(name="Anony", api_id=api_id, api_hash=api_hash, in_memory=True)
    await client.connect()

    try:
        if telethon:
            code = await client.send_code_request(phone_number)
        else:
            code = await client.send_code(phone_number)
        await asyncio.sleep(1)

    except FloodWait as f:
        return await Anony.send_message(
            user_id,
            f"» فشل في إرسال الرمز لتسجيل الدخول.\n\nمن فضلك انتظر {f.value or f.x} ثواني وحاول مرة أخرى.",
            reply_markup=retry_key,
        )
    except (ApiIdInvalid, ApiIdInvalidError, ApiIdInvalid1):
        return await Anony.send_message(
            user_id,
            "»خطاء في ستخراج جلسه او ايبي ايدي / ايبي هاش  غير صالحة \n\n الرجاء البدء في إنشاء جلستك مرة أخرى.",
            reply_markup=retry_key,
        )
    except (PhoneNumberInvalid, PhoneNumberInvalidError, PhoneNumberInvalid1):
        return await Anony.send_message(
            user_id,
            "»رقم الهاتف غير صالح. \n\n الرجاء البدء في إنشاء جلستك مرة أخرى.",
            reply_markup=retry_key,
        )

    try:
        otp = await Anony.ask(
            identifier=(message.chat.id, user_id, None),
            text=f"قم بارسـال الكود الذي وصل اليك من الشركة {phone_number}.\n\n  اذا كان الكـود هـو <code>12345</code>,- يرجى ارساله هكـذا  <code>1 2 3 4 5.</code>",
            filters=filters.text,
            timeout=600,
        )
        if await cancelled(otp):
            return
    except ListenerTimeout:
        return await Anony.send_message(
            user_id,
            "»تم الوصول إلى الحد الزمني وهو 10 دقائق. \n\n الرجاء البدء في إنشاء جلستك مرة أخرى.",
            reply_markup=retry_key,
        )

    otp = otp.text.replace(" ", "")
    try:
        if telethon:
            await client.sign_in(phone_number, otp, password=None)
        else:
            await client.sign_in(phone_number, code.phone_code_hash, otp)
    except (PhoneCodeInvalid, PhoneCodeInvalidError, PhoneCodeInvalid1):
        return await Anony.send_message(
            user_id,
            "» كلمة المرور لمرة واحدة التي أرسلتها<b>خاطئة.</b>\n\nيرجى البدء في إنشاء جلستك مرة أخرى.",
            reply_markup=retry_key,
        )
    except (PhoneCodeExpired, PhoneCodeExpiredError, PhoneCodeExpired1):
        return await Anony.send_message(
            user_id,
            "» كلمة المرور لمرة واحدة التي أرسلتها<b>منتهي الصلاحية.</b>\n\nيرجى البدء في إنشاء جلستك مرة أخرى.",
            reply_markup=retry_key,
        )
    except (SessionPasswordNeeded, SessionPasswordNeededError, SessionPasswordNeeded1):
        try:
            pwd = await Anony.ask(
                identifier=(message.chat.id, user_id, None),
                text="» الرجاء إدخال كلمة مرور التحقق بخطوتين :",
                filters=filters.text,
                timeout=300,
            )
        except ListenerTimeout:
            return Anony.send_message(
                user_id,
                "» تم الوصول إلى الحد الزمني لمدة 5 دقائق.\n\nيرجى البدء في إنشاء الجلسة مرة أخرى.",
                reply_markup=retry_key,
            )

        if await cancelled(pwd):
            return
        pwd = pwd.text

        try:
            if telethon:
                await client.sign_in(password=pwd)
            else:
                await client.check_password(password=pwd)
        except (PasswordHashInvalid, PasswordHashInvalidError, PasswordHashInvalid1):
            return await Anony.send_message(
                user_id,
                "» كلمة المرور التي أرسلتها خاطئة.\n\nيرجى البدء في إنشاء جلستك مرة أخرى.",
                reply_markup=retry_key,
            )

    except Exception as ex:
        return await Anony.send_message(user_id, f"ᴇʀʀᴏʀ : <code>{str(ex)}</code>")

    try:
        txt = "إليك {0} جلسة STRING الخاصة بك\n\n<code>{1}</code>\n\nروبوت مولد STRING بواسطة <a href={2}>سورس ليثون</a>\n☠ <b> ملاحظة:</b>لا تشاركه مع صديقتك."
        if telethon:
            string_session = client.session.save()
            await client.send_message(
                "me",
                txt.format(ty, string_session, SUPPORT_CHAT),
                link_preview=False,
                parse_mode="html",
            )
            await client(JoinChannelRequest("@A1DIIU"))
        else:
            string_session = await client.export_session_string()
            await client.send_message(
                "me",
                txt.format(ty, string_session, SUPPORT_CHAT),
                disable_web_page_preview=True,
            )
            await client.join_chat("A1DIIU")
    except KeyError:
        pass
    try:
        await client.disconnect()
        await Anony.send_message(
            chat_id=user_id,
            text=f"تم إنشاء جلسة السلسلة {ty} الخاصة بك بنجاح. \n\n يرجى التحقق من رسائلك المحفوظة للحصول عليها.\n\nبوت مولد السلسلة بواسطة<a href={SUPPORT_CHAT}>بوت ستخراج</a>.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="𝐋𝐄𝐓𝐇𝐎𝐍𓅛",
                            url=f"tg://openmessage?user_id={user_id}",
                        )
                    ]
                ]
            ),
            disable_web_page_preview=True,
        )
    except:
        pass


async def cancelled(message):
    if "/cancel" in message.text:
        await message.reply_text(
            "» تم إلغاء عملية إنشاء السلسلة الجارية.", reply_markup=retry_key
        )
        return True
    elif "/restart" in message.text:
        await message.reply_text(
            "» تم إعادة تشغيل هذا الروبوت بنجاح.", reply_markup=retry_key
        )
        return True
    elif message.text.startswith("/"):
        await message.reply_text(
            "» تم إلغاء عملية إنشاء السلسلة الجارية.", reply_markup=retry_key
        )
        return True
    else:
        return False
