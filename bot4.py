import nest_asyncio
nest_asyncio.apply()
import random
import asyncio
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
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
    BotCommand("help", "Помощь"),
    BotCommand("go", "Начать разговор"),
    BotCommand("exit", "Выйти из разговора"),
    BotCommand("random_skuki", "Получить случайную идею для занятия"),
    BotCommand("random_zaryadki", "Получить случайную зарядку"),
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

            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens

            # Цена: $0.15 за 1000 токенов → 0.00015 за 1 токен
            price_per_token = 0.15 / 1000
            cost = total_tokens * price_per_token

            await update.message.reply_text(reply)
            await update.message.reply_text(
                f"🔢 Использовано токенов:\n"
                f"📥 Ввод: {prompt_tokens}\n"
                f"📤 Ответ: {completion_tokens}\n"
                f"💡 Всего: {total_tokens}\n\n"
                f"💰 Стоимость запроса: ${cost:.6f}"
            )
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


    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    await set_commands(app)

    print("Бот запущен...")
    await app.run_webhook(
        listen="0.0.0.0",  # Привязка к всем адресам
        port=int(os.getenv("PORT", 5000)),  # Порт для прослушивания
        url_path=TOKEN,  # Путь к токену в URL
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}",  # Вебхук URL
    )

if __name__ == "__main__":
    asyncio.run(main())
