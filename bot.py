from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from config import Config, load_config
import requests
from bs4 import BeautifulSoup
import base64

config: Config = load_config()
BOT_TOKEN: str = config.tg_bot.token

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
COUNTRY: dict[str, str] = {}

cookies = {
    '_ga_FS4ESHM7K5': 'GS1.1.1701585955.1.0.1701585955.0.0.0',
    '_ga': 'GA1.1.656818498.1701585956',
    'fp': 'b680853072b90216f82e695194b5ee9b',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

s = requests.Session()
list_country = []

response = s.get('http://free-proxy.cz/en/', cookies=cookies, headers=headers)

soup = BeautifulSoup(response.text, "lxml")
countries = soup.find("select", id="frmsearchFilter-country").find_all("option")
for c in countries:
    short_name = c.get("value")
    name = c.text.split("(")[0].strip()
    list_country.append(short_name)
    COUNTRY[short_name] = name

keyboard: list[list[KeyboardButton]] = [
    [KeyboardButton(text=f'{o}')] for o, i in COUNTRY.items()]

my_keyboard = ReplyKeyboardMarkup(
    keyboard=keyboard,
    resize_keyboard=True
)


@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer("Привет:)\nЯ прокси бот:)\nВыбирай строну хлопчик🤪",
                         reply_markup=my_keyboard
                         )


@dp.message()
async def process(message: Message):
    select_country = message.text
    url = f"http://free-proxy.cz/en/proxylist/country/{select_country}/http/ping/all"
    response = s.get(url, cookies=cookies, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        table_trs = soup.find("table", id="proxy_list").find("tbody").find_all("tr")
        count = 0
        for tr in table_trs:

            try:
                ip = tr.find("td").find("script").text
            except Exception as ex:
                print(ex)
                continue

            if ip:
                ip = base64.b64decode(ip.split('"')[1]).decode("utf-8")
                port = tr.find("span").text
                await message.answer(f"{ip} : {port}")
                count += 1
            else:
                continue

        await message.answer(f"[INFO] Собрали {count} прокси. Хорошего дня! ")
    else:
        await message.answer(f"Что-то пошло не так Статус код ответа: {response.status_code} или сделали выбор "
                             f" не с кнопок")


if __name__ == "__main__":
    dp.run_polling(bot)