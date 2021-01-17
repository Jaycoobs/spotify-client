## spotify-client

### Before Using

This client requires spotify premium. 
This client does not function on Windows (yet...).
Before you can use it, you need to create an app on the developer
page so that you can give the client permission to act on your behalf.

1. Go to https://developer.spotify.com/dashboard/login and log in with
your spotify account.
2. Click 'Create An App'. You can name the app anything, but it should
be something that lets you know what the app is for. (I use 'terminal-client')
3. Once the app is created, click 'EDIT SETTINGS'
4. Add any valid URI (it doesn't need to be accessible) to the 'Redirect URIs'
list (such as 'http://localhost:9090') and then save.
5. Make a note of your *Redirect URI*, your app's *Client ID*, and your app's
*Client Secret*.
6. You can either put the *Redirect URI*, *Client ID*, and *Client Secret*
into the file called *config* or you can set the environment variables
*SPOTIPY_CLIENT_ID*, *SPOTIPY_CLIENT_SECRET*, and *SPOTIPY_REDIRECT_URI*.
7. Once the values are either set as environment variables or placed in the
config file, you can run the client with python.

### Dependencies

This client requires python 3.
The following can be installed with pip.

- spotipy       - Used to interface with spotify
- fuzzywuzzy    - Used for searching

### Usage

Run the client.py file.
When the client first starts, it will show a list of the user's saved tracks.

- You can navigate the list by using the up and down arrow keys or page up and
page down
- Press enter on a track to play that track. If the track was selected from a
playlist, the playlist will continue to play when the track is over
- Press the forward or back arrows to skip forward or back
- Press 'space' to play or pause playback
- Press 's' to toggle shuffle
- Press 'p' to view the user's playlists
- Press 'd' to view the devices available for playback
- Press 't' to return to the user's saved tracks
- Press '/' to search
- Press 'q' to exit the client
