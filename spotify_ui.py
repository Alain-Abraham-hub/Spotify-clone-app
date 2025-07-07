import streamlit as st
import mysql.connector
from datetime import datetime

# Database connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="spotify_user",
        password="spotify123",
        database="spotify"
    )

# Login / Signup
def login(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

def signup(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

# UI Begins
st.title("🎵 Spotify Clone")
menu = ["Login", "Signup"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Signup":
    st.subheader("Create Account")
    uname = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Sign Up"):
        if signup(uname, pwd):
            st.success("Account created!")
        else:
            st.error("Username already exists")

elif choice == "Login":
    st.subheader("Login")
    uname = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        user_id = login(uname, pwd)
        if user_id:
            st.success(f"Welcome, {uname}!")
            st.session_state.logged_in = True
            st.session_state.user_id = user_id
        else:
            st.error("Invalid credentials")

if st.session_state.get("logged_in", False):

    tab = st.selectbox("Actions", [
        "View Songs", "Add Song", "Search Song",
        "Create Playlist", "View My Playlists", "Add Song to Playlist", "Delete Playlist"
    ])

    conn = get_connection()
    cursor = conn.cursor()

    if tab == "View Songs":
        cursor.execute("SELECT title, artist, genre, album, release_year, duration FROM songs")
        songs = cursor.fetchall()
        for song in songs:
            st.write(f"🎶 {song[0]} by {song[1]} | Genre: {song[2]} | Album: {song[3]} | Year: {song[4]} | Duration: {song[5]}")

    elif tab == "Add Song":
        st.subheader("Add New Song")
        title = st.text_input("Title")
        artist = st.text_input("Artist")
        genre = st.text_input("Genre")
        album = st.text_input("Album")
        release_year = st.number_input("Release Year", 1900, 2100)
        duration = st.time_input("Duration (HH:MM:SS)")
        if st.button("Add Song"):
            cursor.execute(
                "INSERT INTO songs (title, artist, genre, album, release_year, duration) VALUES (%s, %s, %s, %s, %s, %s)",
                (title, artist, genre, album, release_year, duration))
            conn.commit()
            st.success("Song added!")

    elif tab == "Search Song":
        search = st.text_input("Search by Title or Artist")
        if st.button("Search"):
            cursor.execute("SELECT title, artist, genre, album, release_year FROM songs WHERE title LIKE %s OR artist LIKE %s",
                           (f"%{search}%", f"%{search}%"))
            results = cursor.fetchall()
            if results:
                for song in results:
                    st.write(f"{song[0]} by {song[1]} | Genre: {song[2]} | Album: {song[3]} | Year: {song[4]}")
            else:
                st.warning("No results found.")

    elif tab == "Create Playlist":
        playlist_name = st.text_input("Playlist Name")
        if st.button("Create"):
            cursor.execute("INSERT INTO playlists (name, user_id) VALUES (%s, %s)", (playlist_name, st.session_state.user_id))
            conn.commit()
            st.success("Playlist created!")

    elif tab == "View My Playlists":
        cursor.execute("SELECT playlist_id, name FROM playlists WHERE user_id = %s", (st.session_state.user_id,))
        playlists = cursor.fetchall()
        for pl in playlists:
            st.write(f"🎵 {pl[1]} (ID: {pl[0]})")
            cursor.execute("""
                SELECT s.title, s.artist FROM songs s
                JOIN playlist_songs ps ON s.song_id = ps.song_id
                WHERE ps.playlist_id = %s
            """, (pl[0],))
            songs = cursor.fetchall()
            for song in songs:
                st.write(f" - {song[0]} by {song[1]}")

    elif tab == "Add Song to Playlist":
        song_id = st.number_input("Song ID", min_value=1)
        playlist_id = st.number_input("Playlist ID", min_value=1)
        if st.button("Add to Playlist"):
            cursor.execute("INSERT INTO playlist_songs (playlist_id, song_id) VALUES (%s, %s)", (playlist_id, song_id))
            conn.commit()
            st.success("Added to playlist!")

    elif tab == "Delete Playlist":
        playlist_id = st.number_input("Playlist ID to delete", min_value=1)
        if st.button("Delete Playlist"):
            cursor.execute("DELETE FROM playlists WHERE playlist_id = %s AND user_id = %s", (playlist_id, st.session_state.user_id))
            conn.commit()
            st.success("Playlist deleted!")

    conn.close()