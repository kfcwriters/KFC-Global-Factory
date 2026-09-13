"""
etsy_publisher.py
Publishes digital products to Etsy via API v3.
Handles OAuth, listing creation, and digital file upload.
"""
import requests, json, time


ETSY_BASE = "https://openapi.etsy.com/v3"


def get_shop_id(api_key: str) -> str:
    """Get the shop ID for the authenticated user."""
    headers = {"x-api-key": api_key}
    resp = requests.get(f"{ETSY_BASE}/application/users/me", headers=headers, timeout=30)
    if not resp.ok:
        raise RuntimeError(f"Failed to get user info: {resp.status_code} {resp.text[:200]}")
    user_id = resp.json().get("user_id")
    
    resp2 = requests.get(f"{ETSY_BASE}/application/users/{user_id}/shops",
                         headers=headers, timeout=30)
    if not resp2.ok:
        raise RuntimeError(f"Failed to get shop: {resp2.status_code} {resp2.text[:200]}")
    
    shops = resp2.json().get("results", [])
    if not shops:
        raise RuntimeError("No Etsy shop found. Please create a shop first at etsy.com")
    
    shop_id = shops[0]["shop_id"]
    print(f"  [etsy] Shop ID: {shop_id} ✓")
    return str(shop_id)


def create_listing(api_key: str, oauth_token: str, shop_id: str, 
                   product: dict) -> str:
    """Create a new digital listing on Etsy."""
    headers = {
        "x-api-key": api_key,
        "Authorization": f"Bearer {oauth_token}",
        "Content-Type": "application/json",
    }

    listing_data = {
        "quantity": 999,
        "title": product["title"][:140],
        "description": product["description"],
        "price": product["price"],
        "who_made": "i_did",
        "when_made": "made_to_order",
        "taxonomy_id": 2078,        # Books, Movies & Music > Books > Education
        "type": "download",
        "is_digital": True,
        "is_supply": False,
        "tags": product["tags"][:13],  # Etsy max 13 tags
        "materials": [],
        "shipping_profile_id": None,
        "state": "draft",           # Start as draft, activate after file upload
    }

    resp = requests.post(
        f"{ETSY_BASE}/application/shops/{shop_id}/listings",
        headers=headers,
        json=listing_data,
        timeout=30
    )

    if not resp.ok:
        raise RuntimeError(f"Create listing failed: {resp.status_code} {resp.text[:400]}")

    listing_id = str(resp.json()["listing_id"])
    print(f"  [etsy] Listing created: {listing_id} ✓")
    return listing_id


def upload_digital_file(api_key: str, oauth_token: str, shop_id: str,
                        listing_id: str, pdf_path: str, product: dict):
    """Upload the PDF as the digital download file for the listing."""
    headers = {
        "x-api-key": api_key,
        "Authorization": f"Bearer {oauth_token}",
    }

    with open(pdf_path, "rb") as f:
        files = {
            "file": (f"{product['filename']}.pdf", f, "application/pdf"),
            "name": (None, f"{product['filename']}.pdf"),
            "rank": (None, "1"),
        }
        resp = requests.post(
            f"{ETSY_BASE}/application/shops/{shop_id}/listings/{listing_id}/files",
            headers=headers,
            files=files,
            timeout=60
        )

    if not resp.ok:
        raise RuntimeError(f"File upload failed: {resp.status_code} {resp.text[:400]}")

    print(f"  [etsy] PDF uploaded ✓")


def activate_listing(api_key: str, oauth_token: str, shop_id: str, listing_id: str):
    """Change listing state from draft to active so buyers can find it."""
    headers = {
        "x-api-key": api_key,
        "Authorization": f"Bearer {oauth_token}",
        "Content-Type": "application/json",
    }

    resp = requests.patch(
        f"{ETSY_BASE}/application/shops/{shop_id}/listings/{listing_id}",
        headers=headers,
        json={"state": "active"},
        timeout=30
    )

    if not resp.ok:
        raise RuntimeError(f"Activate listing failed: {resp.status_code} {resp.text[:400]}")

    url = f"https://www.etsy.com/listing/{listing_id}"
    print(f"  [etsy] Listing activated: {url} ✓")
    return url


def publish_product(api_key: str, oauth_token: str, 
                    product: dict, pdf_path: str) -> str:
    """
    Full pipeline: get shop → create listing → upload PDF → activate.
    Returns the live Etsy listing URL.
    """
    shop_id    = get_shop_id(api_key)
    listing_id = create_listing(api_key, oauth_token, shop_id, product)
    time.sleep(2)
    upload_digital_file(api_key, oauth_token, shop_id, listing_id, pdf_path, product)
    time.sleep(2)
    url = activate_listing(api_key, oauth_token, shop_id, listing_id)
    return url
