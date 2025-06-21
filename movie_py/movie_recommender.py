import pandas as pd
import difflib
import requests

API_KEY = "99421267a8ba634b808238517e4346ca"

# Load dataset with full genre binary columns
genre_labels = [
    'unknown', 'Action', 'Adventure', 'Animation', "Children's", 'Comedy', 'Crime',
    'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery',
    'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
]

column_names = ['movie_id', 'title', 'release_date', 'video_release_date', 'IMDb_URL'] + genre_labels
movies = pd.read_csv("ml-100k/u.item", sep='|', encoding='latin-1', names=column_names, usecols=range(24))

# Combine genre columns into a single 'genres' column
movies['genres'] = movies[genre_labels].apply(
    lambda row: '|'.join([genre for genre, val in row.items() if val == 1]), axis=1
)

# Clean title for better matching
movies['title'] = movies['title'].str.strip()

def fetch_movie_details(movie_name):
    import re

    # Remove year like (1995) using regex
    clean_title = re.sub(r"\(\d{4}\)", "", movie_name).strip()

    url = f"https://api.themoviedb.org/3/search/movie"
    params = {
        'api_key': API_KEY,
        'query': clean_title
    }

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
            "summary": overview  # Make sure the key matches 'summary' used in app.py
        })
    return result


    # Recommend movies with overlapping genres
    def genre_overlap(genres):
        return len(genre_set.intersection(set(genres.split('|')))) > 0

    similar_movies = movies[movies['genres'].apply(genre_overlap)]
    similar_movies = similar_movies[similar_movies['title'] != selected_movie].head(num_recommendations)

    result = []
    for title in similar_movies['title']:
        poster, overview = fetch_movie_details(title)
        result.append({
            "title": title,
            "poster": poster,
            "summary": overview
        })
    return result
