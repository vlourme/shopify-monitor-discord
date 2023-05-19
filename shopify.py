from urllib.parse import urlparse, urljoin
from requests import get


class Shopify:
    @staticmethod
    def format_url(url: str) -> str:
        """
        Remove URL query strings
        """

        url = url.split("?")[0]
        if not url.endswith("/"):
            url += "/"

        return url

    @staticmethod
    def get_collection(url: str) -> list:
        """
        Get collection's products
        """
        url = Shopify.format_url(url)
        url = urljoin(url, "products.json")

        content = get(url).json()

        return [
            {
                "id": product["id"],
                "title": product["title"],
                "url": urljoin(url, "/products/" + product["handle"]),
                "brand": product["vendor"],
                "type": product["product_type"],
                "price": product.get("variants", [])[0].get("price", "N/A"),
                "variants": [
                    {
                        "id": variant["id"],
                        "title": variant["title"],
                        "price": variant["price"],
                        "available": Shopify.get_available_status(
                            variant.get("available", "N/A")
                        ),
                    }
                    for variant in product.get("variants", [])
                ],
                "image": product["images"][0]["src"] or "",
            }
            for product in content["products"]
        ]

    @staticmethod
    def get_available_status(value) -> int:
        """
        Get available status
        """

        if value == True:
            return 1
        elif value == False:
            return 0
        else:
            return -1

    @staticmethod
    def get_product(url: str) -> dict:
        """
        Get product information
        """
        url = Shopify.format_url(url)
        url = url.rstrip("/") + ".js"

        product = get(url).json()

        return {
            "id": product["id"],
            "title": product["title"],
            "url": urljoin(url, "/products/" + product["handle"]),
            "brand": product["vendor"],
            "price": product["price"] / 100 or "N/A",
            "type": product["type"],
            "variants": [
                {
                    "id": variant["id"],
                    "title": variant["title"],
                    "price": variant["price"] / 100 or "N/A",
                    "available": Shopify.get_available_status(
                        variant.get("available", "N/A")
                    ),
                }
                for variant in product.get("variants", [])
            ],
            "image": product["media"][0]["src"] or "",
        }

    @staticmethod
    def get_search_results(url: str, query: str) -> list:
        """
        Get search results
        """
        params = "resources[type]=product&resources[options][unavailable_products]=hide"
        url = Shopify.format_url(url)
        url = urljoin(
            url, "/search/suggest.json?q={q}&{params}".format(q=query, params=params)
        )

        content = get(url).json()

        return [
            {
                "id": product["id"],
                "title": product["title"],
                "url": urljoin(url, "/products/" + product["handle"]),
                "brand": product["vendor"],
                "image": product["image"],
                "price": product["price"],
            }
            for product in content["resources"]["results"]["products"]
        ]

    @staticmethod
    def is_shopify(url: str) -> bool:
        """
        Check if the URL is a valid Shopify store
        """

        try:
            url = urljoin(url, "/cart.js")
            content = get(url).json()

            return content["token"] != None
        except:
            return False

    @staticmethod
    def is_collection(url: str) -> bool:
        """
        Check if the URL is a valid collection
        """
        if not "/collections/" in url:
            return False

        try:
            products = Shopify.get_collection(url)

            return len(products) > 0
        except:
            return False

    @staticmethod
    def is_product(url: str) -> None:
        """
        Check if the URL is a valid product
        """

        if not "/products/" in url:
            return False

        try:
            Shopify.get_product(url)
            return True
        except:
            return False
