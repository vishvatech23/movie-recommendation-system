import streamlit as st
import pandas as pd
import difflib
import requests

st.set_page_config(page_title="Movie Recommendation System", layout="centered")

# 🎨 Custom Gradient Background (as per your image)
st.markdown("""
<style>
/* Gradient Background */
.stApp {
    background-color: #310e68;
    background-image: linear-gradient(316deg, #310e68 0%, #5f0f40 74%);
    color: white;
}

/* Widget container background with semi-transparent overlay */
.css-18e3th9 {
    background-color: rgba(0, 0, 0, 0.55) !important;
    border-radius: 15px;
    padding: 1.5rem;
}

/* Make text readable */
h1, h2, h3, h4, h5, h6, p, span, label {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# Load dataset
genre_labels = [
    'unknown', 'Action', 'Adventure', 'Animation', "Children's", 'Comedy', 'Crime',
    'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery',
    'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
]
column_names = ['movie_id', 'title', 'release_date', 'video_release_date', 'IMDb_URL'] + genre_labels
movies = pd.read_csv("ml-100k/u.item", sep='|', encoding='latin-1', names=column_names, usecols=range(24))
movies['genres'] = movies[genre_labels].apply(
    lambda row: '|'.join([genre for genre, val in row.items() if val == 1]), axis=1
)
movies['title'] = movies['title'].str.strip()

API_KEY = "99421267a8ba634b808238517e4346ca"

def fetch_movie_details(movie_name):
    import re
    clean_title = re.sub(r"\(\d{4}\)", "", movie_name).strip()
    url = f"https://api.themoviedb.org/3/search/movie"
    params = {'api_key': API_KEY, 'query': clean_title}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get('results'):
            result = data['results'][0]
            poster_path = result.get('poster_path')
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
            overview = result.get('overview', 'No summary available.')
            return poster_url, overview
        else:
            return None, "No summary found."
    except Exception as e:
        print(f"Error fetching details for '{movie_name}': {e}")
        return None, "Summary not available (error occurred)."

def recommend(movie):
    movie_index = difflib.get_close_matches(movie, movies['title'], n=1)
    if not movie_index:
        return []

    selected_movie = movie_index[0]
    selected_genre = movies[movies['title'] == selected_movie]['genres'].values[0]
    similar_movies = movies[movies['genres'] == selected_genre].head(10)

    result = []
    for title in similar_movies['title']:
        poster, overview = fetch_movie_details(title)
        if poster is None:
            poster = "https://via.placeholder.com/120x180?text=No+Image"
        result.append({
            "title": title,
            "poster": poster,
            "summary": overview
        })
    return result

# Streamlit UI
st.title("🎬 Movie Recommendation System")

movie_input = st.text_input("🔍 Search for a movie by name:")
selected_genre = st.selectbox("🎞️ Filter by genre (optional):", [''] + genre_labels)
filtered_movies = movies[movies['genres'].str.contains(selected_genre)] if selected_genre else movies
movie_list = ["Select a movie..."] + filtered_movies['title'].sort_values().tolist()
movie_selection = st.selectbox("🎬 Choose a movie:", movie_list)

if st.button("Get Recommendations"):
    if movie_selection != "Select a movie...":
        results = recommend(movie_selection)
        if results:
            st.subheader("🎯 You might also like:")
            for movie in results:
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.image(movie["poster"], width=120)
                with col2:
                    st.markdown(f"**{movie['title']}**")
                    st.write(movie["summary"])
        else:
            st.warning("No recommendations found.")
    else:
        st.warning("Please select a valid movie.")
