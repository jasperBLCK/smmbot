import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    TokenBasedRequestHandler,
    setup_application,
)
from aiohttp import web

from core.config import config
from core.handlers import StartCommand, SendAllAdmin, ReferralLink, Parsing, ListOrders, Help, FAQ, CreateAnOrder, \
    Check, admin, AdmibGetAllOrders, AddOrRemoveCategory, Balance, CreateBot, Inline_Query, AdminGetService
from finite_state_machine import form_router

main_router = Router()


async def on_startup(bot: Bot):
    await bot.set_webhook(config.MAIN_BOT_URL)


def build_dispatcher(storage: MemoryStorage) -> Dispatcher:
    dispatcher = Dispatcher(storage=storage)
    dispatcher.include_routers(StartCommand.StartRouter, AddOrRemoveCategory.AddOrRemoveCategoryRouter,
                               AdmibGetAllOrders.AdminAllOrders, admin.AdminRouter,
                               Check.CheckRouter, CreateAnOrder.OrderRouter, CreateBot.NewBotRouter,
                               FAQ.FAQRouter, Help.HelpRouter, Inline_Query.QueryRouter,
                               ListOrders.ListOrders, Parsing.ParsingRouter, ReferralLink.ReferralRouter,
                               SendAllAdmin.SendAllRouter, AdminGetService.AdminGetServiceRouter,
                               Balance.BalanceRouter, main_router)
    return dispatcher


def run_webhook(bot: Bot, bot_settings: dict, storage: MemoryStorage):
    main_dispatcher = build_dispatcher(storage)
    main_dispatcher.startup.register(on_startup)

    multibot_dispatcher = Dispatcher(storage=storage)
    multibot_dispatcher.include_router(form_router)

    app = web.Application()
    SimpleRequestHandler(dispatcher=main_dispatcher, bot=bot).register(app, path=config.MAIN_BOT_PATH)
    TokenBasedRequestHandler(
        dispatcher=main_dispatcher,
        bot_settings=bot_settings,
    ).register(app, path=config.OTHER_BOTS_PATH)

    setup_application(app, main_dispatcher, bot=bot)
    setup_application(app, multibot_dispatcher)

    web.run_app(app, host=config.WEB_SERVER_HOST, port=config.WEB_SERVER_PORT)


async def run_polling(bot: Bot, storage: MemoryStorage):
    dispatcher = build_dispatcher(storage)
    await bot.delete_webhook(drop_pending_updates=False)
    await dispatcher.start_polling(bot)


def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    if not config.TOKEN:
        sys.exit('TOKEN is not set (see .env.example)')

    bot_settings = {
        "session": AiohttpSession(),
        "default": DefaultBotProperties(parse_mode=ParseMode.HTML),
    }
    bot = Bot(token=config.TOKEN, **bot_settings)
    storage = MemoryStorage()

    if config.BASE_URL:
        run_webhook(bot, bot_settings, storage)
    else:
        logging.info("BOT_URL is not set, starting in polling mode")
        asyncio.run(run_polling(bot, storage))


if __name__ == "__main__":
    main()
