import asyncio
import os
import dataset
import dotenv
import hikari
import lightbulb
from logging import info
from shopify import Shopify
from monitoring import monitor_product, monitor_collection, monitor_search

dotenv.load_dotenv()

db = dataset.connect("sqlite:///data.db")
bot = lightbulb.BotApp(token=os.getenv("TOKEN"))
bot.d.monitors = db["monitors"]
bot.d.variants = db["variants"]


async def run_background() -> None:
    info("Scraper started.")

    while True:
        for monitor in bot.d.monitors:
            info(
                "Monitoring {type} URL: {url} {query}".format(
                    type=monitor["type"],
                    url=monitor["url"],
                    query=monitor["query"] or "",
                )
            )

            try:
                if monitor["type"] == "product":
                    await monitor_product(bot, monitor)

                if monitor["type"] == "collection":
                    await monitor_collection(bot, monitor)

                if monitor["type"] == "search":
                    await monitor_search(bot, monitor)
            except Exception as e:
                info("Error while monitoring: {error}".format(error=e))

        await asyncio.sleep(int(os.getenv("INTERVAL", 60)))


@bot.listen(hikari.ShardReadyEvent)
async def ready_listener(_):
    info("Bot is ready")
    asyncio.create_task(run_background())


@bot.command()
@lightbulb.option(
    "channel", "Channel to receive alerts", type=hikari.TextableChannel, required=True
)
@lightbulb.option(
    "url", "URL to the product or the collection", type=str, required=True
)
@lightbulb.command(
    "register_monitor", "Enable monitoring for a product or a collection"
)
@lightbulb.implements(lightbulb.SlashCommand)
async def register_monitor(ctx: lightbulb.Context) -> None:
    if not ctx.options.url.startswith(("https://", "http://")):
        await ctx.respond("❌ Invalid URL")
        return

    if Shopify.is_collection(ctx.options.url):
        ctx.bot.d.monitors.insert(
            {
                "url": ctx.options.url,
                "channel_id": ctx.options.channel.id,
                "type": "collection",
            }
        )
        await ctx.respond("✅ Registered collection monitoring!")
        return

    if Shopify.is_product(ctx.options.url):
        ctx.bot.d.monitors.insert(
            {
                "url": ctx.options.url,
                "channel_id": ctx.options.channel.id,
                "type": "product",
            }
        )
        await ctx.respond("✅ Registered product monitoring!")
        return

    await ctx.respond(
        "❌ The URL is invalid, it should contains /products/ or /collections/."
    )


@bot.command()
@lightbulb.option(
    "channel", "Channel to receive alerts", type=hikari.TextableChannel, required=True
)
@lightbulb.option("query", "Searched product name", type=str, required=True)
@lightbulb.option("url", "Website base URL", type=str, required=True)
@lightbulb.command("register_search", "Enable monitoring for a search query")
@lightbulb.implements(lightbulb.SlashCommand)
async def register_search(ctx: lightbulb.Context) -> None:
    if not ctx.options.url.startswith(("https://", "http://")):
        await ctx.respond("❌ Invalid URL")
        return

    if not Shopify.is_shopify(ctx.options.url):
        await ctx.respond("❌ This website is not a Shopify website")
        return

    ctx.bot.d.monitors.insert(
        {
            "url": ctx.options.url,
            "channel_id": ctx.options.channel.id,
            "type": "search",
            "query": ctx.options.query,
        }
    )
    await ctx.respond("✅ Registered search monitoring!")


# @bot.command()
# @lightbulb.command("subscriptions", "Get a list of subscription")
# @lightbulb.implements(lightbulb.SlashCommand)
# async def subscriptions(ctx: lightbulb.Context) -> None:
#     embed = hikari.Embed(title="Subscriptions")

#     for sub in table:
#         embed.add_field(name="#" + str(sub["id"]), value=sub["url"])

#     await ctx.respond(embed)


# @bot.command()
# @lightbulb.option("id", "ID of the subscription", type=int, required=True)
# @lightbulb.command("unsubscribe", "Stop following a subscription")
# @lightbulb.implements(lightbulb.SlashCommand)
# async def unsubscribe(ctx: lightbulb.Context) -> None:
#     table.delete(id=ctx.options.id)
#     info("Deleted subscription #{id}", id=str(ctx.options.id))
#     await ctx.respond(f"🗑 Deleted subscription #{str(ctx.options.id)}.")


if __name__ == "__main__":
    try:
        bot.run(
            activity=hikari.Activity(
                name="Shopify websites!", type=hikari.ActivityType.WATCHING
            )
        )
    except KeyboardInterrupt:
        bot.close()
