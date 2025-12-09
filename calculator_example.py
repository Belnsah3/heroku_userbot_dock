from .. import loader, utils

@loader.tds
class CalculatorMod(loader.Module):
    """Простой модуль-калькулятор для примера"""
    
    strings = {
        "name": "QuickCalc",
        "result": "🔢 <b>Результат:</b> <code>{}</code>",
        "error": "🚫 <b>Ошибка:</b> <code>{}</code>"
    }

    @loader.command(alias="calc")
    async def countcmd(self, message):
        """<выражение> - Посчитать математическое выражение"""
        # 1. Получаем аргументы (то, что после команды)
        expression = utils.get_args_raw(message)
        
        # 2. Проверяем, что пользователь что-то написал
        if not expression:
            await utils.answer(message, "А что считать?")
            return

        # 3. Считаем
        try:
            # eval опасен, но для простого примера пойдет. 
            # Мы удаляем опасные символы для минимальной защиты.
            safe_expr = expression.replace("__", "").replace("import", "").replace("exec", "")
            
            # Выполняем расчет
            result = eval(safe_expr)
            
            # 4. Отправляем ответ
            await utils.answer(message, self.strings("result").format(result))
            
        except Exception as e:
            # Если ошибка (например деление на ноль)
            await utils.answer(message, self.strings("error").format(e))
