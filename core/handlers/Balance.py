# Обработка баланса
import os
from aiogram.filters import StateFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from aiogram.types import Message, CallbackQuery
from aiogram import F
from core.keyboards import Button
from core.config import config
import database as db
from urllib.parse import urlencode
import uuid
import requests
import json
import time
import hmac
import hashlib
from aiogram import Bot, Router

# Глобальные переменные для получения и обновления баланса
Sum = 0.0
order_id = ''
user_id = 0

BalanceRouter = Router()

# Создаем FSM
class FSMFillFrom(StatesGroup):
    ReplenishBalance = State()


# Обработка команды
@BalanceRouter.message(Command('mybalance'))
async def MyBalanceKeyboard(message: Message, state: FSMContext):
    # Вызов главное функции
    await MyBalance(message, state)


# Обработка кнопки Мой Баланс
@BalanceRouter.message(F.text == '🏦Мой баланс')
async def MyBalance(message: Message, state: FSMContext):
    # Получаем баланс из бд с помощью id
    balance = await db.GetBalance(message.from_user.id)
    text = f'Ваш баланс: {balance[0]} руб.\n' \
           '💳 Вы можете пополнить баланс, указав сумму пополнения в рублях:'
    # Используем FSM
    await message.answer(text)
    await state.set_state(FSMFillFrom.ReplenishBalance)


# Обработка FSM для пополнения баланса
@BalanceRouter.message(StateFilter(FSMFillFrom.ReplenishBalance))
async def ReplenishBalance(message: Message, state: FSMContext):
    global Sum
    if message.text.isdigit() is True:
        Sum = float(message.text)
        Shopped = str(os.getenv('SHOPID'))
        SecretKey = str(os.getenv('SECRETKEY'))
        global order_id, user_id
        order_id = uuid.uuid4()
        user_id = message.from_user.id
        print(order_id)
        data = {
            'shop_id': Shopped,
            'amount': Sum,
            'currency': 'RUB',
            'order_id': order_id,
            'test': 1
        }
        sorted_data = sorted(data.items())
        data_string = urlencode(sorted_data)
        sign = hashlib.md5((data_string + SecretKey).encode()).hexdigest()
        PayUrl = f'https://tegro.money/pay/?{data_string}&sign={sign}'
        await message.answer('Выберите способ оплаты', reply_markup=await Button.TegroPay(PayUrl))
        await message.answer('Проверить оплату', reply_markup=Button.CheckPay)
        await message.answer('Если хотите отменить нажмите на кнопку в меню⤵️ ', reply_markup=Button.BackMainKeyboard)
    else:
        await state.clear()


# Обработка кнопки для проверки оплаты
@BalanceRouter.callback_query(F.data == 'check_pay')
async def CheckPay(callback: CallbackQuery, state: FSMContext):
    # Создаем запрос на Tegro для проверки прошла ли оплата
    api_key = config.TEGRO_API_KEY
    data = {
        'shop_id': str('3FF517A8EF30E24571BDAD4181F24FD0'),
        'nonce': int(time.time()),
        'payment_id': str(order_id)
    }
    body = json.dumps(data)
    sign = hmac.new(api_key.encode(), body.encode(), hashlib.sha256).hexdigest()

    headers = {
        'Authorization': f'Bearer {sign}',
        'Content-Type': 'application/json',
    }

    url = "https://tegro.money/api/order/"
    response = requests.post(url, data=body, headers=headers)

    # Проверяем ответ от Tegro
    textdata = json.loads(response.text)
    status = textdata['data']
    # Если вернули 0, то оплата не прошла
    if not status:
        await callback.message.answer('Транзакции не существует')
    # Если строка не пустая, то проверяем статус
    else:
        status = status['status']
        if status == 1:
            await db.UpdateBalance(user_id, Sum)
            await callback.message.answer('Оплата успешно прошла')
            await callback.message.delete()
        else:
            await callback.message.answer('Оплата не прошла')