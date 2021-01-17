#! /usr/bin/env python

import spotipy
from spotipy.oauth2 import SpotifyOAuth

import unicodedata

from fuzzywuzzy import process

import display
from menu import Menu

import sys, tty, termios

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def strlen(s):
    return sum(1 + (unicodedata.east_asian_width(c) in "WFA") for c in s)

def fixlength(s, l):
    pad = l - strlen(s)

    if (pad < 0):
        return ellipsize(s, l)

    return s + (" " * pad)

def ellipsize(s, l):
    r = strlen(s)
    if (r > l):
        return s[:(l-r-3)] + "..."
    return s

def search(searchText, it):
    if (searchText == ""):
        return it
    searchable = [i.getSearchableText() for i in it]
    results = process.extract(searchText, searchable, limit=len(searchable))
    results = [it[searchable.index(i[0])] for i in results]
    return results

def getDevices(sp):
    results = sp.devices()
    return [Device(r) for r in results["devices"]]

class Track:

    def __init__(self, track):
        self.track = track

    def getName(self):
        return self.track["name"]

    def getAlbumName(self):
        return self.track["album"]["name"]

    def getPrimaryArtistName(self):
        return self.track["artists"][0]["name"]

    def getUri(self):
        return self.track["uri"]

    def getMenuText(self, lineLength=80):
        trackLength = lineLength // 3 - 1
        albumLength = lineLength // 3 - 1
        artistLength = lineLength // 3
        return "%s %s %s" % (fixlength(self.getName(), trackLength),\
                               fixlength(self.getAlbumName(), albumLength),\
                               fixlength(self.getPrimaryArtistName(), artistLength))

    def getSearchableText(self):
        return self.getName() + self.getAlbumName() + self.getPrimaryArtistName()

class Playlist:

    def __init__(self, sp, playlist):
        self.sp = sp
        self.playlist = playlist
        self.tracks = []
        self.total = 0

    def getName(self):
        return self.playlist["name"]

    def getId(self):
        return self.playlist["id"]

    def getUri(self):
        return self.playlist["uri"]

    def getMenuText(self, lineLength=80):
        return self.getName()

    def getSearchableText():
        return self.getName()

    def __iter__(self):
        self.offset = 0
        return self

    def __next__(self):
        self.offset += 1
        try:
            return self[self.offset - 1]
        except IndexError:
            raise StopIteration

    def __getitem__(self, n):
        while (len(self.tracks) <= n and (self.total == 0 or len(self.tracks) < self.total)):
            results = self.sp.playlist_tracks(self.getId())
            for item in results["items"]:
                self.tracks.append(Track(item["track"]))
            self.total = int(results["total"])
        return self.tracks[n]

    def __len__(self):
        if (not self.total):
            results = self.sp.playlist_tracks(self.getId(), limit=1)
            self.total = int(results["total"])
        return self.total

class Device:

    def __init__(self, device):
        self.device = device

    def getName(self):
        return self.device["name"]

    def getId(self):
        return self.device["id"]

    def getMenuText(self, lineLength=80):
        return self.getName()

    def getSearchableText(self):
        return self.getName()

class Playlists:

    def __init__(self, sp):
        self.sp = sp
        self.playlists = []
        self.offset = 0
        self.total = None

    def __iter__(self):
        self.offset = 0
        return self

    def __next__(self):
        self.offset += 1
        try:
            return self[self.offset - 1]
        except IndexError:
            raise StopIteration

    def __getitem__(self, n):
        while (len(self.playlists) <= n and (self.total == 0 or len(self.playlists) < self.total)):
            results = self.sp.current_user_playlists()
            for item in results["items"]:
                self.playlists.append(Playlist(self.sp, item))
            self.total = int(results["total"])
        return self.playlists[n]

    def __len__(self):
        if (not self.total):
            results = self.sp.current_user_playlists(limit=1)
            self.total = int(results["total"])
        return self.total

class SavedTracks:

    def __init__(self, sp):
        self.sp = sp
        self.tracks = []
        self.offset = 0
        self.total = None

    def __iter__(self):
        self.offset = 0
        return self

    def __next__(self):
        self.offset += 1
        try:
            return self[self.offset - 1]
        except IndexError:
            raise StopIteration

    def __getitem__(self, n):
        while (len(self.tracks) <= n and (self.total == 0 or len(self.tracks) < self.total)):
            results = self.sp.current_user_saved_tracks(offset=len(self.tracks))
            for item in results["items"]:
                self.tracks.append(Track(item["track"]))
            self.total = int(results["total"])
        return self.tracks[n]

    def __len__(self):
        if (not self.total):
            results = self.sp.current_user_saved_tracks(limit=1)
            self.total = int(results["total"])
        return self.total

class Client:

    def __init__(self, sp):
        self.running = True
        self.sp = sp

        try:
            self.device = getDevices(sp)[0]
        except IndexError:
            self.device = None

        self.savedTracks = SavedTracks(sp)
        self.playlists = Playlists(sp)

        self.currentContext = self.savedTracks
        self.menu = Menu(options=self.currentContext)

        self.searchText = ""
        self.messageText = ""

        self.messageLine = 7
        self.contextLine = self.messageLine + 1
        self.searchLine = self.contextLine + 1
        self.labelLine = self.searchLine + 2
        self.menuStart = self.labelLine + 1

    def playTrack(self, track):
        if (not self.device):
            return
        if (type(self.currentContext) == Playlist):
            self.sp.start_playback(device_id=self.device.getId(),\
                                   offset={"uri":track.getUri()},\
                                   context_uri=self.currentContext.getUri())
        else:
            self.sp.start_playback(device_id=self.device.getId(),\
                                   uris=[track.getUri()])

    def getPlaybackState(self):
        return self.sp.current_playback()

    def play(self):
        self.sp.start_playback()
        self.setMessage("PLAYBACK STARTED")

    def pause(self):
        self.sp.pause_playback()
        self.setMessage("PLAYBACK PAUSED")

    def queueTrack(self, track):
        self.sp.add_to_queue(track.getUri())
        self.setMessage("ADDED %s TO THE QUEUE" % (track.getName()))

    def skip(self):
        self.sp.next_track()

    def prev(self):
        self.sp.previous_track()

    def shuffle(self, state):
        self.sp.shuffle(state)
        self.setMessage("SHUFFLE " + ("ON" if state else "OFF"))

    def setDevice(self, device):
        self.device = device
        p = self.getPlaybackState()
        if (p and self.getPlaybackState()["is_playing"]):
            self.sp.transfer_playback(device.getId())
        self.setMessage("USING DEVICE: " + device.getName())

    def clearMenu(self):
        display.moveCursor(self.menuStart, 0)
        display.clearScreen()

    def getSearchInput(self):
        display.showCursor()
        display.moveCursor(self.searchLine,0)
        display.clearLine()
        i = input("SEARCH / ")
        display.hideCursor()
        return i

    def setMessage(self, message):
        self.messageText = message

    def updateDisplay(self):
        termSize = display.getTerminalSize()

        display.moveCursor(1,0)
        display.setBold()
        print("\
\033[K  ____ ___  ____     ____ _     ___ _____ _   _ _____\n\
\033[K / ___/ _ \| __ )   / ___| |   |_ _| ____| \ | |_   _|\n\
\033[K| |  | | | |  _ \  | |   | |    | ||  _| |  \| | | |\n\
\033[K| |__| |_| | |_) | | |___| |___ | || |___| |\  | | |\n\
\033[K \____\___/|____/   \____|_____|___|_____|_| \_| |_|\n\
\033[K")
        display.clearAttributes()

        for i in range(self.messageLine, self.menuStart+1):
            display.moveCursor(i, 0)
            display.clearLine()

        display.moveCursor(self.messageLine, 0)
        display.clearLine()
        print(self.messageText)

        display.moveCursor(self.contextLine, 0)
        display.clearLine()
        if (type(self.currentContext) == SavedTracks):
            print("SAVED TRACKS")
        if (type(self.currentContext) == Playlist):
            print("PLAYLIST: " + self.currentContext.getName())
        if (type(self.currentContext) == Playlists):
            print("USER PLAYLISTS")

        display.setInverted()
        display.moveCursor(self.labelLine, 0)
        display.clearLine()
        if (type(self.currentContext) == SavedTracks or type(self.currentContext) == Playlist):
            trackLength = termSize[1] // 3
            albumLength = termSize[1] // 3
            artistLength = termSize[1] // 3
            print("%s%s%s" % (fixlength("TRACK", trackLength),\
                               fixlength("ALBUM", albumLength),\
                               fixlength("ARTIST", artistLength)))
        elif (type(self.currentContext) == Playlists):
            print("PLAYLIST NAME")
        display.clearAttributes()

        self.menu.setViewSize(termSize[0] - self.menuStart - 2)
        self.menu.print(top=self.menuStart)

    def processInput(self):
        termSize = display.getTerminalSize()

        c = getch()
        if (c == "\033"):
            getch() # Discard the [
            c = getch()
            if (c == "A"):
                self.menu.selectionUp()
            elif (c == "B"):
                self.menu.selectionDown()
            elif (c == "C"):
                self.skip()
            elif (c == "D"):
                self.prev()
            elif (c == "5"):
                self.menu.selectionUp(self.menu.viewSize)
                getch() # Discard the ~
            elif (c == "6"):
                self.menu.selectionDown(self.menu.viewSize)
                getch() # Discard the ~
        elif (c == "q"):
            self.running = False
        elif (c == "d"):
            self.clearMenu()
            self.currentContext = getDevices(self.sp)
            self.menu = Menu(options=self.currentContext)
        elif (c == "t"):
            self.clearMenu()
            self.currentContext = self.savedTracks
            self.menu = Menu(options=self.currentContext)
        elif (c == "p"):
            self.clearMenu()
            self.currentContext = self.playlists
            self.menu = Menu(options=self.currentContext)
        elif (c == " "):
            p = self.getPlaybackState()
            if (p and p["is_playing"]):
                self.pause()
            else:
                self.play()
        elif (c == "s"):
            p = self.getPlaybackState()
            if (p):
                if (p["shuffle_state"]):
                    self.shuffle(False)
                else:
                    self.shuffle(True)
        elif (c == "e"):
            s = self.menu.getSelection()
            if (type(s) != Track):
                self.setMessage("ONLY TRACKS CAN BE QUEUED")
            else:
                self.queueTrack(s)
        elif (c == "\015"):
            s = self.menu.getSelection()
            if (type(s) == Track):
                self.playTrack(s)
            if (type(s) == Playlist):
                self.clearMenu()
                self.currentContext = s
                self.menu = Menu(options=self.currentContext)
            if (type(s) == Device):
                self.setDevice(s)
        elif (c == "/"):
            self.searchText = self.getSearchInput()
            self.clearMenu()
            self.menu = Menu(options=search(self.searchText, self.currentContext))

    def start(self):
        display.hideCursor()
        display.moveCursor(0,0)
        display.clearScreen()
        while self.running:
            self.updateDisplay()

            try:
                self.processInput()
            except spotipy.exceptions.SpotifyException as e:
                if ("NO_ACTIVE_DEVICE" in e.reason):
                    self.setMessage("NO DEVICE SPECIFIED... PRESS d")
                else:
                    print("SPOTIFY EXCEPTION REASON: " + e.reason)
                    raise e
        display.showCursor()

if (__name__ == "__main__"):
    config = {}
    with open("config", "r") as f:
        for line in f:
            k = line.split("=")
            v = k[1]
            k = k[0]
            if (len(v) > 0):
                config[k] = v.strip()

    if (not "CLIENT_ID" in config):
        print("Config file is missing 'CLIENT_ID'")
        config["CLIENT_ID"] = None
    if (not "CLIENT_SECRET" in config):
        print("Config file is missing 'CLIENT_SECRET'")
        config["CLIENT_SECRET"] = None
    if (not "REDIRECT_URI" in config):
        print("Config file is missing 'REDIRECT_URI'")
        config["REDIRECT_URI"] = None

    scopes = "user-library-read user-modify-playback-state user-read-playback-state \
playlist-read-private playlist-read-collaborative"

    oauth = SpotifyOAuth(client_id=config["CLIENT_ID"],\
                         client_secret=config["CLIENT_SECRET"],\
                         redirect_uri=config["REDIRECT_URI"],\
                         scope=scopes)

    spotify = spotipy.Spotify(auth_manager=oauth)

    c = Client(spotify)
    c.start()
