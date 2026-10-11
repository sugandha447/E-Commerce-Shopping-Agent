import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()


def search_products(query: str, max_price: float = 100000) -> list:
    """
    Search live Amazon products within the user's budget.
    """

    api_key = os.getenv("QUICKCOMMERCE_API_KEY")

    response = requests.get(
        "https://api.quickcommerceapi.com/v1/search",
        headers={
            "X-API-Key": api_key
        },
        params={
            "q": query,
            "lat": 13.0878,
            "lon": 80.2785,
            "platform": "Amazon"
        }
    )

    if response.status_code != 200:
        return [{"error": "Unable to fetch products"}]

    data = response.json()
    products = data.get("data", {}).get("products", [])

    result = []

    for product in products:

        price = product.get("offer_price", 0)
        name = product.get("name", "")

        if price > 0 and price <= max_price:

            product_data = {
                "name": name,
                "price": price,
                "rating": product.get("rating"),
                "rating_count": product.get("rating_count"),
                "available": product.get("available"),
                "link": product.get("deeplink")
            }

            # Add gaming information only when
            # gaming-related information exists.
            gaming_info = []

            latency = re.findall(
                r'\b\d+\s*ms\b',
                name,
                re.IGNORECASE
            )

            if latency:
                gaming_info.extend(latency)

            gaming_words = [
                "gaming mode",
                "low latency",
                "low-latency",
                "gaming"
            ]

            for word in gaming_words:
                if word.lower() in name.lower():
                    gaming_info.append(word)

            if gaming_info:
                product_data["gaming_info"] = list(set(gaming_info))

            result.append(product_data)

    return result