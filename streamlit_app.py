import streamlit as st
import pandas as pd

from apify_utils import run_hashtag_scraper
from spotify_scraper import enrich_with_spotify
from label_filter import filter_unsigned_tracks
from data_utils import split_music_and_original, filter_last_6_weeks

st.set_page_config(page_title="TikTok Hashtag Discovery", layout="wide")

st.title("🔍 TikTok Hashtag Discovery Tool")
st.markdown(
    "This tool scrapes **TikTok videos** by hashtag, ranks them by **views**, enriches with **Spotify metadata**, and filters for **unsigned tracks**."
)

# Sidebar Inputs
st.sidebar.header("🛠 Scraper Settings")
hashtag = st.sidebar.text_input("🏷 Hashtag (no #)", value="techno")
max_results = st.sidebar.slider("🔢 Number of Results", min_value=5, max_value=100, value=20, step=5)

display_cols = [
    "Music", "Music author", "playCount", "diggCount",
    "commentCount", "shareCount", "Text", "video_url", "id", "Create Time"
]

# Step 1 — Scrape TikTok Videos by Hashtag
if st.button("1⃣ Scrape TikTok Hashtag"):
    with st.spinner(f"Scraping TikTok for #{hashtag}..."):
        raw_df = run_hashtag_scraper(hashtag, max_results)

    if raw_df is None or raw_df.empty:
        st.error("❌ No data returned from Apify.")
    else:
        # ✅ Filter to only recent videos
        filtered_df = filter_last_6_weeks(raw_df)

        # Step 2 — Sort by playCount
        sorted_df = filtered_df.sort_values("playCount", ascending=False).reset_index(drop=True)
        st.session_state["hashtag_df"] = sorted_df

        st.success(f"✅ Loaded and sorted {len(sorted_df)} recent videos.")
        st.subheader("🎥 Top TikTok Videos by View Count")
        st.dataframe(sorted_df[display_cols])

# Step 3 — Filter Original Sounds
if "hashtag_df" in st.session_state and st.button("2⃣ Filter Music / Original Sounds"):
    df = st.session_state["hashtag_df"]
    music_df, original_sounds_df = split_music_and_original(df)

    st.session_state["music_df"] = music_df
    st.session_state["original_df"] = original_sounds_df

    st.success(f"🎶 Filtered {len(music_df)} music-based videos and {len(original_sounds_df)} original sounds.")

    st.subheader("🎵 Music-Based Videos")
    st.dataframe(music_df[display_cols])

    st.subheader("📼 Original Sounds")
    st.dataframe(original_sounds_df[display_cols])

# Step 4 — Enrich with Spotify
if "music_df" in st.session_state and st.button("3⃣ Enrich with Spotify"):
    with st.spinner("Enriching with Spotify metadata..."):
        spotify_input_df = st.session_state["music_df"].rename(
            columns={"Music": "Song Title", "Music author": "Artist"}
        )
        spotify_df = enrich_with_spotify(spotify_input_df)

        # Rename back for display
        display_df = spotify_df.rename(
            columns={"Song Title": "Music", "Artist": "Music author"}
        )
        st.session_state["spotify_df"] = display_df

        st.success("✅ Spotify enrichment complete.")
        display_cols_spotify = ["Music", "Music author", "Label", "diggCount", "shareCount", "playCount", "commentCount", "Create Time"]
        st.subheader("🎧 Enriched Songs (Non-Original Sounds)")
        st.dataframe(display_df[display_cols_spotify])

        if "original_df" in st.session_state:
            st.subheader("📼 Original Sounds (Not Enriched)")
            st.dataframe(st.session_state["original_df"][display_cols])

# Step 5 — Filter Unsigned Songs
if "spotify_df" in st.session_state and st.button("4️⃣ Show Unsigned Songs"):
    with st.spinner("Filtering for unsigned or unknown-label songs..."):
        unsigned_df = filter_unsigned_tracks(st.session_state["spotify_df"])
        st.session_state["unsigned_df"] = unsigned_df

        st.success(f"🆓 Found {len(unsigned_df)} unsigned or unknown-label songs.")
        st.subheader("🆓 Unsigned or Unknown-Label Songs")
        display_cols_spotify = ["Music", "Music author", "Label", "diggCount", "shareCount", "playCount", "commentCount", "Create Time"]
        st.dataframe(unsigned_df[display_cols_spotify])

        csv = unsigned_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Unsigned Songs CSV", csv, "unsigned_tiktok_songs.csv", "text/csv")

        if "original_df" in st.session_state:
            st.subheader("📼 Original Sounds (Not Enriched)")
            st.dataframe(st.session_state["original_df"][display_cols])
