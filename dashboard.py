import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="MovieLens Strategic Dashboard", page_icon="🎬", layout="wide")

st.title("🎬 MovieLens Business Intelligence Dashboard")
st.markdown("Interactive insights on User Behavior, Content Performance, and Hidden Patterns.")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    # LOOKING IN LOCAL FOLDER 'MovieLens_Dashboard_Data'
    folder = 'MovieLens_Dashboard_Data/' 
    
    try:
        users = pd.read_csv(folder + 'user_stats.csv')
        trends = pd.read_csv(folder + 'rating_trends.csv')
        genres = pd.read_csv(folder + 'genre_performance.csv')
        tags = pd.read_csv(folder + 'tag_analysis.csv')
        gems = pd.read_csv(folder + 'hidden_gems.csv')
        decades = pd.read_csv(folder + 'decade_impact.csv')
        return users, trends, genres, tags, gems, decades
    except FileNotFoundError:
        return None, None, None, None, None, None

df_users, df_trends, df_genres, df_tags, df_gems, df_decades = load_data()

if df_users is None:
    st.error("⚠️ Data not found! Make sure the 'MovieLens_Dashboard_Data' folder is in the same directory as this script.")
    st.stop()

# --- SIDEBAR ---
st.sidebar.header("Dashboard Filters")
min_votes = st.sidebar.slider("Min Ratings for Genre Analysis", 100, 5000, 1000)

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["👥 User Behavior", "📊 Content Insights", "💎 Hidden Patterns"])

# --- TAB 1: USER BEHAVIOR ---
with tab1:
    st.header("User Behavior & Retention")
    col1, col2, col3 = st.columns(3)
    
    generous_count = len(df_users[df_users['rating_bias'] == 'Generous'])
    harsh_count = len(df_users[df_users['rating_bias'] == 'Harsh'])
    total_users = len(df_users)
    
    col1.metric("Generous Raters", f"{generous_count:,}", f"{(generous_count/total_users)*100:.1f}%")
    col2.metric("Harsh Raters", f"{harsh_count:,}", f"{(harsh_count/total_users)*100:.1f}%")
    col3.metric("Total Users", f"{total_users:,}")
    
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Rating Trends")
        fig_trend = px.line(df_trends, x='year_month', y='avg_rating', markers=True)
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with c2:
        st.subheader("User Activity Tiers")
        bins = [0, 1, 19, 99, 100000]
        labels = ['One-Time', 'Casual', 'Active', 'Power User']
        df_users['tier'] = pd.cut(df_users['n_ratings'], bins=bins, labels=labels)
        retention_counts = df_users['tier'].value_counts().reset_index()
        retention_counts.columns = ['User Tier', 'Count']
        fig_ret = px.bar(retention_counts, x='User Tier', y='Count', color='User Tier')
        st.plotly_chart(fig_ret, use_container_width=True)

# --- TAB 2: CONTENT INSIGHTS ---
with tab2:
    st.header("Content Performance")
    active_genres = df_genres[df_genres['n_ratings'] >= min_votes].sort_values('avg_rating')
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top Genres")
        fig_best = px.bar(active_genres.tail(10), x='avg_rating', y='genre', orientation='h', color='avg_rating')
        st.plotly_chart(fig_best, use_container_width=True)
    with col2:
        st.subheader("Bottom Genres")
        fig_worst = px.bar(active_genres.head(10), x='avg_rating', y='genre', orientation='h', color='avg_rating')
        st.plotly_chart(fig_worst, use_container_width=True)

    st.subheader("Tag Sentiment")
    valid_tags = df_tags[df_tags['n_uses'] >= 50]
    fig_tags = px.scatter(valid_tags, x='n_uses', y='avg_rating', hover_data=['tag'], size='n_uses')
    fig_tags.add_hline(y=3.5, line_dash="dash")
    st.plotly_chart(fig_tags, use_container_width=True)

# --- TAB 3: HIDDEN PATTERNS ---
with tab3:
    st.header("Hidden Patterns")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Decade Analysis")
        fig_years = px.scatter(df_decades, x='decade', y='avg_rating_mean', size='n_movies_rated', color='avg_rating_mean')
        st.plotly_chart(fig_years, use_container_width=True)
    with c2:
        st.subheader("Insights")
        golden = df_decades.loc[df_decades['avg_rating_mean'].idxmax()]
        st.info(f"🏆 Golden Era: {int(golden['decade'])}s ({golden['avg_rating_mean']:.2f} avg)")

    st.subheader("💎 Hidden Gems Finder")
    c1, c2 = st.columns(2)
    with c1:
        genre_filter = st.selectbox("Genre", ["All"] + sorted(list(set(df_gems['genres'].str.split('|').explode().dropna().unique()))))
    with c2:
        year_filter = st.slider("Year", 1990, 2023, (2000, 2023))
        
    filtered = df_gems[(df_gems['release_year'] >= year_filter[0]) & (df_gems['release_year'] <= year_filter[1])]
    if genre_filter != "All":
        filtered = filtered[filtered['genres'].str.contains(genre_filter, na=False)]
        
    st.dataframe(filtered[['title', 'release_year', 'genres', 'avg_rating', 'n_ratings']].sort_values('avg_rating', ascending=False), use_container_width=True)