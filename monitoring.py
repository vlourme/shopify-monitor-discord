from lightbulb import BotApp
from shopify import Shopify
from logging import info
from embed import generate_product_embed
from datetime import datetime


async def check_product(
    bot: BotApp, monitor: dict, product: dict, provider: str
) -> None:
    type = "new"
    announce = False

    for variant in product["variants"]:
        saved_variant = bot.d.variants.find_one(
            monitor_id=monitor["id"], product_id=product["id"], variant_id=variant["id"]
        )

        if saved_variant is None:
            info("New variant detected: {id}".format(id=variant["id"]))
            bot.d.variants.insert(
                {
                    "monitor_id": monitor["id"],
                    "product_id": product["id"],
                    "variant_id": variant["id"],
                    "available": variant["available"],
                    "price": variant["price"],
                    "created_at": datetime.now().timestamp(),
                    "updated_at": datetime.now().timestamp(),
                }
            )

            type = "new"
            announce = True
        elif bool(saved_variant["available"]) != bool(variant["available"]) or float(
            saved_variant["price"]
        ) != float(variant["price"]):
            info("Changes detected for variant {id}".format(id=variant["id"]))
            bot.d.variants.update(
                {
                    "monitor_id": monitor["id"],
                    "product_id": product["id"],
                    "variant_id": variant["id"],
                    "available": variant["available"],
                    "price": variant["price"],
                    "updated_at": datetime.now().timestamp(),
                },
                ["monitor_id", "product_id", "variant_id"],
            )

            type = "update"
            announce = True
        else:
            info("No changes detected for variant {id}".format(id=variant["id"]))

    if announce:
        embed = generate_product_embed(monitor, product, type=type, provider=provider)
        await bot.rest.create_message(monitor["channel_id"], embed=embed)


async def monitor_product(bot: BotApp, monitor: dict) -> None:
    product = Shopify.get_product(monitor["url"])
    await check_product(bot, monitor, product, "product")


async def monitor_collection(bot: BotApp, monitor: dict) -> None:
    products = Shopify.get_collection(monitor["url"])

    for product in products:
        await check_product(bot, monitor, product, "collection")


async def monitor_search(bot: BotApp, monitor: dict) -> None:
    results = Shopify.get_search_results(monitor["url"], monitor["query"])

    for product in results:
        product = Shopify.get_product(product["url"])
        await check_product(bot, monitor, product, "search")
