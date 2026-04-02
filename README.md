# Media Rich Presence

A Discord Rich Presence tool that displays what you're currently watching, powered by [TMDB](https://www.themoviedb.org/). Shows movie posters, ratings, runtime, and more directly on your Discord profile.

Currently supports **movies**, with TV series support planned.

## Requirements

- Python 3.10+
- A [Discord Application](https://discord.com/developers/applications) (for the App ID)
- A [TMDB API key](https://www.themoviedb.org/settings/api)

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Copy `config.example.txt` to `config.txt` and fill in your credentials:
   ```
   cp config.example.txt config.txt
   ```

   ```
   DISCORD_APP_ID=your_discord_app_id
   TMDB_API_KEY=your_tmdb_api_key
   ```

   Alternatively, set `DISCORD_APP_ID` and `TMDB_API_KEY` as environment variables.

## Usage

### Interactive mode

```
python movie_presence.py
```

This opens a prompt where you can search for movies by title, title with year, or TMDB ID:

```
Movie > Casino Royale (2006)
✓ Now showing: Casino Royale (2006)

Movie > id:36557
✓ Now showing: Casino Royale (2006)

Movie > clear
✓ Presence cleared

Movie > quit
```

### CLI mode

Pass a movie directly as an argument:

```
python movie_presence.py "Casino Royale (2006)"
python movie_presence.py id:36557
```

The presence stays active until you press Ctrl+C.

### Windows

Double-click `launch.bat` or run it from the command line with an optional movie argument:

```
launch.bat "Casino Royale (2006)"
```

## License

[MIT](LICENSE)
