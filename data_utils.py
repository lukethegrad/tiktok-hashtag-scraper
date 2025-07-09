import pandas as pd
import streamlit as st


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
