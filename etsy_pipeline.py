#!/usr/bin/env python3
"""
etsy_pipeline.py — Automated Etsy Digital Products Pipeline
============================================================
Runs weekly via GitHub Actions. Each run:
  1. Auto-refreshes Etsy OAuth token using the refresh token
  2. Selects a new product from the catalog
  3. Generates a professional PDF
  4. Publishes it to Etsy as a digital download listing

100% free — no API cost, no external service needed.
"""
import os, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from content_gen    import get_product_for_week
from pdf_gen        import generate_pdf
from etsy_publisher import publish_product
from etsy_auth      import refresh_access_token


def run():
    ETSY_API_KEY      = os.environ.get("ETSY_API_KEY", "")
    ETSY_REFRESH_TOKEN = os.environ.get("ETSY_REFRESH_TOKEN", "")

    if not ETSY_API_KEY:
        raise EnvironmentError("ETSY_API_KEY not set in GitHub Secrets")
    if not ETSY_REFRESH_TOKEN:
        raise EnvironmentError("ETSY_REFRESH_TOKEN not set in GitHub Secrets")

    print(f"\n{'='*60}")
    print(f"  Pipeline : Automated Etsy Digital Products")
    print(f"{'='*60}\n")

    # Step 0: Auto-refresh OAuth token
    print("🔑  Step 0/3 — Refreshing Etsy OAuth token ...")
    oauth_token = refresh_access_token(ETSY_API_KEY, ETSY_REFRESH_TOKEN)

    # Step 1: Get this week's product
    print("\n📋  Step 1/3 — Selecting product for this week ...")
    product = get_product_for_week()
    print(f"  → Title    : {product['title']}")
    print(f"  → Category : {product['category']}")
    print(f"  → Price    : ${product['price']}")

    with tempfile.TemporaryDirectory(prefix="etsy_") as tmp:
        tmp = Path(tmp)

        # Step 2: Generate PDF
        print(f"\n📄  Step 2/3 — Generating professional PDF ...")
        pdf_path = str(tmp / f"{product['filename']}.pdf")
        generate_pdf(product, pdf_path)

        # Step 3: Publish to Etsy
        print(f"\n🛍️   Step 3/3 — Publishing to Etsy ...")
        url = publish_product(ETSY_API_KEY, oauth_token, product, pdf_path)

        print(f"\n🎉  Live on Etsy: {url}")
        return url


if __name__ == "__main__":
    run()
