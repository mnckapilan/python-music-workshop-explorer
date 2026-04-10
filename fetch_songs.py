# ============================================================
#  🐉 HERE BE DRAGONS
# ============================================================
#  This file is for workshop setup only.
#  You don't need to run or understand it to do the exercises.
#
#  What it's doing:
#    This script talks to Apple's iTunes Search API — a free
#    service on the internet that knows about millions of songs.
#    It fetches up to 200 tracks for each of 50 artists, tidies
#    up the data (genre, duration, BPM etc.), then saves
#    everything to data/songs.json.
#
#    It uses urllib to make web requests, json to read the
#    responses, and pathlib to save the file. These are concepts
#    from well beyond Exercise 7!
#
#  To refresh the song library (your teacher will do this):
#      python3 data/fetch_songs.py
# ============================================================

import json
import random
import time
import urllib.parse
import urllib.request
from pathlib import Path

# 65 artists — prioritising current UK/English-world student relatability
ARTISTS = [
    # Current / recent — artists students are streaming right now
    "Sabrina Carpenter",
    "Chappell Roan",
    "Charli XCX",
    "Olivia Dean",
    "Gracie Abrams",
    "Tate McRae",
    "Noah Kahan",
    "Hozier",
    "Benson Boone",
    "Teddy Swims",
    "Lana Del Rey",
    "Conan Gray",
    "Doechii",
    "Ice Spice",
    "Megan Thee Stallion",
    # Established pop — massively relevant
    "Taylor Swift",
    "Ed Sheeran",
    "Dua Lipa",
    "Ariana Grande",
    "Harry Styles",
    "Olivia Rodrigo",
    "Billie Eilish",
    "Lady Gaga",
    "Adele",
    "Bruno Mars",
    "Justin Bieber",
    "Doja Cat",
    "Lizzo",
    # Hip-Hop / R&B — artists teens actually know
    "Drake",
    "Kendrick Lamar",
    "Tyler the Creator",
    "SZA",
    "The Weeknd",
    "Beyoncé",
    "Rihanna",
    "Post Malone",
    "Travis Scott",
    "J. Cole",
    "21 Savage",
    "Future",
    "Frank Ocean",
    "Usher",
    "Eminem",
    "Nicki Minaj",
    "Cardi B",
    "Lil Baby",
    "Gunna",
    "Victoria Monet",
    "Summer Walker",
    # Rock / Indie / Alternative
    "Arctic Monkeys",
    "Coldplay",
    "The 1975",
    "The Killers",
    "Tame Impala",
    "Glass Animals",
    "Sam Fender",
    "Wet Leg",
    # UK — grime, UK R&B, UK pop
    "Central Cee",
    "Dave",
    "Stormzy",
    "Little Simz",
    "Jorja Smith",
    "RAYE",
    "PinkPantheress",
    # Timeless but still taught and played
    "Michael Jackson",
    "Amy Winehouse",
    "Oasis",
    "Kanye West",
    # By request
    "Bad Bunny",
    "Janelle Monae",
]

assert len(ARTISTS) == 70, f"Expected 70 artists, got {len(ARTISTS)}"

# iTunes hard limit per search request
ITUNES_LIMIT = 200

# Realistic BPM ranges by genre (primaryGenreName)
BPM_RANGES = {
    "Pop":               (100, 130),
    "Hip-Hop/Rap":       (80,  105),
    "R&B/Soul":          (65,  100),
    "Dance":             (120, 145),
    "Electronic":        (120, 140),
    "Rock":              (110, 140),
    "Alternative":       (100, 130),
    "Country":           (88,  120),
    "Indie Pop":         (90,  125),
    "Singer/Songwriter": (75,  115),
    "Soul":              (65,  100),
    "Rap":               (80,  105),
    "Latin":             (95,  135),
    "Reggae":            (60,   90),
    "K-Pop":             (105, 135),
    "Soundtrack":        (80,  120),
    "Holiday":           (90,  130),
    "Classical":         (60,  180),
    "Jazz":              (70,  180),
}
DEFAULT_BPM_RANGE = (90, 130)


def bpm_for_genre(genre: str) -> int:
    for key, (lo, hi) in BPM_RANGES.items():
        if key.lower() in genre.lower():
            return random.randint(lo, hi)
    return random.randint(*DEFAULT_BPM_RANGE)


def fetch_artist_tracks(artist: str) -> list[dict]:
    params = urllib.parse.urlencode({
        "term":    artist,
        "entity":  "song",
        "limit":   ITUNES_LIMIT,
        "country": "US",
    })
    url = f"https://itunes.apple.com/search?{params}"
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=15) as resp:
                return json.loads(resp.read()).get("results", [])
        except Exception as exc:
            if attempt == 2:
                print(f"  ✗ Giving up: {exc}")
                return []
            print(f"  Retry {attempt + 1}…")
            time.sleep(2)
    return []


def normalise(raw: dict) -> dict:
    genre    = raw.get("primaryGenreName", "Pop")
    track_exp      = raw.get("trackExplicitness", "notExplicit")
    collection_exp = raw.get("collectionExplicitness", "notExplicit")
    explicit = track_exp in ("explicit", "cleaned") or collection_exp == "explicit"
    duration = round(raw.get("trackTimeMillis", 0) / 60000, 2)
    year     = int(raw.get("releaseDate", "2020")[:4])
    return {
        "title":      raw["trackName"],
        "artist":     raw["artistName"],
        "album":      raw.get("collectionName", "Unknown Album"),
        "year":       year,
        "genre":      genre,
        "duration":   duration,
        "explicit":   explicit,
        "bpm":        bpm_for_genre(genre),
        "play_count": random.randint(50, 500),
    }


def main():
    random.seed(42)
    songs: list[dict] = []
    seen:  set[tuple] = set()   # (title_lower, artist_lower)

    for i, artist in enumerate(ARTISTS, 1):
        print(f"[{i:2}/{len(ARTISTS)}] {artist}…", end=" ", flush=True)
        raw_tracks = fetch_artist_tracks(artist)

        added = 0
        for raw in raw_tracks:
            if raw.get("kind") != "song":
                continue
            song = normalise(raw)
            key  = (song["title"].lower(), song["artist"].lower())
            if key not in seen:
                seen.add(key)
                songs.append(song)
                added += 1

        print(f"{added} added  (total: {len(songs)})")
        time.sleep(0.4)   # stay polite to the API

    out_path = Path(__file__).parent / "songs.json"
    out_path.write_text(json.dumps(songs, indent=2, ensure_ascii=False))
    print(f"\nDone. Saved {len(songs)} songs → {out_path}")


if __name__ == "__main__":
    main()
