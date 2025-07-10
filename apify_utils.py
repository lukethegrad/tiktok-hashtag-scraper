import os
import json
import requests
import pandas as pd
import streamlit as st
import time

# 🔐 Apify credentials
APIFY_API_KEY = os.getenv("APIFY_API_KEY")


def run_hashtag_scraper(hashtag: str, max_results: int) -> pd.DataFrame:
    try:
        hashtag = hashtag.strip().replace("#", "")
        hashtag_actor = "clockworks~tiktok-hashtag-scraper"

        input_payload = {
            "hashtags": [hashtag],
            "maxItems": max_results
        }

        st.write("🏷 Running Apify hashtag scraper with:")
        st.json(input_payload)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {APIFY_API_KEY}"
        }

        response = requests.post(
            f"https://api.apify.com/v2/acts/{hashtag_actor}/runs?wait=1",
            json=input_payload,
            headers=headers
        )
        response.raise_for_status()

        run_data = response.json()
        dataset_id = run_data["data"]["defaultDatasetId"]
        st.write(f"📁 Dataset ID: {dataset_id}")

        dataset_items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?format=json"

        # ⏳ Poll until data is ready or timeout
        timeout = 300  # seconds
        interval = 10  # seconds
        elapsed = 0

        st.write("🔄 Polling Apify for dataset results...")

        while elapsed < timeout:
            result = requests.get(dataset_items_url, headers=headers)
            if result.status_code == 200:
                items = result.json()
                if items:
                    st.success(f"✅ Received {len(items)} items from Apify.")
                    df = pd.DataFrame(items)
                    df = df.rename(columns={
                        "authorMeta.name": "Author",
                        "text": "Text",
                        "diggCount": "diggCount",
                        "shareCount": "shareCount",
                        "playCount": "playCount",
                        "commentCount": "commentCount",
                        "videoMeta.duration": "Duration (seconds)",
                        "musicMeta.musicName": "Music",
                        "musicMeta.musicAuthor": "Music author",
                        "webVideoUrl": "video_url"
                    })
                    return df

            time.sleep(interval)
            elapsed += interval
            st.write(f"⏳ Waited {elapsed}s... still waiting for Apify dataset...")

        st.warning("⚠️ Timeout reached. No data received from Apify.")
        return pd.DataFrame()

    except requests.exceptions.HTTPError as e:
        st.error("❌ Failed to run hashtag scraper (HTTP error).")
        if e.response is not None:
            st.error(f"🔍 Apify response:\n{e.response.text}")
        st.error(str(e))
        return pd.DataFrame()

    except Exception as e:
        st.error("❌ Unexpected error when running hashtag scraper.")
        st.error(str(e))
        return pd.DataFrame()


