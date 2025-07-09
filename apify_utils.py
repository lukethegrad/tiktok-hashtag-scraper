import os
import json
import requests
import pandas as pd
import streamlit as st

# 🔐 Apify credentials
APIFY_API_KEY = os.getenv("APIFY_API_KEY")


def run_hashtag_scraper(hashtag: str, max_results: int) -> pd.DataFrame:
    """
    Runs the Apify 'clockworks/tiktok-hashtag-scraper' to get TikTok videos by hashtag.
    Returns a DataFrame with all extracted metadata.
    """
    try:
        hashtag_actor = "clockworks~tiktok-hashtag-scraper"

        input_payload = {
            "hashtag": hashtag,
            "maxItems": max_results
        }


        st.write("🏷 Running Apify hashtag scraper with:")
        st.json(input_payload)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {APIFY_API_KEY}"
        }

        # Run the Apify actor
        response = requests.post(
            f"https://api.apify.com/v2/acts/{hashtag_actor}/runs?wait=1",
            json=input_payload,
            headers=headers
        )
        response.raise_for_status()

        run_data = response.json()
        dataset_id = run_data["data"]["defaultDatasetId"]
        st.write(f"📁 Dataset ID: {dataset_id}")

        # Fetch dataset records
        dataset_items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?format=json"
        result = requests.get(dataset_items_url, headers=headers)
        result.raise_for_status()

        items = result.json()
        if not items:
            st.warning("⚠️ No results returned from Apify hashtag scraper.")
            return pd.DataFrame()

        df = pd.DataFrame(items)

        # Normalize column names for downstream compatibility
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

    except Exception as e:
        st.error("❌ Failed to run hashtag scraper.")
        st.error(str(e))
        return pd.DataFrame()
