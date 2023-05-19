from lightbulb import BotApp
from shopify import Shopify
from logging import info
from embed import generate_product_embed


async def check_product(bot: BotApp, monitor: dict, product: dict, provider: str):
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
                }
            )

            announce = True
        elif (
            saved_variant["available"] != variant["available"]
            or saved_variant["price"] != variant["price"]
        ):
            info("Changes detected for variant {id}".format(id=variant["id"]))
            bot.d.variants.update(
                {
                    "monitor_id": monitor["id"],
                    "product_id": product["id"],
                    "variant_id": variant["id"],
                    "available": variant["available"],
                    "price": variant["price"],
                },
                ["monitor_id", "product_id", "variant_id"],
            )

            announce = True
        else:
            info("No changes detected for variant {id}".format(id=variant["id"]))

    if announce:
        embed = generate_product_embed(monitor, product, type="new", provider=provider)
        await bot.rest.create_message(monitor["channel_id"], embed=embed)


async def monitor_product(bot: BotApp, monitor: dict):
    product = Shopify.get_product(monitor["url"])
    await check_product(bot, monitor, product, "product")


async def monitor_collection(bot: BotApp, monitor: dict):
    products = Shopify.get_collection(monitor["url"])

    for product in products:
        await check_product(bot, monitor, product, "collection")


async def monitor_search(bot: BotApp, monitor: dict):
    results = Shopify.get_search_results(monitor["url"], monitor["query"])

    for product in results:
        product = Shopify.get_product(product["url"])
        await check_product(bot, monitor, product, "search")
