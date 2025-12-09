# requires: telethon
from .. import loader, utils
from telethon.tl.types import UserStatusOnline, UserStatusOffline, UserStatusRecently, UserStatusLastWeek, UserStatusLastMonth

@loader.tds
class WhoIsMod(loader.Module):
    """
    Продвинутый модуль информации о пользователе.
    Демонстрирует работу с Entity, Status и Formatting.
    """
    strings = {
        "name": "WhoIsPro",
        "loading": "🔄 <b>Получаю информацию...</b>",
        "user_info": (
            "👤 <b>INFO FOR:</b> <a href='tg://user?id={id}'>{full_name}</a>\n"
            "🆔 <b>ID:</b> <code>{id}</code>\n"
            "🦅 <b>Username:</b> {username}\n"
            "🦠 <b>Bot:</b> {is_bot}\n"
            "🔋 <b>Status:</b> {status}\n"
            "📸 <b>Photo:</b> {has_photo}"
        ),
        "no_user": "❌ <b>Пользователь не найден.</b>"
    }

    @loader.command(alias="whois")
    async def userinfocmd(self, message):
        """<reply/username> - Получить инфо о юзере"""
        
        # 1. Используем utils.answer для пре-лоадинга
        await utils.answer(message, self.strings("loading"))
        
        # 2. Пытаемся получить пользователя
        args = utils.get_args(message)
        reply = await message.get_reply_message()
        
        user = None
        try:
            if reply:
                user = await self.client.get_entity(reply.sender_id)
            elif args:
                user = await self.client.get_entity(args[0])
            else:
                user = await self.client.get_entity("me")
        except:
            # Если юзер скрыт или не найден
            await utils.answer(message, self.strings("no_user"))
            return

        # 3. Определяем статус (Онлайн/Оффлайн)
        status = "Unknown"
        if isinstance(user.status, UserStatusOnline):
            status = "🟢 Online"
        elif isinstance(user.status, UserStatusOffline):
            status = f"🔴 Offline (seen {utils.format_date(user.status.was_online)})"
        elif isinstance(user.status, UserStatusRecently):
            status = "🟡 Recently"
        elif isinstance(user.status, UserStatusLastWeek):
            status = "🟡 Last Week"
        elif isinstance(user.status, UserStatusLastMonth):
            status = "🟡 Last Month"

        # 4. Проверяем наличие фото
        has_photo = "Yes" if user.photo else "No"
        
        # 5. Формируем ФИО
        full_name = utils.escape_html(f"{user.first_name} {user.last_name or ''}".strip())
        username = f"@{user.username}" if user.username else "No username"

        # 6. Отправляем красивый ответ
        # Если есть фото - отправляем с фото, если нет - просто текст
        caption = self.strings("user_info").format(
            id=user.id,
            full_name=full_name,
            username=username,
            is_bot="Yes" if user.bot else "No",
            status=status,
            has_photo=has_photo
        )

        if user.photo:
            # Скачиваем и отправляем фото профиля
            photo = await self.client.download_profile_photo(user, file=bytes)
            # Удаляем сообщение "loading" и отправляем новое с фото
            await message.delete() 
            await self.client.send_file(
                message.chat_id, 
                photo, 
                caption=caption,
                reply_to=reply.id if reply else None
            )
        else:
            await utils.answer(message, caption)
