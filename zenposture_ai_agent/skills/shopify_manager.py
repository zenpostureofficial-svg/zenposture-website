"""
Shopify Manager Skill
Manage ZenPosture's Shopify store via Admin API.
"""

import urllib.request, urllib.parse, json


class ShopifyManager:
    def __init__(self, shop_url, access_token):
        self.base = f"https://{shop_url}/admin/api/2024-01"
        self.headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }

    def _request(self, method, endpoint, data=None):
        url = f"{self.base}/{endpoint}"
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, headers=self.headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read()), None
        except urllib.error.HTTPError as e:
            return None, f"HTTP {e.code}: {e.read().decode()}"
        except Exception as e:
            return None, str(e)

    # ── Products ──────────────────────────────────────────────────────────────

    def list_products(self, limit=10):
        data, err = self._request("GET", f"products.json?limit={limit}")
        if err: return None, err
        return data.get("products", []), None

    def get_product(self, product_id):
        data, err = self._request("GET", f"products/{product_id}.json")
        if err: return None, err
        return data.get("product"), None

    def create_product(self, title, description, price, sku="", images=None):
        payload = {"product": {
            "title": title,
            "body_html": description,
            "variants": [{"price": str(price), "sku": sku, "inventory_management": "shopify"}],
            "images": [{"src": img} for img in (images or [])]
        }}
        data, err = self._request("POST", "products.json", payload)
        if err: return None, err
        return data.get("product"), None

    def update_product(self, product_id, **fields):
        payload = {"product": {"id": product_id, **fields}}
        data, err = self._request("PUT", f"products/{product_id}.json", payload)
        if err: return None, err
        return data.get("product"), None

    def delete_product(self, product_id):
        _, err = self._request("DELETE", f"products/{product_id}.json")
        return err is None, err

    def update_price(self, product_id, variant_id, new_price):
        payload = {"variant": {"id": variant_id, "price": str(new_price)}}
        data, err = self._request("PUT", f"variants/{variant_id}.json", payload)
        if err: return None, err
        return data.get("variant"), None

    # ── Orders ────────────────────────────────────────────────────────────────

    def list_orders(self, status="any", limit=10):
        data, err = self._request("GET", f"orders.json?status={status}&limit={limit}")
        if err: return None, err
        return data.get("orders", []), None

    def get_order(self, order_id):
        data, err = self._request("GET", f"orders/{order_id}.json")
        if err: return None, err
        return data.get("order"), None

    # ── Inventory ─────────────────────────────────────────────────────────────

    def get_inventory(self, inventory_item_id, location_id):
        endpoint = f"inventory_levels.json?inventory_item_ids={inventory_item_id}&location_ids={location_id}"
        data, err = self._request("GET", endpoint)
        if err: return None, err
        levels = data.get("inventory_levels", [])
        return levels[0] if levels else None, None

    # ── Summary for agent ─────────────────────────────────────────────────────

    def store_summary(self):
        products, _ = self.list_products(limit=5)
        orders, _   = self.list_orders(status="open", limit=5)
        lines = []
        if products:
            lines.append(f"Products ({len(products)} shown):")
            for p in products:
                price = p["variants"][0]["price"] if p.get("variants") else "?"
                lines.append(f"  • {p['title']} — ₹{price} (ID: {p['id']})")
        if orders:
            lines.append(f"\nOpen Orders ({len(orders)}):")
            for o in orders:
                lines.append(f"  • #{o['order_number']} — ₹{o['total_price']} — {o['financial_status']}")
        return "\n".join(lines) or "No data found."
