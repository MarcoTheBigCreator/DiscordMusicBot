"""
Constants and configuration for the Discord Music Bot
"""

# Help system categories
HELP_CATEGORIES = {
    "overview": {
        "title": "Music Bot Help",
        "description": "Navigate through different command categories using the buttons below.\n ",
        "icon": "🏠"
    },
    "music": {
        "title": "Music Commands",
        "description": "Core music playback and control commands.\n ",
        "icon": "🎵"
    },
    "queue": {
        "title": "Queue Management",
        "description": "Commands to manage your music queue.\n ",
        "icon": "📋"
    },
    "loop": {
        "title": "Loop & Shuffle",
        "description": "Control playback modes and queue arrangement.\n ",
        "icon": "🔄"
    },
    "info": {
        "title": "Information",
        "description": "Get information about the bot and music.\n ",
        "icon": "📊"
    },
    "admin": {
        "title": "Admin Commands",
        "description": "Administrative and configuration commands.\n ",
        "icon": "⚙️"
    }
}

# Command definitions for help system
COMMAND_CATEGORIES = {
    "music": [
        ("play", "p", "Add song/playlist to queue", "play earthgang up"),
        ("skip", "s", "Skip current song", "skip"),
        ("pause", "pa", "Pause playback", "pause"),
        ("resume", "re", "Resume playback", "resume"),
        ("nowplaying", "np", "Show current song", "nowplaying"),
        ("leave", "", "Disconnect from voice channel", "leave")
    ],
    "queue": [
        ("queue", "q", "Show queue with pagination", "queue 2"),
        ("clear", "c", "Clear entire queue", "clear"),
        ("shuffle", "sh", "Shuffle entire queue", "shuffle"),
        ("remove", "r", "Remove specific song", "remove 3"),
        ("move", "mv", "Move song position", "move 3 1"),
        ("jump", "j", "Jump to specific song", "jump 5")
    ],
    "loop": [
        ("loop", "l", "Cycle through loop modes", "loop"),
        ("", "", "• Off ▶️ - Normal playback", ""),
        ("", "", "• Song 🔂 - Repeat current song", ""),
        ("", "", "• Queue 🔁 - Repeat entire queue", "")
    ],
    "info": [
        ("status", "info", "Show bot status", "status"),
        ("ping", "", "Check bot latency", "ping"),
        ("help", "h", "Show this help message", "help")
    ],
    "admin": [
        ("prefix", "pre", "Change bot prefix", "prefix !")
    ]
}

# Bot configuration
DEFAULT_LOOP_MODE = "off"
QUEUE_SONGS_PER_PAGE = 10
VIEW_TIMEOUT = 300  # 5 minutes

# Loop mode icons
LOOP_ICONS = {
    "off": "▶️",
    "song": "🔂",
    "queue": "🔁"
}

# Command response messages
MESSAGES = {
    # Error messages
    "not_in_voice": "You're not in a Voice Channel",
    "queue_empty": "The queue is empty",
    "bot_not_connected": "Bot is not connected to a voice channel",
    "invalid_index": "Invalid index",
    "nothing_playing": "Nothing is playing right now",
    "already_first_song": "Already playing the first song",
    "need_more_songs": "Need at least 2 songs to {}",  # Format with action
    "no_query": "Please provide a song to search for",
    "song_not_found": "I could not find that song",
    "connection_failed": "Failed to connect to voice channel",
    "nothing_to_pause": "Nothing is playing to pause",
    "nothing_to_resume": "Nothing is paused to resume",
    "queue_already_empty": "The queue is already empty",
    "same_position": "Source and destination are the same",
    "song_removed_format": "Removed {}",
    "next_up": "Next up",
    "duration_label": "Duration: {}",

    # Success messages
    "paused": "Paused",
    "resumed": "Resumed",
    "disconnected": "Disconnected",
    "song_skipped": "Song skipped",
    "song_removed": "Song removed",
    "queue_cleared": "Cleared {} song(s) from the queue",
    "queue_shuffled": "Shuffled {} song(s) in the queue",
    "song_moved": "Moved '{}' from position {} to {}",
    "jumped_to": "Jumped to: {}",

    # Playlist messages
    "playlist_loading": "🎵 Loading playlist...",
    "playlist_added": "📋 Added {} songs from playlist",
    "playlist_queued": "📋 Queued {} songs from playlist",
    "playlist_title": "Playlist: {}",
    "playlist_partial": "⚠️ Loaded {} of {} songs (some may be unavailable)",
    "playlist_limit": "📋 Playlist limited to {} songs (max allowed)",

    # Status messages
    "queued": "Queued",
    "now_playing": "Now Playing",
    "moving_channel": "Moving to your voice channel",
    "song_field": "Song",
    "by_field": "By",

    # Loop messages
    "loop_song": "🔂 Loop mode: **Song** - Current song will repeat",
    "loop_queue": "🔁 Loop mode: **Queue** - Queue will repeat",
    "loop_off": "▶️ Loop mode: **Off** - Normal playback",

    # Help messages
    "help_footer": "Bot made with ❤️ • Use buttons to navigate • Timeout: 5 minutes",
    "help_usage": "• Click the buttons below to navigate between categories\n• Use the prefix `-` before each command\n• Commands are case-insensitive",
    "help_closed": "Help closed."
}

# YouTube-DL options
YDL_OPTIONS = {
    'format': 'm4a/bestaudio/best',
    'noplaylist': False,
    'extract_flat': False,
    'ignoreerrors': True
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}
