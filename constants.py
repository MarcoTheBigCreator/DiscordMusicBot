"""
Constants and configuration for the Discord Music Bot
"""

# Help system categories
HELP_CATEGORIES = {
    "overview": {
        "title": "Music Bot Help",
        "description": "Navigate through different command categories using the buttons below.\n ",
        "icon": "🏠",
    },
    "music": {
        "title": "Music Commands",
        "description": "Core music playback and control commands.\n ",
        "icon": "🎵",
    },
    "queue": {
        "title": "Queue Management",
        "description": "Commands to manage your music queue.\n ",
        "icon": "📋",
    },
    "loop": {
        "title": "Loop & Shuffle",
        "description": "Control playback modes and queue arrangement.\n ",
        "icon": "🔄",
    },
    "info": {
        "title": "Information",
        "description": "Get information about the bot and music.\n ",
        "icon": "📊",
    },
    "admin": {
        "title": "Admin Commands",
        "description": "Administrative and configuration commands.\n ",
        "icon": "⚙️",
    },
}

# Command definitions for help system
COMMAND_CATEGORIES = {
    "music": [
        ("play", "p", "Add song/playlist to queue", "play earthgang up"),
        ("skip", "s", "Skip current song", "skip"),
        ("pause", "pa", "Pause playback", "pause"),
        ("resume", "re", "Resume playback", "resume"),
        ("nowplaying", "np", "Show current song", "nowplaying"),
        ("leave", "", "Disconnect from voice channel", "leave"),
    ],
    "queue": [
        ("queue", "q", "Show queue with pagination", "queue 2"),
        ("clear", "c", "Clear entire queue", "clear"),
        ("shuffle", "sh", "Shuffle pending songs; keep current audio", "shuffle"),
        ("remove", "r", "Remove specific song", "remove 3"),
        ("move", "mv", "Move song position", "move 3 1"),
        ("jump", "j", "Jump to specific song", "jump 5"),
    ],
    "loop": [
        ("loop", "l", "Cycle through loop modes", "loop"),
        ("", "", "• Off ▶️ - Normal playback", ""),
        ("", "", "• Song 🔂 - Repeat current song", ""),
        ("", "", "• Queue 🔁 - Repeat entire queue", ""),
    ],
    "info": [
        ("status", "info", "Show bot status", "status"),
        ("ping", "", "Check bot latency", "ping"),
        ("help", "h", "Show this help message", "help"),
    ],
    "admin": [("prefix", "pre", "Change this server's prefix (Manage Server)", "prefix !")],
}

# Bot configuration
DEFAULT_LOOP_MODE = "off"
QUEUE_SONGS_PER_PAGE = 10
VIEW_TIMEOUT = 300  # 5 minutes

# Loop mode icons
LOOP_ICONS = {"off": "▶️", "song": "🔂", "queue": "🔁"}

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
    "voice_reconnecting": "The voice connection is recovering. Please try again shortly.",
    "nothing_to_pause": "Nothing is playing to pause",
    "nothing_to_resume": "Nothing is paused to resume",
    "playback_held": "Playback paused after an audio access error. Your queue is preserved. Use resume to retry this track or skip to try the next one.",
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
    "help_closed": "Help closed.",
}


# New responses. Existing customization keys above remain unchanged.
MESSAGES.update(
    {
        "different_channel": "Join my voice channel to control the music 🎵",
        "guild_only": "Invite me to a server to play some music 🎵",
        "busy": "🎵 I'm preparing several requests. Please try again shortly.",
        "queue_full": "📋 The queue is full. Remove some songs and try again.",
        "invalid_query": "Please enter a song name or a YouTube link (up to 500 characters).",
        "extraction_failed": "I couldn't prepare that song. Try again or use its YouTube link 🎵",
        "playback_failed": "I couldn't open the audio. I'll try the next song 🎵",
        "audio_forbidden": "YouTube refused the audio (HTTP 403). Try updating yt-dlp; finding the video doesn't guarantee its audio can be opened.",
        "timeout": "That request took too long. Please try again 🎵",
        "bot_verification": "YouTube requested bot verification. Try later; cookies may not resolve it.",
        "cookies_expired": "The configured YouTube cookies have expired. Ask the bot operator to renew them.",
        "age_restricted": "YouTube requires age verification for this video.",
        "authentication_required": "This video requires a YouTube session with access. Ask the bot operator about optional cookies.",
        "region_restricted": "That video isn't available in the bot's region.",
        "unavailable": "I couldn't access that video right now. Try again later.",
        "format_unavailable": "YouTube didn't provide a playable audio format for that video. Try updating yt-dlp.",
        "rate_limited": "YouTube is limiting requests. Wait a while before trying again.",
        "invalid_arguments": "Check the arguments with {prefix}help 🎵",
        "missing_permissions": "You need Manage Server permission to change my prefix.",
        "prefix_changed": "Prefix changed to: `{}`",
        "prefix_invalid": "Use a prefix of 1–10 characters without spaces.",
        "prefix_failed": "Failed to update prefix",
        "pong": "Pong! 🏓",
        "shuffle_pending": "🔀 Pending songs shuffled! The current song keeps playing.",
        "preview": "🎵 Preview",
        "more_songs": "... and {} more",
        "playlist_count": "📋 **{}** songs added to queue",
        "queue_title": "Queue - Page {}/{}",
        "queue_empty_view": "🎵 Queue is empty",
        "queue_count": "{} song(s) total",
        "requested_by": "Requested by: {}\n",
        "queue_current": "🎵 **Now Playing** - {}",
        "queue_item": "{}. {}",
        "queue_footer": "🔄 Loop: {} {}",
        "first_page": "Already on the first page!",
        "last_page": "Already on the last page!",
    }
)

MESSAGES.update(
    {
        "cookies_invalid": "The cookies file is invalid. Ask the bot operator to supply a Netscape cookies file.",
        "request_cancelled": "That request was cancelled. Try play again 🎵",
    }
)

MESSAGES.update(
    {
        "help_how_to": "💡 How to use",
        "help_example": "*Example:* `{}`",
        "button_overview": "🏠",
        "button_music": "🎵",
        "button_queue": "📋",
        "button_loop": "🔄",
        "button_info": "📊",
        "button_admin": "⚙️",
        "button_close": "❌ Close",
        "button_previous": "⬅️ Previous",
        "button_next": "Next ➡️",
        "status_title": "Bot Status",
        "status_connection": "🔗 Connection",
        "status_connected": "Connected to {}",
        "status_disconnected": "Not connected",
        "status_queue": "📋 Queue",
        "status_queue_count": "{} song(s)",
        "status_current": "🎵 Current Song",
        "status_empty": "Empty",
        "status_none": "None",
        "status_loop": "🔄 Loop Mode",
        "status_status": "⏯️ Status",
        "status_playing": "Playing",
        "status_paused": "Paused",
        "status_stopped": "Stopped",
        "status_preparing": "Preparing",
        "unknown_requester": "Unknown",
        "shuffle_title": "🔀 Queue Shuffled",
    }
)
