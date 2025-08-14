# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import subprocess
import time

OUTPUT_FILE = "report.csv"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def run_scraper():
    process = subprocess.Popen(["python", "scraper.py"])
    while process.poll() is None:
        with st.spinner("Processing URLs..."):
            time.sleep(2)

def display_analysis():
    try:
        df = pd.read_csv(OUTPUT_FILE, dtype={"url": str})
        df["error"] = df["error"].fillna("")
        df_clean = df[df["error"] == ""].copy()

        df_clean.insert(0, "video_no", range(1, len(df_clean) + 1))
        df_clean = df_clean[["video_no", "views", "likes", "comments", "shares", "url"]]

        st.subheader("Video Metrics Table")
        st.dataframe(df_clean, use_container_width=True)

        # --- Top 10 Videos by Views ---
        st.subheader("🔝 Top 10 Videos by Views")
        top_views = df_clean.sort_values(by="views", ascending=False).head(10)
        fig1, ax1 = plt.subplots()
        ax1.barh(top_views["url"], top_views["views"], color="orange")
        ax1.set_xlabel("Views")
        ax1.set_title("Top 10 Videos by Views")
        ax1.invert_yaxis()
        st.pyplot(fig1)

        # --- Top 10 Videos by Likes ---
        st.subheader("❤️ Top 10 Videos by Likes")
        top_likes = df_clean.sort_values(by="likes", ascending=False).head(10)
        fig2, ax2 = plt.subplots()
        ax2.barh(top_likes["url"], top_likes["likes"], color="green")
        ax2.set_xlabel("Likes")
        ax2.set_title("Top 10 Videos by Likes")
        ax2.invert_yaxis()
        st.pyplot(fig2)

        # --- Pie Chart of Total Metrics ---
        st.subheader("📊 Engagement Breakdown (Pie Chart)")
        totals = df_clean[["views", "likes", "comments", "shares"]].sum()
        pie_labels = ["Views", "Likes", "Comments", "Shares"]
        pie_values = [totals["views"], totals["likes"], totals["comments"], totals["shares"]]
        pie_colors = ["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"]

        fig3, ax3 = plt.subplots()
        ax3.pie(pie_values, labels=pie_labels, colors=pie_colors, autopct="%1.1f%%", startangle=140)
        ax3.axis("equal")
        st.pyplot(fig3)

        # --- Clean Totals Table ---
        st.subheader("📦 Overall Totals")
        totals_df = pd.DataFrame({
            "Metric": ["Total Views", "Total Likes", "Total Comments", "Total Shares"],
            "Value": [
                f"{int(totals['views']):,}",
                f"{int(totals['likes']):,}",
                f"{int(totals['comments']):,}",
                f"{int(totals['shares']):,}"
            ]
        })
        st.table(totals_df)

    except FileNotFoundError:
        st.error(f"Report file `{OUTPUT_FILE}` not found. Please run the process first.")
    except Exception as e:
        st.error(f"Error displaying analysis: {e}")


def main():
    st.sidebar.image("logo.png", use_container_width=True)
    st.sidebar.markdown("---")

    st.title("TikTok Video Analytics")

    tab1, tab2 = st.tabs(["Input", "Analysis"])

    with tab1:
        st.header("Input TikTok URLs")
        uploaded_file = st.file_uploader("Upload a .txt file with TikTok URLs (one per line)", type=["txt"])

        if uploaded_file is not None:
            file_path = os.path.join(UPLOAD_DIR, "urls.txt")
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            if st.button("Start Processing"):
                run_scraper()
                st.session_state["processed"] = True
        else:
            st.info("Please upload a .txt file containing TikTok URLs.")

    with tab2:
        st.header("Analysis Results")
        if st.session_state.get("processed", False):
            display_analysis()
        else:
            st.info("No data available. Please upload and process URLs first.")

if __name__ == "__main__":
    main()
