import pickle
import streamlit as st
import requests
import pandas as pd
from requests.exceptions import ConnectionError, Timeout, RequestException
import time

def fetch_poster(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=6f9456b1e9f451efce2a6b03ff5fa896'
    for attempt in range(3):  # Retry up to 3 times
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
            data = response.json()
            return f"https://image.tmdb.org/t/p/w500/{data['poster_path']}"
        except (ConnectionError, Timeout) as e:
            st.warning(f"Network issue: {e}. Retrying ({attempt+1}/3)...")
            time.sleep(2)  # Wait for 2 seconds before retrying
        except RequestException as e:
            st.error(f"An error occurred: {e}")
            return None
    st.error("Failed to fetch poster after 3 attempts.")
    return None

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movie_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        poster = fetch_poster(movie_id)
        if poster:
            recommended_movie_posters.append(poster)
        else:
            recommended_movie_posters.append('')  # Append an empty string if poster fetch failed

    return recommended_movies, recommended_movie_posters

st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://miro.medium.com/v2/resize:fit:1100/format:webp/0*Jb306SqcT0f-5ZFe");
        background-size: cover;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.header('Movie Recommender System')
movie_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movie_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    names, posters = recommend(selected_movie)
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            if posters[idx]:  # Only display if poster URL is valid
                st.image(posters[idx])
            st.text(names[idx])
