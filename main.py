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
@lightbulb.command("monitors", "Manage monitors")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def monitors() -> None:
    pass


@monitors.child
@lightbulb.command("add", "Add a monitor")
@lightbulb.implements(lightbulb.SlashSubGroup)
async def add() -> None:
    pass


@add.child
@lightbulb.option("channel", "Channel", type=hikari.TextableChannel, required=True)
@lightbulb.option("url", "Collection URL", type=str, required=True)
@lightbulb.command("collection", "Enable monitoring for a collection")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def register_collection(ctx: lightbulb.Context) -> None:
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

    await ctx.respond("❌ The URL is invalid, it should contains /collections/.")


@add.child
@lightbulb.option("channel", "Channel", type=hikari.TextableChannel, required=True)
@lightbulb.option("url", "Product URL", type=str, required=True)
@lightbulb.command("product", "Enable monitoring for a product")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def register_product(ctx: lightbulb.Context) -> None:
    if not ctx.options.url.startswith(("https://", "http://")):
        await ctx.respond("❌ Invalid URL")
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

    await ctx.respond("❌ The URL is invalid, it should contains /products/.")


@add.child
@lightbulb.option("channel", "Channel", type=hikari.TextableChannel, required=True)
@lightbulb.option("query", "Searched product name", type=str, required=True)
@lightbulb.option("url", "Website base URL", type=str, required=True)
@lightbulb.command("search", "Enable monitoring for a search query")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def search(ctx: lightbulb.Context) -> None:
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


@monitors.child
@lightbulb.option("channel", "Channel", type=hikari.TextableChannel, required=True)
@lightbulb.command("collections", "List collections")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def list(ctx: lightbulb.Context):
    monitors = bot.d.monitors.find(channel_id=ctx.options.channel.id)

    if not monitors:
        await ctx.respond("❌ No monitors found")
        return

    for monitor in monitors:
        embed = hikari.Embed()
        embed.title = "Monitor #{}".format(monitor["id"])
        embed.add_field("URL", monitor["url"], inline=True)
        embed.add_field("Type", str(monitor["type"]).capitalize(), inline=True)

        variants_count = bot.d.variants.count(monitor_id=monitor["id"])
        embed.add_field("Variants found", variants_count, inline=True)
        await ctx.respond(embed=embed)


@monitors.child
@lightbulb.option("id", "Monitor ID", type=int, required=True)
@lightbulb.command("remove", "Remove a monitor")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def remove(ctx: lightbulb.Context):
    monitor = bot.d.monitors.find_one(id=ctx.options.id)

    if not monitor:
        await ctx.respond("❌ Monitor not found")
        return

    bot.d.monitors.delete(id=ctx.options.id)
    await ctx.respond("✅ Monitor removed")


if __name__ == "__main__":
    if os.name != "nt":
        import uvloop

        uvloop.install()

    bot.run(
        activity=hikari.Activity(
            name="Shopify websites!", type=hikari.ActivityType.WATCHING
        )
    )
