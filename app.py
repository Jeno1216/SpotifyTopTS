from flask import Flask, request, url_for, session, redirect, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import uuid

CLIENT_ID = "86a224772b124b51989123bed131d2e4"
CLIENT_SECRET = "57da38d12b31449a80df5b37256d7a29"
SECRET_KEY = "your-secret-key"
TOKEN_CODE = "token_info"
MEDIUM_TERM = "medium_term"
SHORT_TERM = "short_term"
LONG_TERM = "long_term"

app = Flask(__name__)

# Generate a unique session key for each user using UUID
def generate_secret_key():
    return str(uuid.uuid4())

# Use the IP address as a session key for separate sessions
def get_session_key():
    return str(request.remote_addr)

# Create a SpotifyOAuth instance with the required credentials
def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=url_for("redirectPage", _external=True),
        scope="user-top-read user-library-read user-read-recently-played"
    )

@app.route('/')
def index():
    name = 'username'
    return render_template('index.html', title='Welcome', username=name)

@app.route('/login')
def login():
    sp_oauth = create_spotify_oauth()

    # Get a unique session key for the user
    session_key = get_session_key()

    # Set the session secret key based on the session key
    app.secret_key = f'SECRET_KEY_{session_key}'

    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_CODE] = token_info
    return redirect(url_for("getTracks", _external=True))

def get_token():
    sp_oauth = create_spotify_oauth()
    token_info = session.get(TOKEN_CODE, None)

    if not token_info:
        raise Exception("User not logged in")

    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60

    if is_expired:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session[TOKEN_CODE] = token_info

    return token_info

@app.route('/getTracks')
def getTracks():
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect("/")

    sp = spotipy.Spotify(auth=token_info['access_token'])
    current_user_name = sp.current_user()['display_name']

    # Replace 'YOUR_TAYLOR_SWIFT_SPOTIFY_ID' with Taylor Swift's Spotify ID.
    taylor_swift_id = '06HL4z0CvFAxyc27GXpf02'

    # Get the user's top tracks for different time ranges
    long_term_tracks = sp.current_user_top_tracks(limit=1000, time_range=LONG_TERM)
    medium_term_tracks = sp.current_user_top_tracks(limit=1000, time_range=MEDIUM_TERM)
    short_term_tracks = sp.current_user_top_tracks(limit=1000, time_range=SHORT_TERM)

    # Filter the top tracks to get Taylor Swift's tracks for each time range
    long_term_taylor_swift_tracks = [track for track in long_term_tracks['items'] if any(artist['id'] == taylor_swift_id for artist in track['artists'])]
    medium_term_taylor_swift_tracks = [track for track in medium_term_tracks['items'] if any(artist['id'] == taylor_swift_id for artist in track['artists'])]
    short_term_taylor_swift_tracks = [track for track in short_term_tracks['items'] if any(artist['id'] == taylor_swift_id for artist in track['artists'])]

    # Take the top 10 Taylor Swift tracks for the long-term
    short_term_songs = short_term_taylor_swift_tracks[:10]
    medium_term_songs = medium_term_taylor_swift_tracks[:10]
    long_term_songs = long_term_taylor_swift_tracks[:10]

    return render_template(
        'receipt.html',
        user_display_name=current_user_name,
        long_term_songs=long_term_songs,
        medium_term_songs=medium_term_songs,
        short_term_songs=short_term_songs,
        currentTime=gmtime()
    )

if __name__ == '__main__':
    app.run(debug=True)
