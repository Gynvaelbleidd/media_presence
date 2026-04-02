#!/usr/bin/env python3
"""
Media Rich Presence for Discord
Displays what you're watching with TMDB integration.

Setup:
1. Create a Discord Application at https://discord.com/developers/applications
2. Get a TMDB API key at https://www.themoviedb.org/settings/api
3. Copy config.example.txt to config.txt and fill in your credentials
   (or set DISCORD_APP_ID and TMDB_API_KEY environment variables)
"""

import os
import re
import sys
import time
import requests
from pypresence import Presence

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"


def load_config():
    """Load DISCORD_APP_ID and TMDB_API_KEY from config.txt or environment variables."""
    config = {}
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.txt")

    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip()
                    if value:
                        config[key] = value

    discord_app_id = config.get("DISCORD_APP_ID") or os.getenv("DISCORD_APP_ID")
    tmdb_api_key = config.get("TMDB_API_KEY") or os.getenv("TMDB_API_KEY")

    if not discord_app_id:
        print("✗ Error: DISCORD_APP_ID is not set.")
        print("  Set it in config.txt or as an environment variable.")
        print("  Create a Discord Application at https://discord.com/developers/applications")
        sys.exit(1)

    if not tmdb_api_key:
        print("✗ Error: TMDB_API_KEY is not set.")
        print("  Set it in config.txt or as an environment variable.")
        print("  Get an API key at https://www.themoviedb.org/settings/api")
        sys.exit(1)

    return discord_app_id, tmdb_api_key


DISCORD_APP_ID, TMDB_API_KEY = load_config()


class MoviePresence:
    def __init__(self):
        self.rpc = None
        self.connected = False
        self.current_movie = None
        self.start_time = None

    def connect(self):
        try:
            self.rpc = Presence(DISCORD_APP_ID)
            self.rpc.connect()
            self.connected = True
            print("✓ Connected to Discord")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to Discord: {e}")
            print("  Make sure Discord is running and your App ID is correct.")
            return False

    def disconnect(self):
        if self.rpc:
            try:
                self.rpc.close()
            except:
                pass
        self.connected = False

    def search_movie(self, query: str, year: int = None) -> dict | None:
        params = {
            "api_key": TMDB_API_KEY,
            "query": query,
            "include_adult": "true"
        }
        if year:
            params["year"] = year
        try:
            response = requests.get(f"{TMDB_BASE_URL}/search/movie", params=params)
            response.raise_for_status()
            results = response.json().get("results", [])
            if not results:
                return None
            return results[0]
        except Exception as e:
            print(f"✗ TMDB search failed: {e}")
            return None

    def get_movie_details(self, movie_id: int) -> dict | None:
        params = {"api_key": TMDB_API_KEY}
        try:
            response = requests.get(f"{TMDB_BASE_URL}/movie/{movie_id}", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"✗ Failed to get movie details: {e}")
            return None

    def set_movie(self, title: str, year: int = None, tmdb_id: int = None) -> bool:
        if not self.connected:
            print("✗ Not connected to Discord")
            return False
        if tmdb_id:
            print(f"Fetching TMDB ID: {tmdb_id}")
            movie = self.get_movie_details(tmdb_id)
        else:
            print(f"Searching for: {title}" + (f" ({year})" if year else ""))
            search_result = self.search_movie(title, year)
            if not search_result:
                print(f"✗ Movie not found: {title}")
                return False
            movie = self.get_movie_details(search_result["id"])
        if not movie:
            return False

        self.current_movie = movie
        self.start_time = int(time.time())

        movie_title = movie.get("title", title)
        release_year = movie.get("release_date", "")[:4]
        runtime = movie.get("runtime", 0)
        rating = movie.get("vote_average", 0)
        poster_path = movie.get("poster_path")

        details = movie_title
        if release_year:
            details = f"{movie_title} ({release_year})"

        state_parts = []
        if runtime:
            hours, mins = divmod(runtime, 60)
            if hours:
                state_parts.append(f"{hours}h {mins}m")
            else:
                state_parts.append(f"{mins}m")
        if rating:
            state_parts.append(f"★ {rating:.1f}")
        state = " • ".join(state_parts) if state_parts else "Watching"

        presence_kwargs = {
            "details": details[:128],
            "state": state[:128],
            "start": self.start_time,
        }

        if poster_path:
            presence_kwargs["large_image"] = f"{TMDB_IMAGE_BASE}{poster_path}"
            presence_kwargs["large_text"] = movie.get("tagline", movie_title)[:128] or movie_title

        presence_kwargs["small_image"] = "watching"
        presence_kwargs["small_text"] = "Watching"

        try:
            self.rpc.update(**presence_kwargs)
            print(f"✓ Now showing: {details}")
            if runtime:
                print(f"  Runtime: {runtime} minutes")
            if rating:
                print(f"  Rating: {rating:.1f}/10")
            return True
        except Exception as e:
            print(f"✗ Failed to update presence: {e}")
            return False

    def search_tv(self, query: str, year: int = None) -> dict | None:
        params = {
            "api_key": TMDB_API_KEY,
            "query": query,
            "include_adult": "true"
        }
        if year:
            params["first_air_date_year"] = year
        try:
            response = requests.get(f"{TMDB_BASE_URL}/search/tv", params=params)
            response.raise_for_status()
            results = response.json().get("results", [])
            if not results:
                return None
            return results[0]
        except Exception as e:
            print(f"✗ TMDB search failed: {e}")
            return None

    def get_tv_details(self, tv_id: int) -> dict | None:
        params = {"api_key": TMDB_API_KEY}
        try:
            response = requests.get(f"{TMDB_BASE_URL}/tv/{tv_id}", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"✗ Failed to get TV show details: {e}")
            return None

    def set_tv(self, title: str, year: int = None, season: int = None, tmdb_id: int = None) -> bool:
        if not self.connected:
            print("✗ Not connected to Discord")
            return False
        if tmdb_id:
            print(f"Fetching TMDB ID: {tmdb_id}")
            show = self.get_tv_details(tmdb_id)
        else:
            print(f"Searching for: {title}" + (f" ({year})" if year else ""))
            search_result = self.search_tv(title, year)
            if not search_result:
                print(f"✗ TV show not found: {title}")
                return False
            show = self.get_tv_details(search_result["id"])
        if not show:
            return False

        self.current_movie = show
        self.start_time = int(time.time())

        show_title = show.get("name", title)
        first_air_year = show.get("first_air_date", "")[:4]
        rating = show.get("vote_average", 0)
        poster_path = show.get("poster_path")

        details = show_title
        if first_air_year:
            details = f"{show_title} ({first_air_year})"

        state_parts = []
        if season:
            state_parts.append(f"Season {season}")
        if rating:
            state_parts.append(f"★ {rating:.1f}")
        state = " • ".join(state_parts) if state_parts else "Watching"

        presence_kwargs = {
            "details": details[:128],
            "state": state[:128],
            "start": self.start_time,
        }

        if poster_path:
            presence_kwargs["large_image"] = f"{TMDB_IMAGE_BASE}{poster_path}"
            presence_kwargs["large_text"] = show.get("tagline", show_title)[:128] or show_title

        presence_kwargs["small_image"] = "watching"
        presence_kwargs["small_text"] = "Watching"

        try:
            self.rpc.update(**presence_kwargs)
            print(f"✓ Now showing: {details}")
            if season:
                print(f"  Season: {season}")
            if rating:
                print(f"  Rating: {rating:.1f}/10")
            return True
        except Exception as e:
            print(f"✗ Failed to update presence: {e}")
            return False

    def clear(self):
        if self.rpc and self.connected:
            try:
                self.rpc.clear()
                self.current_movie = None
                self.start_time = None
                print("✓ Presence cleared")
            except Exception as e:
                print(f"✗ Failed to clear presence: {e}")


def parse_tv_input(raw: str) -> tuple[str, int | None, int | None]:
    """Parse TV input string. Returns (title, year, season)."""
    season = None
    year = None
    text = raw.strip()

    # Check last parenthesized group for season (SN)
    if text.endswith(")") and "(" in text:
        paren_start = text.rfind("(")
        inner = text[paren_start + 1:-1].strip()
        season_match = re.match(r'^[Ss](\d+)$', inner)
        if season_match:
            season = int(season_match.group(1))
            text = text[:paren_start].strip()

    # Check (now last) parenthesized group for year
    if text.endswith(")") and "(" in text:
        paren_start = text.rfind("(")
        inner = text[paren_start + 1:-1].strip()
        if inner.isdigit() and len(inner) == 4:
            year = int(inner)
            text = text[:paren_start].strip()

    return text, year, season


def interactive_mode(mp: MoviePresence):
    print("\n" + "=" * 50)
    print("Media Rich Presence - Interactive Mode")
    print("=" * 50)
    print("Commands:")
    print("  <movie title>        - Set movie (e.g., 'Casino Royale')")
    print("  <title> (year)       - Set movie with year (e.g., 'Casino Royale (2006)')")
    print("  id:<tmdb_id>         - Set movie by TMDB ID (e.g., 'id:36557')")
    print("  clear                - Clear presence")
    print("  quit / exit          - Exit program")
    print("=" * 50 + "\n")

    while True:
        try:
            user_input = input("Movie > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "q"):
                break
            if user_input.lower() == "clear":
                mp.clear()
                continue
            if user_input.lower().startswith("id:"):
                try:
                    tmdb_id = int(user_input[3:].strip())
                    mp.set_movie(None, None, tmdb_id)
                    continue
                except ValueError:
                    print("✗ Invalid TMDB ID")
                    continue
            if user_input.isdigit():
                mp.set_movie(None, None, int(user_input))
                continue
            year = None
            title = user_input
            if user_input.endswith(")") and "(" in user_input:
                try:
                    year_start = user_input.rfind("(")
                    year_str = user_input[year_start + 1:-1].strip()
                    if year_str.isdigit() and len(year_str) == 4:
                        year = int(year_str)
                        title = user_input[:year_start].strip()
                except:
                    pass
            mp.set_movie(title, year)
        except KeyboardInterrupt:
            print("\n")
            break
        except EOFError:
            break

    mp.clear()
    mp.disconnect()
    print("Goodbye!")


def tv_interactive_mode(mp: MoviePresence):
    print("\n" + "=" * 50)
    print("Media Rich Presence - TV Mode")
    print("=" * 50)
    print("Commands:")
    print("  <show title>            - Set show (e.g., 'Breaking Bad')")
    print("  <title> (year)          - With year (e.g., 'Breaking Bad (2008)')")
    print("  <title> (SN)            - With season (e.g., 'Breaking Bad (S3)')")
    print("  <title> (year) (SN)     - Both (e.g., 'Breaking Bad (2008) (S3)')")
    print("  id:<tmdb_id>            - Set show by TMDB ID (e.g., 'id:1396')")
    print("  clear                   - Clear presence")
    print("  quit / exit             - Exit program")
    print("=" * 50 + "\n")

    while True:
        try:
            user_input = input("TV > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "q"):
                break
            if user_input.lower() == "clear":
                mp.clear()
                continue
            if user_input.lower().startswith("id:"):
                try:
                    tmdb_id = int(user_input[3:].strip())
                    mp.set_tv(None, None, None, tmdb_id)
                    continue
                except ValueError:
                    print("✗ Invalid TMDB ID")
                    continue
            if user_input.isdigit():
                mp.set_tv(None, None, None, int(user_input))
                continue
            title, year, season = parse_tv_input(user_input)
            mp.set_tv(title, year, season)
        except KeyboardInterrupt:
            print("\n")
            break
        except EOFError:
            break

    mp.clear()
    mp.disconnect()
    print("Goodbye!")


def select_media_type() -> str:
    """Prompt user to select media type."""
    print("\nSelect media type:")
    print("  movie")
    print("  tv")
    while True:
        choice = input("> ").strip().lower()
        if choice in ("movie", "tv"):
            return choice
        print("Please enter 'movie' or 'tv'.")


def _cli_movie(mp: MoviePresence, query: str):
    """Handle CLI mode for movies."""
    tmdb_id = None
    if query.lower().startswith("id:"):
        try:
            tmdb_id = int(query[3:].strip())
        except ValueError:
            print("✗ Invalid TMDB ID")
            sys.exit(1)
    elif query.isdigit():
        tmdb_id = int(query)
    if tmdb_id:
        if mp.set_movie(None, None, tmdb_id):
            print("\nPress Ctrl+C to exit and clear presence...")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n")
        mp.clear()
        mp.disconnect()
        return
    year = None
    title = query
    if query.endswith(")") and "(" in query:
        try:
            year_start = query.rfind("(")
            year_str = query[year_start + 1:-1].strip()
            if year_str.isdigit() and len(year_str) == 4:
                year = int(year_str)
                title = query[:year_start].strip()
        except:
            pass
    if mp.set_movie(title, year):
        print("\nPress Ctrl+C to exit and clear presence...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n")
    mp.clear()
    mp.disconnect()


def _cli_tv(mp: MoviePresence, query: str):
    """Handle CLI mode for TV shows."""
    tmdb_id = None
    if query.lower().startswith("id:"):
        try:
            tmdb_id = int(query[3:].strip())
        except ValueError:
            print("✗ Invalid TMDB ID")
            sys.exit(1)
    elif query.isdigit():
        tmdb_id = int(query)
    if tmdb_id:
        if mp.set_tv(None, None, None, tmdb_id):
            print("\nPress Ctrl+C to exit and clear presence...")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n")
        mp.clear()
        mp.disconnect()
        return
    title, year, season = parse_tv_input(query)
    if mp.set_tv(title, year, season):
        print("\nPress Ctrl+C to exit and clear presence...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n")
    mp.clear()
    mp.disconnect()


def main():
    mp = MoviePresence()
    if not mp.connect():
        sys.exit(1)

    if len(sys.argv) > 1:
        raw_args = " ".join(sys.argv[1:])

        if raw_args.lower().startswith("movie:"):
            _cli_movie(mp, raw_args[6:].strip())
        elif raw_args.lower().startswith("tv:"):
            _cli_tv(mp, raw_args[3:].strip())
        else:
            _cli_movie(mp, raw_args)
    else:
        media_type = select_media_type()
        if media_type == "movie":
            interactive_mode(mp)
        else:
            tv_interactive_mode(mp)


if __name__ == "__main__":
    main()
