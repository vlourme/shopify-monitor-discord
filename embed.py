from hikari import Embed, Color
from urllib.parse import urlparse, urljoin


def generate_product_embed(
    monitor: dict, product: dict, type: str, provider: str
) -> Embed:
    url = urlparse(monitor["url"])

    embed = Embed(title=product["title"], url=product["url"])
    embed.set_author(
        name=url.hostname,
        url=monitor["url"],
        icon="https://t2.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url={}&size=256".format(
            urljoin(monitor["url"], "/")
        ),
    )
    embed.set_image(product["image"])
    embed.add_field(name="Brand", value=product["brand"], inline=True)
    embed.add_field(name="Type", value=product["type"], inline=True)
    embed.add_field(name="Price", value=product["price"], inline=True)

    variants = [
        variant["title"] if variant["available"] == 1 else "*" + variant["title"] + "*"
        for variant in product["variants"]
        if variant["available"] != 0
    ]

    embed.add_field(
        name="Available variants",
        value=", ".join(variants) if len(variants) > 0 else "None",
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
