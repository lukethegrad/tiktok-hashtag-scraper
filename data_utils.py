import pandas as pd
import streamlit as st
from datetime import datetime, timedelta


def split_music_and_original(df: pd.DataFrame):
    """
    Splits TikTok videos into two DataFrames:
    1. Music-based (non-original sounds)
    2. Original sounds (labelled as 'original sound')
    """
    if "Music" not in df.columns:
        st.warning("⚠️ 'Music' column missing — cannot separate music and original sounds.")
        return df, pd.DataFrame()

    # Separate based on whether music name contains "original sound"
    music_df = df[~df["Music"].str.lower().str.contains("original sound", na=False)].copy()
    original_df = df[df["Music"].str.lower().str.contains("original sound", na=False)].copy()

    st.write(f"🎵 Music videos: {len(music_df)} | 📼 Original sounds: {len(original_df)}")
    return music_df.reset_index(drop=True), original_df.reset_index(drop=True)


def filter_last_6_weeks(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filters DataFrame to only include videos from the last 6 weeks.
    """
    if "Create Time" not in df.columns:
        st.warning("⚠️ 'Create Time' column missing — cannot filter by recency.")
        return df

    # Ensure Create Time is a datetime object
    df["Create Time"] = pd.to_datetime(df["Create Time"], errors="coerce")

    # Drop any rows where date parsing failed
    df = df.dropna(subset=["Create Time"])

    cutoff = datetime.now() - timedelta(weeks=6)
    recent_df = df[df["Create Time"] >= cutoff].copy()

    st.write(f"📆 Filtered to {len(recent_df)} videos from the last 6 weeks.")
    return recent_df.reset_index(drop=True)
