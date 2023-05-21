# Shopify Monitor for Discord

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/donate/?hosted_button_id=X28NBS7XN2Q9C)

Shopify Monitor for Discord is a Python-based project that allows users to track prices, availability changes, search results, and collections for any Shopify product. It provides low latency notifications to Discord channels, ensuring you never miss an important change.

You can make a donation using the button above, all of my Discord bot are open-source and hopefully they'll always be. You can help me maintaining them by making a small donation.

## Features

- Track price changes and availability of specific Shopify products.
- Monitor changes in search results for a specified keyword.
- Watch collections for product listing, availability change and price drops.
- Sends notifications to a specified Discord channel.
- Fully configurable to track as many or as few products/search terms/collections as desired.

## Bot commands

```sh
/monitors add search [url] [query] [channel]    # Monitor a search query
/monitors add collection [url] [channel]        # Monitor a collection
/monitors add product [url] [channel]           # Monitor a product
/monitors list [channel]                        # List active monitors for a given channel
/monitors remove [id]                           # Deactivate a monitor
```

## Requirements

- Python 3.9 or later
- Discord account and server

## Installation

1. Clone this repository
2. Install requirements and Python dependencies (`pip install -r requirements.txt`)
3. Copy the .env.example to .env and define your configuration
4. Run the project using `python -OO main.py`

> You'll need to setup a Discord bot with the `bot` scope and following permissions:
>
> - Send messages
> - Use Slash Commands
> - Read Messages/View Channels

## Drawbacks and limitations

- I haven't tested this bot on password-protected websites, this will certainly result in an error.
- No proxy-system included, use latency like 3-5 minutes to avoid bans.
