from flask import Flask, request, url_for, session, redirect, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time 
from time import gmtime, strftime
import os

CLIENT_ID = "86a224772b124b51989123bed131d2e4"
CLIENT_SECRET = "57da38d12b31449a80df5b37256d7a29"
SECRET_KEY = "asdf"
TOKEN_CODE = "token_info"
MEDIUM_TERM = "medium_term"
SHORT_TERM = "short_term"
LONG_TERM = "long_term"

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=url_for("redirectPage",_external=True), 
        scope="user-top-read user-library-read user-read-recently-played"
    )

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SESSION_COOKIE_NAME'] = 'Eriks Cookie'

@app.route('/')
def index():
    name = 'username'
    return render_template('index.html', title='Welcome', username=name)

@app.route('/login')
def login():
    sp_oauth = create_spotify_oauth()
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
    token_info = session.get(TOKEN_CODE, None)
    if not token_info: 
        raise "exception"
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60 
    if (is_expired): 
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info 

@app.route('/getTracks')
def getTracks():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect("/")
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    
    # Replace 'YOUR_TAYLOR_SWIFT_SPOTIFY_ID' with Taylor Swift's Spotify ID.
    taylor_swift_id = '6HaGTQPmzraVmaVxvz6EUc'

    # Get the user's top tracks for the long-term
    top_tracks = sp.current_user_top_tracks(limit=1000, time_range=LONG_TERM)

    # Filter the top tracks to get Taylor Swift's tracks
    taylor_swift_tracks = [track for track in top_tracks['items'] if any(artist['id'] == taylor_swift_id for artist in track['artists'])]

    # Take the top 10 Taylor Swift tracks for the long-term
    top_10_taylor_swift_songs = taylor_swift_tracks[:10]

    return render_template('receipt.html', user_display_name="", songs=top_10_taylor_swift_songs, currentTime=gmtime())


@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    return strftime("%a, %d %b %Y", date)

@app.template_filter('mmss')
def _jinja2_filter_miliseconds(time, fmt=None):
    time = int(time / 1000)
    minutes = time // 60 
    seconds = time % 60 
    if seconds < 10: 
        return str(minutes) + ":0" + str(seconds)
    return str(minutes) + ":" + str(seconds ) 

if __name__ == '__main__':
    app.run(debug=True)