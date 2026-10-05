from aiogram.filters.command import Command
from aiogram.types import Message, CallbackQuery
from aiogram import F
from core.keyboards import Button
from core.config import config
import database as db
import requests
import json
from aiogram import Bot, Router

ListOrders = Router()

# Глобальные переменные для вывода всех заказов
MinOrdersList = 0
MaxOrdersList = 12


# Обработка команды мои заказы
@ListOrders.message(Command('myorder'))
async def MyOrderCommand(message: Message):
    await MyOrder(message)


@ListOrders.message(F.text == '📋Мои заказы')
async def MyOrder(message: Message, bot: Bot):
    # Получаем список всех заказов
    OrderList = await db.GetOrders(message.from_user.id)
    text = ''
    # Проверяем что список больше 0
    if len(OrderList) > 0:
        # Проверяем что они не поместятся в одно сообщение
        if len(OrderList) < 13:
            # Перебираем все заказы пользователя и обновляем статусы
            for order in OrderList:
                NameProduct = await db.GetProductName(order[2])
                url = 'https://smmpanel.ru/api/v1'
                data = {
                    'key': '***REMOVED***',
                    'action': 'status',
                    'order': order[8]
                }
                response = requests.post(url, data=data)
                OrderData = json.loads(response.text)
                Status = (OrderData['status'])
                Order_id = (OrderData['order'])
                await db.UpdateOrderStatus(Order_id, Status)
                # Проверяем все возможные статусы
                if Status == 'Pending':
                    text += f'🆕В ожидании {NameProduct} {order[4]}шт {order[5]}RUB\n'
                elif Status == 'In progress':
                    text += f'🔄В работе {NameProduct} {order[4]}шт {order[5]}RUB\n'
                elif Status == 'Processing':
                    text += f'➕Обработка {NameProduct} {order[4]}шт {order[5]}RUB\n'
                elif Status == 'Completed':
                    text += f'☑️Выполнен {NameProduct} {order[4]}шт {order[5]}RUB\n'
                elif Status == 'success':
                    text += f'🆕Новый {NameProduct} {order[4]}шт {order[5]}RUB\n'
                elif Status == 'Partial':
                    text += f'☑️Выполнен частично {NameProduct} {order[4]}шт {order[5]}RUB\n'
                elif Status == 'Canceled':
                    if await db.GetRefundStatus(order[0]) != 1:
                        await db.Refund(order[0])
                        await db.UpdateBalance(message.from_user.id, order[5])
                        Referrals = await db.GetReferral(message.from_user.id)
                        if Referrals is not None:
                            SecondLevelReferral = await db.GetReferral(Referrals)
                            if SecondLevelReferral is not None:
                                ReferralSum = order[5] * 0.04
                                await db.WriteOffTheReferral(SecondLevelReferral, ReferralSum)
                                await db.WriteOffTheBalance(SecondLevelReferral, ReferralSum)
                            ReferralSum = order[5] * 0.12
                            await db.WriteOffTheReferral(Referrals, ReferralSum)
                            await db.WriteOffTheBalance(Referrals, ReferralSum)
                    text += f'❌Отменен {NameProduct} {order[4]}шт {order[5]}RUB\n'
            await message.answer(text)
        # Если заказы не поместятся в одно сообщение
        else:
            # Перебираем по очереди все сообщения
            Status = ''
            for a in range(MinOrdersList, MaxOrdersList):
                if a < len(OrderList):
                    NameProduct = await db.GetProductName(OrderList[a][2])
                    Service = await db.GetServiceCategory(NameProduct[1])
                    if Service == 'SmmPanel':
                        url = 'https://smmpanel.ru/api/v1'
                        data = {
                            'key': '***REMOVED***',
                            'action': 'status',
                            'order': OrderList[a][8]
                        }
                        response = requests.post(url, data=data)
                        OrderData = json.loads(response.text)
                        Status = (OrderData['status'])
                        Order_id = (OrderData['order'])
                        await db.UpdateOrderStatus(Order_id, Status)
                    else:
                        url = 'https://smoservice.media/api/'
                        data = {
                            'user_id': '419104',
                            'api_key': '***REMOVED***',
                            'action': 'check_order',
                            'order_id': OrderList[a][8]
                        }
                        response = requests.post(url, data=data)
                        OrderData = json.loads(response.text)
                        Status = (OrderData['data']['status'])
                        Order_id = (OrderData['data']['order_id'])
                        await db.UpdateOrderStatus(Order_id, Status)
                        print(Status)
                    if Status == 'Pending':
                        text += f'🆕В ожидании {NameProduct[0]} {OrderList[a][4]}шт {OrderList[a][5]}RUB\n'
                    elif Status == 'In progress' or Status == 'Выполняется':
                        text += f'🔄В работе {NameProduct[0]} {OrderList[a][4]}шт {OrderList[a][5]}RUB\n'
                    elif Status == 'Processing':
                        text += f'➕Обработка {NameProduct[0]} {OrderList[a][4]}шт {OrderList[a][5]}RUB\n'
                    elif Status == 'Completed' or Status == 'Завершен':
                        text += f'✅Выполнен {NameProduct[0]} {OrderList[a][4]}шт {OrderList[a][5]}RUB\n'
                    elif Status == 'success':
                        text += f'🆕Новый {NameProduct[0]} {OrderList[a][4]}шт {OrderList[a][5]}RUB\n'
                    elif Status == 'Partial':
                        text += f'☑️Выполнен частично {NameProduct[0]} {OrderList[a][4]}шт {OrderList[a][5]}RUB\n'
                    elif Status == 'Не оплачен':
                        text += f'❌Не оплачен {NameProduct[0]} {OrderList[a][4]}шт {OrderList[a][5]}RUB\n'
                    elif Status == 'Canceled' or Status == 'Отменен':
                        if await db.GetRefundStatus(OrderList[a][0]) != 1:
                            await db.Refund(OrderList[a][0])
                            await db.UpdateBalance(message.from_user.id, OrderList[a][5])
                            Referrals = await db.GetReferral(message.from_user.id)
                            if Referrals is not None:
                                SecondLevelReferral = await db.GetReferral(Referrals)
                                if SecondLevelReferral is not None:
                                    ReferralSum = OrderList[a][5] * 0.04
                                    await db.WriteOffTheReferral(SecondLevelReferral, ReferralSum)
                                    await db.WriteOffTheBalance(SecondLevelReferral, ReferralSum)
                                ReferralSum = OrderList[a][5] * 0.12
                                await db.WriteOffTheReferral(Referrals, ReferralSum)
                                await db.WriteOffTheBalance(Referrals, ReferralSum)
                        text += f'❌Отменен {NameProduct[0]} {OrderList[a][4]}шт {OrderList[a][5]}RUB\n'
            # Делаем защиту в меньшую и большую сторону
            if MinOrdersList >= 0:
                print(MaxOrdersList)
                if MaxOrdersList < 13:
                    await bot.send_message(message.from_user.id, text, reply_markup=Button.OnlyNextOrdersList)
                elif len(OrderList) > MaxOrdersList > 12:
                    await bot.send_message(message.from_user.id, text, reply_markup=Button.NextOrdersList)
                else:
                    await bot.send_message(message.from_user.id, text, reply_markup=Button.BackOrdersList)
    # В противном случае выводим что не заказов
    else:
        await message.answer('У вас нет заказов')


# Если человек хочет перейти на след слайд
@ListOrders.callback_query(F.data == 'NextOrdersList')
async def NoSubCategory(callback: CallbackQuery, bot: Bot):
    global MinOrdersList, MaxOrdersList
    MinOrdersList += 12
    MaxOrdersList += 12
    await callback.message.delete()
    await MyOrder(callback, bot)


# Если человек хочет перейти на прошлый слайд
@ListOrders.callback_query(F.data == 'BackOrderList')
async def NoSubCategory(callback: CallbackQuery, bot: Bot):
    global MinOrdersList, MaxOrdersList
    MinOrdersList -= 12
    MaxOrdersList -= 12
    await callback.message.delete()
    await MyOrder(callback, bot)
