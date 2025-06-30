import nest_asyncio
nest_asyncio.apply()
import random
import asyncio
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
import openai
from openai import AsyncOpenAI


from dotenv import load_dotenv
import os
import logging

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = "https://telegram-l27s.onrender.com"
client = AsyncOpenAI(api_key=openai.api_key)


logging.basicConfig(level=logging.INFO)

chat_users = set()  # множество для отслеживания пользователей в режиме чата

arsenals = {
    "🔥 Быстрые приколы и кайфовые движухи": [
        "😂 Залипни на мемах — придумывай свои подписи и смейся до слёз.",
        "📺 Вбей в YouTube «How to…» и выбери первое видео — учись фехтовать морковкой или завязывать галстук.",
        "🎯 Поищи странные челленджи в ТикТоке — повторить или просто посмеяться.",
        "🍪 Найди самый странный рецепт на кулинарном канале и попробуй представить, как это на вкус.",
        "⏱ Запусти таймер на 5 минут и пиши список самых бессмысленных целей, например, стать космонавтом-единорогом.",
        "🎲 Попроси меня придумать мини-игру с хаосом и без правил — скука убежит!",
        "🎶 Включи песни 80-х на повтор и танцуй как звезда MTV, даже если дома один.",
        "🦸‍♂️ Пройди абсурдный тест «какой ты супергерой» — сюрприз и смех гарантированы.",
        "📝 Напиши самый бесполезный список в мире — например, как пропустить встречу и не попасться."
    ],
    "🧠 Для ума и лёгкой прокачки": [
        "📚 Учись 30 минут — код, рисование или почему японцы любят хай-тек туалеты.",
        "🌐 Листай случайные статьи в Википедии — открой для себя осьминогов-инопланетян или лягушек-пряток.",
        "🎲 Делай это ритуалом — каждый день новая тема, и она всегда непредсказуемая.",
        "🧩 Пройди тест на IQ или эмоциональный интеллект — чтобы узнать, насколько ты загадка для себя.",
        "🪞 Объясни сложную тему себе в зеркало с паузами на смех и «да ну нафиг».",
        "🎧 Включи подкаст по непонятной теме и ищи забавный факт, чтобы удивить самого себя.",
        "🤯 Поищи в интернете слово «парадокс» и удивляйся этому безумию.",
        "🌟 Сделай карту желаний с дикими мечтами — полет на Луну, дружба с драконом и прочее."
    ],
    "🎭 Арт и творчество без напряга": [
        "🚀 Напиши рассказ про космическую корову, которая спасает галактику — будь странным и смешным.",
        "🍕 Напиши стишок о пицце и вечной прокрастинации — для вдохновения и смеха.",
        "✍️ Нарисуй каракули «мне лень, но хочется» — повод посмеяться или создать шедевр.",
        "🎥 Сними короткое видео, где ты режиссёр, но всё идёт не так — смейся и монтируй без правил.",
        "👟 Придумай блокбастер с главным героем — своей обувью. Звезда deserves славу!",
        "📸 Сделай мини-фотоисторию из будильника, кружки и тапка с диалогами."
    ],
    "💪 Для тела (но без фанатизма)": [
        "⏳ 7 минут лёгкой боли — и ты почти супергерой (плащ не гарантируется).",
        "🚶‍♂️ Выходи на улицу с подкастом про бандитов 90-х или деревенскую жизнь и просто кайфуй.",
        "💃 Танцуй, как будто никто не смотрит — даже если смотрят, всё равно танцуй.",
        "🌬 Сделай 10 минут дыхательной гимнастики — не засыпай!",
        "🔥 Устрой танцпол у себя в комнате под любимый трек — звезда клуба в деле.",
        "🏃‍♂️ Пробеги лёгкую тренировку из приложения — устал? Говори, что это интервальная пауза.",
        "🏆 Придумай мини-ритуал — 10 прыжков, 5 отжиманий и танец победы, делай когда хочешь.",
        "🐢 Стань мастером медленного движения — растяжка или походка в стиле «медленно и стильно».",
        "🧘‍♂️ Попробуй йогу для ленивых — позы как для сна, но с пользой."
    ],
    "🎮 Игры, чтобы просто кайфануть": [
        "🐐 Играй в странный симулятор козла, гуся с миссией или что-то невообразимое.",
        "🃏 Карточные игры соло — учись бить самого себя и выигрывать.",
        "👶 Вспомни себя ребёнком без правил и просто кайфуй от процесса.",
        "🧸 Играй в «что если» — враги плюшевые мишки, просто фантазируй и наслаждайся.",
        "🧩 Запусти пазл и собирай его максимально медленно, чтобы почувствовать абсурд.",
        "🎤 Словесные игры — рифмуй слова с «пельмени» и «горошек», смейся и продолжай.",
        "🎮 Запусти старую игру и вспомни кайф просто нажимать кнопки без смысла.",
        "🌍 Пофантазируй про свой мир и игру там — рисуй в голове и записывай идеи."
    ]
}


arsenals_зарядок = {
    "зарядка_вариант_1": [
        "Утренняя зарядка на 10 минут — включайся в драйв! ⚡️🔥\n"
        "1. Разогрев (2 мин)\n"
        "👋 Махи руками вперёд и назад — 30 сек\n"
        "🔄 Круговые вращения плечами — 30 сек (вперёд и назад)\n"
        "🤸‍♂️ Наклоны головы и лёгкие повороты — 30 сек\n"
        "🏃‍♂️ Лёгкий бег на месте с поднятием колен — 30 сек\n\n"
        "2. Динамическая часть (4 мин)\n"
        "✨ Прыжки «звёздочка» — 40 раз (разминай суставы)\n"
        "🦵 Приседания с руками вверх — 20 раз (не надо глубоко, главное — движение)\n"
        "🚶‍♂️ Выпады вперёд — по 10 на каждую ногу (чуть растягиваем бёдра)\n"
        "💪 Отжимания от стены или пола — 15 раз (чуть напряги руки и грудь)\n\n"
        "3. Сила и баланс (2,5 мин)\n"
        "🧘‍♂️ Планка на локтях — держи 45 секунд, дыши ровно\n"
        "🍑 Подъёмы таза лёжа — 20 раз (включай ягодицы, не спину)\n"
        "🦶 Баланс на одной ноге — по 30 сек на каждую ногу, руки в стороны (включаем мозг и стабилизацию)\n\n"
        "4. Растяжка и расслабление (1,5 мин)\n"
        "🙆‍♂️ Наклоны вперёд, пытаясь дотянуться до пальцев ног — 30 сек (без фанатизма!)\n"
        "😺 Потягивания стоя — руки вверх, тянись как кошка после сна — 30 сек\n"
        "🌬️ Глубокие вдохи с поднятыми руками и выдохи с опусканием — 30 сек"
    ],
    "зарядка_вариант_2": [
"""Зарядка вариант 2 — взбодрись и зажги! ⚡️🔥
1. Разогрев (2 мин)
🤸‍♀️ Круговые махи ногами вперёд-назад — по 30 сек на каждую ногу
👐 Разводим руки в стороны и собираем вместе — 1 мин, плавно, чтобы разогреть плечи и грудь

2. Динамическая часть (4 мин)
🏃‍♂️ Бег на месте с захлёстом пяток к ягодицам — 40 секунд
🦵 Приседания с поворотом корпуса в сторону — 15 раз на каждую сторону (включаем косые мышцы)
🐾 Шаги "крабом" влево-вправо — 1 минута (для боковой стабилизации)
💪 Отжимания с колен — 20 раз (чуть полегче, но с чувством)

3. Сила и баланс (2,5 мин)
🧘‍♀️ Статический выпад — держим по 30 сек на каждую ногу, руки вверх (тут и баланс, и растяжка)
🍑 Мостик на ягодицы с поднятой ногой — по 15 раз на каждую ногу
🦶 Баланс на одной ноге с закрытыми глазами — по 20 сек (если не упал — герой!)

4. Растяжка и расслабление (1,5 мин)
🙇‍♂️ Наклоны головы в стороны — по 20 сек на каждую сторону
👐 Потягивания вперёд, пытаясь дотянуться до пола — 30 сек (без фанатизма)
🌬️ Глубокие вдохи через нос, выдох через рот — 30 сек, представляй, как вся усталость уходит прочь"""

    ],
}

async def start_training_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
    [
        InlineKeyboardButton("💥 День 1", callback_data='тренировка1'),
        InlineKeyboardButton("🍑 День 2", callback_data='тренировка2')
    ],
    [
        InlineKeyboardButton("🦾 День 3", callback_data='тренировка3'),
        InlineKeyboardButton("⚡ День 4", callback_data='тренировка4')
    ]
]

    reply_markup = InlineKeyboardMarkup(keyboard)

    message = (
        "🔥 *Готов прокачать тело и дух?*\n"
        "Выбери день тренировки и вперёд к цели!\n\n"
        "_Помни: маленький шаг каждый день — это путь к большому результату_ 💪"
    )

    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="Markdown")


async def handle_training_day_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data  # ожидается 'тренировка1', 'тренировка2' и т.д.
    
    if data.startswith("тренировка"):
        day = int(data.replace("тренировка", ""))
        context.user_data[f"warmup_index_day{day}"] = 0
        context.user_data[f"main_index_day{day}"] = 0
        context.user_data["warmup_message_ids"] = []
        context.user_data["main_message_ids"] = []

        # Отправляем первое сообщение разминки для дня
        warmup_texts = {
            1: (
                "🟡 *РАЗМИНКА (5 минут)*\nНачнём шаг за шагом!\n\n"
                "1️⃣ Круговые вращения руками вперёд — 15 секунд\n"
                "2️⃣ Круговые вращения руками назад — 15 секунд\n"
                "3️⃣ Плечевые круги и махи руками — 30 секунд\n"
                "4️⃣ Прыжки на месте — 30 секунд\n"
                "5️⃣ Лёгкие отжимания от пола — 10 повторений\n"
                "6️⃣ Подъём гантелей на бицепс (разогрев) — 10 повторений\n"
                "7️⃣ Скручивания на пресс — 15 повторений\n"
                "8️⃣ Планка — 30 секунд\n"
            ),
            2: (
                "🟡 *РАЗМИНКА (5 минут)*\nНачнём шаг за шагом!\n\n"
                "1️⃣ Прыжки на месте — 60 секунд\n"
                "2️⃣ Круговые вращения руками и ногами — 60 секунд\n"
                "3️⃣ Приседания без веса — 15 повторений\n"
                "4️⃣ Наклоны в стороны — 20 повторений\n"
                "5️⃣ Планка — 30 секунд\n"
            ),
            3: (
                "🟡 *РАЗМИНКА (5 минут)*\nНачнём шаг за шагом!\n\n"
                "1️⃣ Прыжки на месте — 60 секунд\n"
                "2️⃣ Круговые вращения руками и ногами — 60 секунд\n"
                "3️⃣ Приседания без веса — 15 повторений\n"
                "4️⃣ Наклоны в стороны — 20 повторений\n"
                "5️⃣ Планка — 30 секунд\n"
            ),
            4: (
                "🟡 *РАЗМИНКА (5 минут)*\nНачнём шаг за шагом!\n\n"
                "1️⃣ Прыжки на месте — 60 секунд\n"
                "2️⃣ Круговые вращения руками и ногами — 60 секунд\n"
                "3️⃣ Приседания без веса — 15 повторений\n"
                "4️⃣ Наклоны в стороны — 20 повторений\n"
                "5️⃣ Планка — 30 секунд\n"
            )
        }
        
        text = warmup_texts.get(day, "Разминка для этого дня не задана.")
        await query.message.reply_text(text, parse_mode="Markdown")

        # Отправляем первый шаг разминки с кнопками
        await send_next_warmup_step(day, query.message.chat_id, context)




async def handle_warmup_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # callback_data: разминка{day}_шаг_{index}_{action}
    data = query.data
    parts = data.split("_")

    # Извлекаем номер дня из первой части
    day_part = parts[0]  # 'разминка1', 'разминка2' и т.д.
    day = int(day_part.replace("разминка", ""))

    step_index = int(parts[2])
    action = parts[3]
    chat_id = query.message.chat_id

    # Получаем список разминки для нужного дня
    warmup_lists = {
        1: warmup_steps_day1,
        2: warmup_steps_day2,
        3: warmup_steps_day3,
        4: warmup_steps_day4,
    }

    warmup_steps_for_day = warmup_lists.get(day)
    if not warmup_steps_for_day:
        await query.message.reply_text("⚠️ Разминка для этого дня не найдена.")
        return

    step = warmup_steps_for_day[step_index]

    if action == "старт":
        msg_timer_start = await query.message.reply_text(f"⏱ {step['name']} — таймер {step.get('duration', 0)} сек начат!")
        await asyncio.sleep(step.get('duration', 0))
        msg_timer_end = await query.message.reply_text(f"✅ {step['name']} завершено!")

        context.user_data["warmup_message_ids"] = [
            query.message.message_id,
            msg_timer_start.message_id,
            msg_timer_end.message_id
        ]
        context.user_data["was_started"] = True

    elif action == "готово":
        msg_done = await query.message.reply_text(f"✅ {step['name']} отмечено как выполнено.")
        await asyncio.sleep(2)

        message_ids = context.user_data.get("warmup_message_ids", [])
        message_ids.append(msg_done.message_id)
        message_ids.append(query.message.message_id)

        try:
            if context.user_data.get("was_started"):
                for msg_id in message_ids[-4:]:
                    await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            else:
                for msg_id in message_ids[-2:]:
                    await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

        context.user_data["was_started"] = False
        context.user_data["warmup_message_ids"] = []

        # Увеличиваем индекс разминки и отправляем следующий шаг
        key = f"warmup_index_day{day}"
        index = context.user_data.get(key, 0) + 1
        context.user_data[key] = index

        if index >= len(warmup_steps_for_day):
            # Разминка закончена, переходим к основной тренировке
            await start_main_workout(day, chat_id, context)
        else:
            # Отправляем следующий шаг разминки
            await send_next_warmup_step(day, chat_id, context)

async def send_next_warmup_step(day: int, chat_id, context):
    warmup_lists = {
        1: warmup_steps_day1,
        2: warmup_steps_day2,
        3: warmup_steps_day3,
        4: warmup_steps_day4,
    }

    warmup_steps_for_day = warmup_lists.get(day)
    if not warmup_steps_for_day:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Разминка для этого дня не найдена.")
        return

    index = context.user_data.get(f"warmup_index_day{day}", 0)

    if index >= len(warmup_steps_for_day):
        # Разминка завершена, переходим к основной тренировке
        await start_main_workout(day, chat_id, context)
        return

    step = warmup_steps_for_day[index]
    text = f"*{step['name']}*\n"
    text += f"⏱ {step['duration']} сек" if step["type"] == "time" else f"🔁 {step['reps']} раз"

    buttons = [
        [
            InlineKeyboardButton("▶️ Я начал", callback_data=f"разминка{day}_шаг_{index}_старт"),
            InlineKeyboardButton("✅ Я сделал", callback_data=f"разминка{day}_шаг_{index}_готово")
        ]
    ]

    message = await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )

    context.user_data["warmup_message_ids"] = [message.message_id]

async def start_main_workout(day, chat_id, context):
    main_workout = {
        1: (
            "🎉 Разминка завершена! Переходим к основной тренировке...\n\n"
            "💥 *ДЕНЬ 1 — Грудь, руки, пресс*\n\n"
            "• Отжимания от пола — 3×максимум\n"
            "• Отжимания с узкой постановкой — 3×10\n"
            "• Гантели вверх лёжа на полу — 3×12\n"
            "• Подъём гантелей на бицепс — 3×15\n"
            "• Скручивания на пресс — 3×20\n"
            "• Планка — 3×30 сек"
        ),
        2: (
            "🎉 Разминка завершена! Переходим к основной тренировке...\n\n"
            "🍑 *ДЕНЬ 2 — Ягодицы, ноги, пресс*\n\n"
            "• Приседания с гантелями — 3×15\n"
            "• Выпады вперёд (каждая нога) — 3×12\n"
            "• Ягодичный мостик с весом — 3×15\n"
            "• Подъём ног лёжа (пресс) — 3×20\n"
            "• Скручивания — 3×20\n"
            "• Планка боковая (левая + правая) — по 30 сек"
        ),
        3: (
            "🎉 Разминка завершена! Переходим к основной тренировке...\n\n"
            "🦾 *ДЕНЬ 3 — Спина, плечи, пресс*\n\n"
            "• Подтягивания — 3×максимум\n"
            "• Тяга гантелей в наклоне — 3×12\n"
            "• Разводка гантелей в стороны — 3×12\n"
            "• \"Супермен\" лёжа — 3×20\n"
            "• Планка с подъёмом ноги — 3×30 сек\n"
            "• Скручивания с руками вверх — 3×20"
        ),
        4: (
            "🎉 Разминка завершена! Переходим к основной тренировке...\n\n"
            "⚡ *ДЕНЬ 4 — Кардио и добивка*\n\n"
            "• Бёрпи — 3×10\n"
            "• Прыжки с разведением ног — 3×20\n"
            "• Отжимания на максимум — 3×макс\n"
            "• Скручивания на пресс — 3×20\n"
            "• Планка — 3×1 мин"
        )
    }

    text = main_workout.get(day, "Основная тренировка не найдена.")
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
    context.user_data[f"main_index_day{day}"] = 0
    await send_next_main_step(day, chat_id, context)





async def handle_main_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # callback_data: тренировка{day}_шаг_{index}_{action}
    data = query.data
    parts = data.split("_")

    day_part = parts[0]  # 'тренировка1', 'тренировка2' и т.д.
    day = int(day_part.replace("тренировка", ""))

    step_index = int(parts[2])
    action = parts[3]
    chat_id = query.message.chat_id

    main_workouts = {
        1: main_workout_day1,
        2: main_workout_day2,
        3: main_workout_day3,
        4: main_workout_day4,
    }

    workout_for_day = main_workouts.get(day)
    if not workout_for_day:
        await query.message.reply_text("⚠️ Тренировка для этого дня не найдена.")
        return

    step = workout_for_day[step_index]

    if action == "старт":
        if step.get("type") == "time":
            msg_start = await query.message.reply_text(f"⏱ {step['name']} — таймер {step['duration']} сек начат!")
            await asyncio.sleep(step['duration'])
            msg_end = await query.message.reply_text(f"✅ {step['name']} завершено!")
            context.user_data["main_message_ids"] = [
                query.message.message_id,
                msg_start.message_id,
                msg_end.message_id,
            ]
        else:
            context.user_data["main_message_ids"] = [query.message.message_id]
        context.user_data["main_started"] = True

    elif action == "готово":
        msg_done = await query.message.reply_text(f"✅ {step['name']} отмечено как выполнено.")
        await asyncio.sleep(2)

        message_ids = context.user_data.get("main_message_ids", [])
        message_ids.append(msg_done.message_id)
        message_ids.append(query.message.message_id)

        try:
            if context.user_data.get("main_started"):
                for msg_id in message_ids[-4:]:
                    await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            else:
                for msg_id in message_ids[-2:]:
                    await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

        context.user_data["main_started"] = False
        context.user_data["main_message_ids"] = []

        key = f"main_index_day{day}"
        index = context.user_data.get(key, 0) + 1
        context.user_data[key] = index

        if index >= len(workout_for_day):
            await context.bot.send_message(chat_id=chat_id, text=f"🎉 Основная тренировка Дня {day} завершена! Отличная работа! 💪")
            return

        await send_next_main_step(day, chat_id, context)


async def send_next_main_step(day: int, chat_id, context):
    main_workouts = {
        1: main_workout_day1,
        2: main_workout_day2,
        3: main_workout_day3,
        4: main_workout_day4,
    }

    workout_for_day = main_workouts.get(day)
    if workout_for_day is None:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Тренировка для этого дня не найдена.")
        return

    index = context.user_data.get(f"main_index_day{day}", 0)
    if index >= len(workout_for_day):
        return

    step = workout_for_day[index]

    text = f"*{step['name']}*\n"
    if step.get("type") == "time":
        text += f"⏱ {step['sets']}×{step['duration']} сек"
    else:
        text += f"🔁 {step['reps']}"

    buttons = [
        [
            InlineKeyboardButton("▶️ Я начал", callback_data=f"тренировка{day}_шаг_{index}_старт"),
            InlineKeyboardButton("✅ Я сделал", callback_data=f"тренировка{day}_шаг_{index}_готово"),
        ]
    ]

    message = await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown",
    )

    context.user_data["main_message_ids"] = [message.message_id]










###################################################################################################################3
main_workout_day1 = [
    {"name": "Отжимания от пола", "reps": "3×максимум"},
    {"name": "Отжимания с узкой постановкой", "reps": "3×10"},
    {"name": "Гантели вверх лёжа на полу", "reps": "3×12"},
    {"name": "Подъём гантелей на бицепс", "reps": "3×15"},
    {"name": "Скручивания на пресс", "reps": "3×20"},
    {"name": "Планка", "duration": 30, "type": "time", "sets": 3}
]

warmup_steps_day1 = [
    {"name": "Круговые вращения руками вперёд", "duration": 15, "type": "time"},
    {"name": "Круговые вращения руками назад", "duration": 15, "type": "time"},
    {"name": "Плечевые круги и махи руками", "duration": 30, "type": "time"},
    {"name": "Прыжки на месте", "duration": 30, "type": "time"},
    {"name": "Лёгкие отжимания от пола", "reps": 10, "type": "reps"},
    {"name": "Подъём гантелей на бицепс (разогрев)", "reps": 10, "type": "reps"},
    {"name": "Скручивания на пресс", "reps": 15, "type": "reps"},
    {"name": "Планка", "duration": 30, "type": "time"}
]
async def handle_day1_workout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["warmup_index"] = 0
    context.user_data["main_index"] = 0
    context.user_data["warmup_message_ids"] = []
    context.user_data["main_message_ids"] = []

    await query.message.reply_text(
        "🟡 *РАЗМИНКА (5 минут)*\nНачнём шаг за шагом!\n\n"
        "1️⃣ Круговые вращения руками вперёд — 15 секунд\n"
        "2️⃣ Круговые вращения руками назад — 15 секунд\n"
        "3️⃣ Плечевые круги и махи руками — 30 секунд\n"
        "4️⃣ Прыжки на месте — 30 секунд\n"
        "5️⃣ Лёгкие отжимания от пола — 10 повторений\n"
        "6️⃣ Подъём гантелей на бицепс (разогрев) — 10 повторений\n"
        "7️⃣ Скручивания на пресс — 15 повторений\n"
        "8️⃣ Планка — 30 секунд\n",
        parse_mode="Markdown"
    )
    await send_next_warmup_step_day1(query.message.chat_id, context)


async def send_next_warmup_step_day1(chat_id, context):
    index = context.user_data.get("warmup_index", 0)

    if index >= len(warmup_steps_day1):
        await context.bot.send_message(chat_id=chat_id,
            text=(
                "🎉 Разминка завершена! Переходим к основной тренировке...\n\n"
                "💥 *ДЕНЬ 1 — Грудь, руки, пресс*\n\n"
                "• Отжимания от пола — 3×максимум\n"
                "• Отжимания с узкой постановкой — 3×10\n"
                "• Гантели вверх лёжа на полу — 3×12\n"
                "• Подъём гантелей на бицепс — 3×15\n"
                "• Скручивания на пресс — 3×20\n"
                "• Планка — 3×30 сек"
            ),
            parse_mode="Markdown"
        )
        context.user_data["main_index"] = 0
        await send_next_main_step_day1(chat_id, context)
        return

    step = warmup_steps_day1[index]
    text = f"*{step['name']}*\n"
    text += f"⏱ {step['duration']} сек" if step["type"] == "time" else f"🔁 {step['reps']} раз"

    buttons = [
        [
            InlineKeyboardButton("▶️ Я начал", callback_data=f"разминка1_шаг_{index}_старт"),
            InlineKeyboardButton("✅ Я сделал", callback_data=f"разминка1_шаг_{index}_готово")
        ]
    ]

    message = await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )

    context.user_data["warmup_message_ids"] = [message.message_id]


async def send_next_main_step_day1(chat_id, context):
    index = context.user_data.get("main_index", 0)

    if index >= len(main_workout_day1):
        await context.bot.send_message(chat_id=chat_id, text="🎉 Основная тренировка Дня 1 завершена! Отлично поработал! 💪")
        return

    step = main_workout_day1[index]
    text = f"*{step['name']}*\n"

    if step.get("type") == "time":
        text += f"⏱ {step['sets']}×{step['duration']} сек"
    else:
        text += f"🔁 {step['reps']}"

    buttons = [
        [
            InlineKeyboardButton("▶️ Я начал", callback_data=f"тренировка1_шаг_{index}_старт"),
            InlineKeyboardButton("✅ Я сделал", callback_data=f"тренировка1_шаг_{index}_готово")
        ]
    ]

    message = await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )

    context.user_data["main_message_ids"] = [message.message_id]




############################################################################################################################
main_workout_day2 = [
    {"name": "Приседания с гантелями", "reps": "3×15"},
    {"name": "Выпады вперёд (каждая нога)", "reps": "3×12"},
    {"name": "Ягодичный мостик с весом", "reps": "3×15"},
    {"name": "Подъём ног лёжа (пресс)", "reps": "3×20"},
    {"name": "Скручивания", "reps": "3×20"},
    {"name": "Планка боковая (левая + правая)", "duration": 30, "type": "time", "sets": 2}  # по 30 сек на каждую сторону
]

warmup_steps_day2 = [
    {"name": "Прыжки на месте", "duration": 60, "type": "time"},
    {"name": "Круговые вращения руками и ногами", "duration": 60, "type": "time"},
    {"name": "Приседания без веса", "reps": 15, "type": "reps"},
    {"name": "Наклоны в стороны", "reps": 20, "type": "reps"},
    {"name": "Планка", "duration": 30, "type": "time"}
]

# Запуск разминки и основной тренировки Дня 2
async def handle_day2_workout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["warmup_index"] = 0
    context.user_data["main_index"] = 0
    context.user_data["warmup_message_ids"] = []
    context.user_data["main_message_ids"] = []

    await query.message.reply_text(
        "🟡 *РАЗМИНКА (5 минут)*\nНачнём шаг за шагом!\n\n"
        "1️⃣ Прыжки на месте — 60 секунд\n"
        "2️⃣ Круговые вращения руками и ногами — 60 секунд\n"
        "3️⃣ Приседания без веса — 15 повторений\n"
        "4️⃣ Наклоны в стороны — 20 повторений\n"
        "5️⃣ Планка — 30 секунд\n",
        parse_mode="Markdown"
    )
    await send_next_warmup_step_day2(query.message.chat_id, context)

# Отправка следующего шага разминки Дня 2
async def send_next_warmup_step_day2(chat_id, context):
    index = context.user_data.get("warmup_index", 0)

    if index >= len(warmup_steps_day2):
        await context.bot.send_message(chat_id=chat_id,
            text=(
                "🎉 Разминка завершена! Переходим к основной тренировке...\n\n"
                "🍑 *ДЕНЬ 2 — Ягодицы, ноги, пресс*\n\n"
                "• Приседания с гантелями — 3×15\n"
                "• Выпады вперёд (каждая нога) — 3×12\n"
                "• Ягодичный мостик с весом — 3×15\n"
                "• Подъём ног лёжа (пресс) — 3×20\n"
                "• Скручивания — 3×20\n"
                "• Планка боковая (левая + правая) — по 30 сек"
            ),
            parse_mode="Markdown"
        )
        context.user_data["main_index"] = 0
        await send_next_main_step_day2(chat_id, context)
        return

    step = warmup_steps_day2[index]

    text = f"*{step['name']}*\n"
    text += f"⏱ {step['duration']} сек" if step["type"] == "time" else f"🔁 {step['reps']} раз"

    buttons = [
        [
            InlineKeyboardButton("▶️ Я начал", callback_data=f"разминка2_шаг_{index}_старт"),
            InlineKeyboardButton("✅ Я сделал", callback_data=f"разминка2_шаг_{index}_готово")
        ]
    ]

    message = await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )

    context.user_data["warmup_message_ids"] = [message.message_id]

# Отправка следующего шага основной тренировки Дня 2
async def send_next_main_step_day2(chat_id, context):
    index = context.user_data.get("main_index", 0)

    if index >= len(main_workout_day2):
        await context.bot.send_message(chat_id=chat_id, text="🎉 Основная тренировка Дня 2 завершена! Отличная работа! 💪")
        return

    step = main_workout_day2[index]
    text = f"*{step['name']}*\n"

    if step.get("type") == "time":
        text += f"⏱ {step['sets']}×{step['duration']} сек"
    else:
        text += f"🔁 {step['reps']}"

    buttons = [
        [
            InlineKeyboardButton("▶️ Я начал", callback_data=f"тренировка2_шаг_{index}_старт"),
            InlineKeyboardButton("✅ Я сделал", callback_data=f"тренировка2_шаг_{index}_готово")
        ]
    ]

    message = await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )

    context.user_data["main_message_ids"] = [message.message_id]
############################################################################################################################

main_workout_day3 = [
    {"name": "Подтягивания", "reps": "3×максимум"},
    {"name": "Тяга гантелей в наклоне", "reps": "3×12"},
    {"name": "Разводка гантелей в стороны", "reps": "3×12"},
    {"name": "\"Супермен\" лёжа", "reps": "3×20"},
    {"name": "Планка с подъёмом ноги", "duration": 30, "type": "time", "sets": 3},
    {"name": "Скручивания с руками вверх", "reps": "3×20"}
]

warmup_steps_day3 = [
    {"name": "Прыжки на месте", "duration": 60, "type": "time"},
    {"name": "Круговые вращения руками и ногами", "duration": 60, "type": "time"},
    {"name": "Приседания без веса", "reps": 15, "type": "reps"},
    {"name": "Наклоны в стороны", "reps": 20, "type": "reps"},
    {"name": "Планка", "duration": 30, "type": "time"}
]

async def handle_day3_workout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["warmup_index"] = 0
    context.user_data["main_index"] = 0
    context.user_data["warmup_message_ids"] = []
    context.user_data["main_message_ids"] = []

    await query.message.reply_text(
        "🟡 *РАЗМИНКА (5 минут)*\nНачнём шаг за шагом!\n\n"
        "1️⃣ Прыжки на месте — 60 секунд\n"
        "2️⃣ Круговые вращения руками и ногами — 60 секунд\n"
        "3️⃣ Приседания без веса — 15 повторений\n"
        "4️⃣ Наклоны в стороны — 20 повторений\n"
        "5️⃣ Планка — 30 секунд\n",
        parse_mode="Markdown"
    )
    await send_next_warmup_step_day3(query.message.chat_id, context)

async def send_next_warmup_step_day3(chat_id, context):
    index = context.user_data.get("warmup_index", 0)

    if index >= len(warmup_steps_day3):
        await context.bot.send_message(chat_id=chat_id,
            text=(
                "🎉 Разминка завершена! Переходим к основной тренировке...\n\n"
                "🦾 *ДЕНЬ 3 — Спина, плечи, пресс*\n\n"
                "• Подтягивания — 3×максимум\n"
                "• Тяга гантелей в наклоне — 3×12\n"
                "• Разводка гантелей в стороны — 3×12\n"
                "• \"Супермен\" лёжа — 3×20\n"
                "• Планка с подъёмом ноги — 3×30 сек\n"
                "• Скручивания с руками вверх — 3×20"
            ),
            parse_mode="Markdown"
        )
        context.user_data["main_index"] = 0
        await send_next_main_step_day3(chat_id, context)
        return

    step = warmup_steps_day3[index]
    text = f"*{step['name']}*\n"
    text += f"⏱ {step['duration']} сек" if step["type"] == "time" else f"🔁 {step['reps']} раз"

    buttons = [
        [
            InlineKeyboardButton("▶️ Я начал", callback_data=f"разминка3_шаг_{index}_старт"),
            InlineKeyboardButton("✅ Я сделал", callback_data=f"разминка3_шаг_{index}_готово")
        ]
    ]

    message = await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )

    context.user_data["warmup_message_ids"] = [message.message_id]

async def send_next_main_step_day3(chat_id, context):
    index = context.user_data.get("main_index", 0)

    if index >= len(main_workout_day3):
        await context.bot.send_message(chat_id=chat_id, text="🎉 Основная тренировка Дня 3 завершена! Молодец, зверюга! 🐺")
        return

    step = main_workout_day3[index]
    text = f"*{step['name']}*\n"

    if step.get("type") == "time":
        text += f"⏱ {step['sets']}×{step['duration']} сек"
    else:
        text += f"🔁 {step['reps']}"

    buttons = [
        [
            InlineKeyboardButton("▶️ Я начал", callback_data=f"тренировка3_шаг_{index}_старт"),
            InlineKeyboardButton("✅ Я сделал", callback_data=f"тренировка3_шаг_{index}_готово")
        ]
    ]

    message = await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )

    context.user_data["main_message_ids"] = [message.message_id]

############################################################################################################################
main_workout_day4 = [
    {"name": "Бёрпи", "reps": "3×10"},
    {"name": "Прыжки с разведением ног", "reps": "3×20"},
    {"name": "Отжимания на максимум", "reps": "3×макс"},
    {"name": "Скручивания на пресс", "reps": "3×20"},
    {"name": "Планка", "duration": 60, "type": "time", "sets": 3}
]

warmup_steps_day4 = [
    {"name": "Прыжки на месте", "duration": 60, "type": "time"},
    {"name": "Круговые вращения руками и ногами", "duration": 60, "type": "time"},
    {"name": "Приседания без веса", "reps": 15, "type": "reps"},
    {"name": "Наклоны в стороны", "reps": 20, "type": "reps"},
    {"name": "Планка", "duration": 30, "type": "time"}
]

async def handle_day4_workout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["warmup_index"] = 0
    context.user_data["main_index"] = 0
    context.user_data["warmup_message_ids"] = []
    context.user_data["main_message_ids"] = []

    await query.message.reply_text(
        "🟡 *РАЗМИНКА (5 минут)*\nНачнём шаг за шагом!\n\n"
        "1️⃣ Прыжки на месте — 60 секунд\n"
        "2️⃣ Круговые вращения руками и ногами — 60 секунд\n"
        "3️⃣ Приседания без веса — 15 повторений\n"
        "4️⃣ Наклоны в стороны — 20 повторений\n"
        "5️⃣ Планка — 30 секунд\n",
        parse_mode="Markdown"
    )
    await send_next_warmup_step_day4(query.message.chat_id, context)

async def send_next_warmup_step_day4(chat_id, context):
    index = context.user_data.get("warmup_index", 0)

    if index >= len(warmup_steps_day4):
        await context.bot.send_message(chat_id=chat_id,
            text=(
                "🎉 Разминка завершена! Переходим к основной тренировке...\n\n"
                "⚡ *ДЕНЬ 4 — Кардио и добивка*\n\n"
                "• Бёрпи — 3×10\n"
                "• Прыжки с разведением ног — 3×20\n"
                "• Отжимания на максимум — 3×макс\n"
                "• Скручивания на пресс — 3×20\n"
                "• Планка — 3×1 мин"
            ),
            parse_mode="Markdown"
        )
        context.user_data["main_index"] = 0
        await send_next_main_step_day4(chat_id, context)
        return

    step = warmup_steps_day4[index]
    text = f"*{step['name']}*\n"
    text += f"⏱ {step['duration']} сек" if step["type"] == "time" else f"🔁 {step['reps']} раз"

    buttons = [
        [
            InlineKeyboardButton("▶️ Я начал", callback_data=f"разминка4_шаг_{index}_старт"),
            InlineKeyboardButton("✅ Я сделал", callback_data=f"разминка4_шаг_{index}_готово")
        ]
    ]

    message = await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )

    context.user_data["warmup_message_ids"] = [message.message_id]



async def send_next_main_step_day4(chat_id, context):
    index = context.user_data.get("main_index", 0)

    if index >= len(main_workout_day4):
        await context.bot.send_message(chat_id=chat_id, text="🎉 День 4 завершён! Ты монстр! 🧨 Отдых заслужен.")
        return

    step = main_workout_day4[index]
    text = f"*{step['name']}*\n"

    if step.get("type") == "time":
        text += f"⏱ {step['sets']}×{step['duration']} сек"
    else:
        text += f"🔁 {step['reps']}"

    buttons = [
        [
            InlineKeyboardButton("▶️ Я начал", callback_data=f"тренировка4_шаг_{index}_старт"),
            InlineKeyboardButton("✅ Я сделал", callback_data=f"тренировка4_шаг_{index}_готово")
        ]
    ]

    message = await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )

    context.user_data["main_message_ids"] = [message.message_id]





############################################################################################################################


async def random_skuki(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Выбираем случайный арсенал
    arsenal_name = random.choice(list(arsenals.keys()))
    task = random.choice(arsenals[arsenal_name])
    await update.message.reply_text(f"Вот тебе случайная идея из арсенала - \n**{arsenal_name}**:")
    await update.message.reply_text(f"{task}")

async def random_zaryadki(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arsenal_name = random.choice(list(arsenals_зарядок.keys()))
    task = random.choice(arsenals_зарядок[arsenal_name])
    await update.message.reply_text(f"Вот тебе случайная зарядка ДЕЙСТВУЙ - \n**{arsenal_name}**:")
    await update.message.reply_text(task)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой тренировочный бот 💪")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Я могу помочь тебе с тренировками!\n\n"
        "Команды:\n"
        "/start - Запустить бота\n"
        "/help - Показать это сообщение\n"
        "/go - Начать разговор с ИИ\n"
        "/exit - Выйти из режима разговора\n"
    )
    await update.message.reply_text(help_text)

async def set_commands(application):
    commands = [
    BotCommand("start", "Запустить бота"),
    BotCommand("training", "Выбрать/начать тренировку"),
    BotCommand("help", "Помощь"),
    BotCommand("go", "Начать разговор"),
    BotCommand("exit", "Выйти из разговора"),
    BotCommand("random_skuki", "Получить случайную идею для занятия"),
    BotCommand("random_zaryadki", "Получить случайную зарядку")
]
    await application.bot.set_my_commands(commands)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    if user_id in chat_users:
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ты ведешь себя как друг и товарищ. Приводишь примеры для лучшего объяснения"},
                    {"role": "user", "content": user_message}
                ]
            )

            reply = response.choices[0].message.content
            await update.message.reply_text(reply)
            
        except Exception as e:
            logging.error(f"Ошибка OpenAI API: {e}")
            await update.message.reply_text("Извини, возникла ошибка при обработке запроса.")
    else:
        await update.message.reply_text(f"Ты написал: {user_message}")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Извини, я не знаю такой команды.")

async def go(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_users.add(user_id)
    await update.message.reply_text("🧠 Ты вошёл в режим общения с ИИ. Пиши что угодно!\n\nНапиши /exit чтобы выйти.")

async def exit_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in chat_users:
        chat_users.remove(user_id)
        await update.message.reply_text("✅ Ты вышел из режима общения с ИИ.")
    else:
        await update.message.reply_text("Ты и так не в режиме общения с ИИ.")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("go", go))
    app.add_handler(CommandHandler("exit", exit_chat))
    app.add_handler(CommandHandler("random_skuki", random_skuki))
    app.add_handler(CommandHandler("random_zaryadki", random_zaryadki))
    app.add_handler(CommandHandler("training", start_training_menu))

    app.add_handler(CallbackQueryHandler(handle_day1_workout, pattern='^тренировка_день1$'))
    app.add_handler(CallbackQueryHandler(handle_day2_workout, pattern='^тренировка_день2$'))
    app.add_handler(CallbackQueryHandler(handle_day3_workout, pattern='^тренировка_день3$'))
    app.add_handler(CallbackQueryHandler(handle_day4_workout, pattern='^тренировка_день4$'))
    app.add_handler(CallbackQueryHandler(handle_warmup_step, pattern=r'^разминка_шаг_\d+_(старт|готово)$'))
    app.add_handler(CallbackQueryHandler(handle_training_day_selection, pattern=r"^тренировка[1-4]$"))
    app.add_handler(CallbackQueryHandler(handle_warmup_step, pattern=r"^разминка[1-4]_шаг_\d+_(старт|готово)$"))
    app.add_handler(CallbackQueryHandler(handle_main_step, pattern=r"^тренировка[1-4]_шаг_\d+_(старт|готово)$"))





    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    await set_commands(app)

    print("Бот запущен локально через polling...")
    # await app.run_polling()

    await app.run_webhook(
        listen="0.0.0.0",  # Привязка к всем адресам
        port=int(os.getenv("PORT", 5000)),  # Порт для прослушивания
        url_path=TOKEN,  # Путь к токену в URL
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}",  # Вебхук URL
    )

if __name__ == "__main__":
    asyncio.run(main())
