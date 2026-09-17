"""
etsy_publisher.py
Publishes digital products to Etsy via API v3.
FIXED: Etsy v3 requires x-api-key header for API key
AND Authorization: Bearer token for OAuth separately.
"""
import requests, time

ETSY_BASE = "https://openapi.etsy.com/v3"


def _headers(api_key: str, oauth_token: str = None,
             shared_secret: str = None) -> dict:
    """
    Build correct headers for Etsy API v3.
    As of Feb 9, 2026, Etsy requires BOTH keystring AND shared secret
    in x-api-key header, joined by colon: "keystring:shared_secret"
    """
    import os
    secret = shared_secret or os.environ.get("ETSY_SHARED_SECRET", "")
    if secret:
        h = {"x-api-key": f"{api_key}:{secret}"}
    else:
        h = {"x-api-key": api_key}
    if oauth_token:
        h["Authorization"] = f"Bearer {oauth_token}"
    return h


def get_shop_id(api_key: str, oauth_token: str) -> str:
    """Get the shop ID for the authenticated user."""
    resp = requests.get(
        f"{ETSY_BASE}/application/users/me",
        headers=_headers(api_key, oauth_token),
        timeout=30
    )
    if not resp.ok:
        raise RuntimeError(f"Failed to get user info: {resp.status_code} {resp.text[:300]}")

    user_id = resp.json().get("user_id")
    print(f"  [etsy] User ID: {user_id}")

    resp2 = requests.get(
        f"{ETSY_BASE}/application/users/{user_id}/shops",
        headers=_headers(api_key, oauth_token),
        timeout=30
    )
    if not resp2.ok:
        raise RuntimeError(f"Failed to get shop: {resp2.status_code} {resp2.text[:300]}")

    shops = resp2.json().get("results", [])
    if not shops:
        raise RuntimeError("No Etsy shop found. Please create a shop first at etsy.com")

    shop_id = str(shops[0]["shop_id"])
    print(f"  [etsy] Shop ID: {shop_id} ✓")
    return shop_id


def create_listing(api_key: str, oauth_token: str, shop_id: str,
                   product: dict) -> str:
    """Create a new digital listing on Etsy."""
    headers = _headers(api_key, oauth_token)
    headers["Content-Type"] = "application/json"

    listing_data = {
        "quantity": 999,
        "title": product["title"][:140],
        "description": product["description"],
        "price": product["price"],
        "who_made": "i_did",
        "when_made": "made_to_order",
        "taxonomy_id": 2078,
        "type": "download",
        "is_digital": True,
        "is_supply": False,
        "tags": product["tags"][:13],
        "materials": [],
        "state": "draft",
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
    """Upload the PDF as the digital download file."""
    headers = _headers(api_key, oauth_token)

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


def activate_listing(api_key: str, oauth_token: str, shop_id: str,
                     listing_id: str) -> str:
    """Activate the listing so buyers can find it."""
    headers = _headers(api_key, oauth_token)
    headers["Content-Type"] = "application/json"

    resp = requests.patch(
        f"{ETSY_BASE}/application/shops/{shop_id}/listings/{listing_id}",
        headers=headers,
        json={"state": "active"},
        timeout=30
    )

    if not resp.ok:
        raise RuntimeError(f"Activate failed: {resp.status_code} {resp.text[:400]}")

    url = f"https://www.etsy.com/listing/{listing_id}"
    print(f"  [etsy] Listing activated: {url} ✓")
    return url


def publish_product(api_key: str, oauth_token: str,
                    product: dict, pdf_path: str) -> str:
    """Full pipeline: get shop → create listing → upload PDF → activate."""
    shop_id    = get_shop_id(api_key, oauth_token)
    listing_id = create_listing(api_key, oauth_token, shop_id, product)
    time.sleep(2)
    upload_digital_file(api_key, oauth_token, shop_id, listing_id, pdf_path, product)
    time.sleep(2)
    url = activate_listing(api_key, oauth_token, shop_id, listing_id)
    return url
