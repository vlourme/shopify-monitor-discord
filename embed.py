from hikari import Embed, Color
from urllib.parse import urlparse


def generate_product_embed(
    monitor: dict, product: dict, type: str, provider: str
) -> Embed:
    url = urlparse(monitor["url"])

    embed = Embed(title=product["title"], url=product["url"])
    embed.set_author(
        name=url.hostname,
        url=monitor["url"],
        icon="https://www.google.com/s2/favicons?domain={}&size=256".format(
            url.hostname
        ),
    )
    embed.set_image(product["image"])
    embed.add_field(name="Brand", value=product["brand"])
    embed.add_field(name="Type", value=product["type"])

    for variant in product["variants"]:
        if variant["available"] == 0:
            continue

        if variant["available"] == 1:
            available = "Yes"
        else:
            available = "N/A"

        embed.add_field(
            name="__{}__".format(variant["title"]),
            value=f"Price: **{variant['price']}**\nAvailable: **{available}**",
            inline=True,
        )

    if type == "new":
        embed.color = Color(0xA1C181)
        embed.set_footer(text="🆕 New product")
    elif type == "update":
        embed.color = Color(0xFE7F2D)
        embed.set_footer(text="🔄 Product updated")

    if provider == "collection":
        embed.set_footer(text=f"{embed.footer.text} | 📦 Collection monitoring")
    elif provider == "product":
        embed.set_footer(text=f"{embed.footer.text} | 📦 Product monitoring")
    elif provider == "search":
        embed.set_footer(text=f"{embed.footer.text} | 🔍 Search monitoring")

    return embed
