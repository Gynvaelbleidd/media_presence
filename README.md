# Media Rich Presence

A Discord Rich Presence tool that displays what you're currently watching, powered by [TMDB](https://www.themoviedb.org/). Shows posters, ratings, and more directly on your Discord profile.

Supports **movies** and **TV series**.

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

On launch, select a media type:

```
Select media type:
  movie
  tv
> movie
```

#### Movie mode

Search for movies by title, title with year, or TMDB ID:

```
Movie > Casino Royale (2006)
✓ Now showing: Casino Royale (2006)

Movie > id:36557
✓ Now showing: Casino Royale (2006)

Movie > clear
✓ Presence cleared

Movie > quit
```

#### TV mode

Search for TV shows by title, with optional year and season:

```
TV > Breaking Bad
✓ Now showing: Breaking Bad (2008)

TV > Breaking Bad (2008)
✓ Now showing: Breaking Bad (2008)

TV > Breaking Bad (S3)
✓ Now showing: Breaking Bad (2008)
  Season: 3

TV > Breaking Bad (2008) (S3)
✓ Now showing: Breaking Bad (2008)
  Season: 3

TV > id:1396
✓ Now showing: Breaking Bad (2008)

TV > clear
✓ Presence cleared

TV > quit
```

### CLI mode

Pass a movie or TV show directly as an argument, prefixed with `movie:` or `tv:`:

```
python movie_presence.py movie: Casino Royale (2006)
python movie_presence.py tv: Breaking Bad (S3)
python movie_presence.py tv: id:1396
```

Without a prefix, the argument is treated as a movie:

```
python movie_presence.py "Casino Royale (2006)"
```

The presence stays active until you press Ctrl+C.

### Windows

Double-click `launch.bat` for interactive mode, or run from the command line:

```
launch.bat movie: Casino Royale (2006)
launch.bat tv: Breaking Bad (S3)
```

## License

[MIT](LICENSE)
