# Discord Music Bot CRUMMY v4.0 (Refactored)

<div align="center">
  <img src="https://user-images.githubusercontent.com/86860760/220523513-b32c0c1d-c003-408a-9569-a0c1d7d81ec5.jpg">
  <h1 align="center"> Discord Music Bot "Crummy" [Version 4.0 - Refactored]</h1>
  <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/MarcoTheBigCreator/DiscordMusicBot?color=blueviolet&style=for-the-badge">
  <a href="https://github.com/MarcoTheBigCreator/DiscordMusicBot/graphs/contributors">
    <img alt="GitHub contributors" src="https://img.shields.io/github/contributors/MarcoTheBigCreator/DiscordMusicBot?color=gree&style=for-the-badge">
  </a>
   <a href="https://github.com/MarcoTheBigCreator/DiscordMusicBot/network/members">
    <img alt="GitHub forks" src="https://img.shields.io/github/forks/MarcoTheBigCreator/DiscordMusicBot?style=for-the-badge">
  </a>
  <a href="https://github.com/MarcoTheBigCreator/DiscordMusicBot/stargazers">
    <img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/MarcoTheBigCreator/DiscordMusicBot?color=yellow&style=for-the-badge">
  </a>
  <p align="center">
   An easy to use Discord Bot for playing music in Discord servers. Using <a href="https://www.python.org/">Python</a>, <a href="https://github.com/yt-dlp/yt-dlp">yt-dlp</a> and <a href="https://ffmpeg.org/">FFmpeg</a>.
  </p>
  <a href="https://github.com/MarcoTheBigCreator/DiscordMusicBot/stargazers"><strong>Give to Crummy a Star!</strong></a>
  <hr>
  <h3>Local installation guide below • Historical Heroku guide retained for reference</h3>
  <hr>
</div>

<div>
  <h2 align="center"> How does it look? </h2>
  <p align="center">
  <img src="https://github.com/MarcoTheBigCreator/DiscordMusicBot/assets/86860760/b4647dcc-3503-4d82-9d52-55590956a92b" style="width: 40%;">
  <img src="https://github.com/MarcoTheBigCreator/DiscordMusicBot/assets/86860760/ab4cb35d-3f90-45eb-adbc-51ce50650e91" style="width: 48%;">
  <img src="https://github.com/MarcoTheBigCreator/DiscordMusicBot/assets/86860760/f22bea8b-0b9b-449c-8360-2a82b77351c5" style="width: 70%;">
  <img src="https://github.com/MarcoTheBigCreator/DiscordMusicBot/assets/86860760/56480cb9-f4da-4d7d-923b-53748b665b36" style="width: 70%;">
  <br>
</div>

<!-- Step 1: Discord App -->
<div>
  <br>
  <h2 align="center"> How to create yours? </h2>
  <div align="left">
    <h3>Step 1: Create an Application on Discord Developer Portal</h3>
    <ol>
      <li>
        <strong>Access</strong> to<a href="https://discord.com/developers/applications"> Discord Developer Portal</a> and make a new application.
        <img src="https://user-images.githubusercontent.com/86860760/221338732-33510cba-77c4-4e9a-9ba2-1302fd6e95be.png">
      </li> 
      <br>
      <li>
        <strong>Customize</strong> the "General Information" as you wish. Then, <strong>go</strong> to "Bot" settings.
        <img src="https://user-images.githubusercontent.com/86860760/221339439-ed0f890c-02e4-46c4-8551-25375cac624b.png">
      </li>
      <br>
       <li>
        <strong>Click</strong> on "Add Bot" button and <strong>accept</strong>.
        <img src="https://user-images.githubusercontent.com/86860760/221340657-04c46a2e-c5b8-4eb9-8b83-bc25be6ca796.png">
      </li>
      <br>
      <li>
         <strong>Customize</strong> the bot icon and username and then:
         <ol>
          <li><strong>Click</strong> on "View Token" button.</li>
          <li><strong>Copy</strong> the token.</li>
          <li><strong>Save it</strong> in your local <code>.env</code> file only (never in shared notes, screenshots or Git; reset it in the portal if exposed).</li>
        </ol>
        <img src="https://user-images.githubusercontent.com/86860760/221341089-cc655ce9-fa36-4e64-85f9-5ba35765659f.png">
      </li>
      <br>
      <li>
        <strong>Scroll down</strong> and enable <strong>Message Content Intent</strong>. Server Members Intent and Presence Intent are not needed. The older screenshot below is a visual reference; do not enable every privileged intent.
        <img src="https://user-images.githubusercontent.com/86860760/221394463-ce9b9b09-1cb2-4af7-be3d-66ce08d04985.png">
      </li>
      <br>
      <li>
        <strong>Select</strong> View Channels, Send Messages, Embed Links, Read Message History, Connect and Speak. Administrator is not required. Give these permissions in the text and voice channels you will use; the historical screenshot below shows the location, not the permissions to copy.
        <img src="https://user-images.githubusercontent.com/86860760/221341382-dae43315-6e62-4db8-948f-71b0751b67bf.png">
      </li>
      <br>
      <li>
        <strong>Click</strong> on "OAuth2" settings and <strong>go to</strong> "URL Generator" option.
        <ol>
          <li>
            <strong>Select</strong> "bot" in "Scopes" and choose the six permissions listed above in "Bot Permissions". Administrator is unnecessary.
          </li>
        </ol>
        <img src="https://user-images.githubusercontent.com/86860760/221342221-0389a535-b722-4727-9fbc-6bb0a5ae30da.png">
        <img src="https://user-images.githubusercontent.com/86860760/221342388-3dfab5f0-8a8f-4cc5-aa66-7ae07660b46b.png">
      </li>
      <br>
      <li>
        <strong>Copy</strong> and <strong>Paste</strong> the link in a new tab to invite your bot to the server of your choice.
      </li>
    </ol>
  </div>

  <!-- Local use -->
  <div align="center">
    <hr>
    <h2>Steps for local use</h2>
  </div>
    <div align="left">
    <h3>Step 2: Install FFmpeg</h3>
    <p>On Windows, run <code>winget install --id Gyan.FFmpeg -e</code>, then close and reopen PowerShell. Check with <code>ffmpeg -version</code>. On Ubuntu/Debian use <code>sudo apt install ffmpeg</code>; on macOS use <code>brew install ffmpeg</code>.</p>
    <strong>Follow the steps of</strong><a href="https://youtu.be/5xgegeBL0kw"> How to install FFmpeg</a> to proceed to the final step (the video is not mine so I would ask you to leave your support for the creator with a like or a comment).
  </div>
  <div align="left">
    <h3>Step 3: Download and configure the Program</h3>
    <strong>Use Python 3.12.16 for v4 (uv installs it for this project); Git is optional. For introductory background see</strong><a href="https://youtu.be/nU2Egc3Zx3Q?si=0JEnBFNEuXjVf-j1"> How to Install Python</a> and <a href="https://git-scm.com/downloads"> Git Download Page</a> to proceed with the process (the video is not mine so I would ask you to leave your support for the creator with a like or a comment).
    <ol>
      <li><strong>Clone</strong> the repo.</li>
      <pre><code>git clone https://github.com/MarcoTheBigCreator/DiscordMusicBot.git</code></pre>
      <p>If Git is not installed. <strong>Download</strong> manually the repo.</p>
      <img src="https://github.com/MarcoTheBigCreator/DiscordMusicBot/assets/86860760/4f4b1a12-002f-4738-9511-66258acaa11a">
      <br>
      <br>
      <li><strong>Install</strong> the dependencies (make sure you're on the repo's folder to execute the command).</li>
      <p>Install uv on Windows: <code>winget install --id astral-sh.uv -e</code>. Reopen PowerShell, then open the downloaded project folder. On Linux/macOS install uv using the <a href="https://docs.astral.sh/uv/getting-started/installation/">official instructions</a>.</p>
      <pre><code>uv python install 3.12.16
uv sync --locked</code></pre>
      <p>uv creates an isolated <code>.venv</code>. You do not need to replace your computer's global Python. Check the project's interpreter with <code>uv run --locked python --version</code>.</p>
      <br>
      <li><strong>Open</strong> the repo in a code editor and <strong>copy</strong> the <strong>.env.template</strong> file.</li>
      <br>
      <li><strong>Paste</strong> it <strong>changing</strong> the name to just <strong>.env</strong></li>
      <br>
      <li><strong>Put</strong> your Bot's Token (the one you previously copied and saved) on the <strong>.env</strong> file.</li>
      <img src="https://github.com/MarcoTheBigCreator/DiscordMusicBot/assets/86860760/c6e4def1-d205-4435-9eb4-c62bf1659478">
      <br>
      <br>
      <li><strong>Run</strong> the program.</li>
      <pre><code>uv run bot</code></pre>
      <br>
      <li><strong>Optional:</strong> create a shortcut that runs <code>uv run bot</code> with this repository as its working directory. Double-clicking main.py may use your old global Python instead.</li>
    </ol>
  </div>
  <br>

  <!-- Heroku Deploying -->
  <p><strong>Historical deployment walkthrough:</strong> the screenshots and video below are preserved, but they are not a verified v4 deployment recipe. Use <code>.python-version</code> instead of the deprecated <code>runtime.txt</code> (<a href="https://devcenter.heroku.com/articles/python-runtimes">Heroku documentation</a>). <code>Procfile</code> still defines one worker. Dependencies are managed by <code>pyproject.toml</code> and <code>uv.lock</code>; a requirements.txt export is no longer stored. Heroku supports uv natively (<a href="https://devcenter.heroku.com/changelog-items/3238">official announcement</a>). Before deploying, provision FFmpeg and any JavaScript components explicitly, configure secrets as environment variables, and use persistent storage for CRUMMY_DATA_DIR and optional cookies. Dyno filesystems are ephemeral. The old buildpack/video may not provide current requirements. No Heroku deployment has been tested for v4.</p>
  <div align="center">
    <hr>
    <h2>Steps for Heroku deploying</h2>
  </div>
  <div align="left">
    <h3>Step 2: Download and configure the deployment to Heroku</h3>
    <strong>It is expected having Python and optionally Git installed already, If not click on</strong><a href="https://youtu.be/nU2Egc3Zx3Q?si=0JEnBFNEuXjVf-j1"> How to Install Python</a> and <a href="https://git-scm.com/downloads"> Git Download Page</a> to proceed with the process (the video is not mine so I would ask you to leave your support for the creator with a like or a comment).
    <ol>
      <li><strong>Clone</strong> the repo.</li>
      <pre><code>git clone https://github.com/MarcoTheBigCreator/DiscordMusicBot.git</code></pre>
      <p>*If Git is not installed. <strong>Download</strong> manually the repo.</p>
      <img src="https://github.com/MarcoTheBigCreator/DiscordMusicBot/assets/86860760/4f4b1a12-002f-4738-9511-66258acaa11a">
      <br>

      <br>
      <li><strong>Follow</strong> the steps of the <a href="https://youtu.be/nU2Egc3Zx3Q?si=0JEnBFNEuXjVf-j1">Heroku deployment video</a>. (It's an excellent video for inexperience people, in case of previous experience deploying apps, can do it your own) <strong>Don't forget the support for the video's creator</strong>.</li>
      <p>*The token he mentions on the video is the one you saved previously.</p>
      <p>*The files are already made (you can skip to minute 5:59).</p>
      <br>
      <li>In addition to the video steps it's necessary to <strong>install</strong> this build pack (you can do it from the page direclty as image indicates).</li>
      <pre><code>https://github.com/heroku/heroku-buildpack-activestorage-preview.git</code></pre>
      <img src="https://github.com/MarcoTheBigCreator/DiscordMusicBot/assets/86860760/c1a59078-d001-4654-bf01-d0d1e5064127">
      <br>
      <br>
    <p>*After this a new deployment will be necessary to add that build pack.</p>
    <li><strong>Historical screenshot:</strong> this used runtime.txt. v4 selects Python using .python-version; do not change the interpreter just to trigger a deployment.</li>
      <img src="https://github.com/MarcoTheBigCreator/DiscordMusicBot/assets/86860760/cd121a58-9213-47c5-8074-9d01d3831180">
      <br>
      <br>
    <li><strong>Historical command:</strong> the project owner decides when reviewed changes are committed.</li>
    <pre><code># Commit only after owner review and explicit authorization</code></pre>
    <li><strong>Push</strong> the changes in order to start a new deployment.</li>
    <pre><code>git push heroku main</code></pre>
    <li><strong>Activate</strong> your Heroku app. </li>
    <img src="https://github.com/MarcoTheBigCreator/DiscordMusicBot/assets/86860760/d82501df-45ca-4b6b-9212-9f95d143cb7a">
    </ol>
  </div>
  <br>
  <hr>

  <!-- Commands Documentation -->
  <div align="center">
    <h2>Commands</h2>
  </div>
  <div align="left">
    <p>Below is a list of commands available for Crummy v4.0 (Refactored), along with their aliases and functions. Use these commands to control the music playback in your server.</p>
    <h3>🎵 Core Music Commands</h3>
    <table>
      <thead>
        <tr>
          <th>Commands</th>
          <th>Aliases</th>
          <th>Function</th>
          <th>How to use it</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>play</td>
          <td>(p, PLAY, Play, P)</td>
          <td>Add song to queue (supports URLs and search)</td>
          <td>-play never gonna give you up</td>
        </tr>
        <tr>
          <td>skip</td>
          <td>(s, SKIP, Skip, S)</td>
          <td>Skip current song</td>
          <td>-skip</td>
        </tr>
        <tr>
          <td>pause</td>
          <td>(pa, Pause, PAUSE)</td>
          <td>Pause playback</td>
          <td>-pause</td>
        </tr>
        <tr>
          <td>resume</td>
          <td>(unpause, re, un, Resume, Unpause, RESUME, UNPAUSE, RE)</td>
          <td>Resume playback</td>
          <td>-resume</td>
        </tr>
        <tr>
          <td>nowplaying</td>
          <td>(np, Nowplaying, NP, NOWPLAYING)</td>
          <td>Show current song</td>
          <td>-nowplaying</td>
        </tr>
        <tr>
          <td>leave</td>
          <td>(LEAVE, Leave)</td>
          <td>Disconnect from voice channel</td>
          <td>-leave</td>
        </tr>
      </tbody>
    </table>
    <h3>📋 Queue Management Commands</h3>
    <table>
      <thead>
        <tr>
          <th>Commands</th>
          <th>Aliases</th>
          <th>Function</th>
          <th>How to use it</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>queue</td>
          <td>(q, QUEUE, Queue, Q)</td>
          <td>Show current queue with pagination</td>
          <td>-queue 2</td>
        </tr>
        <tr>
          <td>clear</td>
          <td>(c, Clear, CLEAR, C)</td>
          <td>Clear entire queue</td>
          <td>-clear</td>
        </tr>
        <tr>
          <td>shuffle</td>
          <td>(sh, Shuffle, SHUFFLE, SH)</td>
          <td>Shuffle pending songs, keeping current audio</td>
          <td>-shuffle</td>
        </tr>
        <tr>
          <td>remove</td>
          <td>(r, Remove, REMOVE, R)</td>
          <td>Remove specific song from queue</td>
          <td>-remove 3</td>
        </tr>
        <tr>
          <td>move</td>
          <td>(mv, Move, MOVE, MV)</td>
          <td>Move song position in queue</td>
          <td>-move 3 1</td>
        </tr>
        <tr>
          <td>jump</td>
          <td>(j, Jump, JUMP, J)</td>
          <td>Jump to specific song in queue</td>
          <td>-jump 5</td>
        </tr>
      </tbody>
    </table>
    <h3>🔄 Loop System Commands</h3>
    <table>
      <thead>
        <tr>
          <th>Commands</th>
          <th>Aliases</th>
          <th>Function</th>
          <th>How to use it</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>loop</td>
          <td>(l, LOOP, Loop)</td>
          <td>Cycle through loop modes (Off ▶️ / Song 🔂 / Queue 🔁)</td>
          <td>-loop</td>
        </tr>
      </tbody>
    </table>
    <h3>📊 Information Commands</h3>
    <table>
      <thead>
        <tr>
          <th>Commands</th>
          <th>Aliases</th>
          <th>Function</th>
          <th>How to use it</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>help</td>
          <td>(h, Help, HELP, H)</td>
          <td>Interactive help with categorized commands</td>
          <td>-help</td>
        </tr>
        <tr>
          <td>status</td>
          <td>(info, Status, STATUS, INFO)</td>
          <td>Show bot status</td>
          <td>-status</td>
        </tr>
        <tr>
          <td>ping</td>
          <td>(PING)</td>
          <td>Check bot latency</td>
          <td>-ping</td>
        </tr>
      </tbody>
    </table>
    <h3>⚙️ Admin Commands</h3>
    <table>
      <thead>
        <tr>
          <th>Commands</th>
          <th>Aliases</th>
          <th>Function</th>
          <th>How to use it</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>prefix</td>
          <td>(pre, PRE, Pre, PREFIX, Prefix)</td>
          <td>Change this server's prefix (Manage Server permission)</td>
          <td>-prefix !</td>
        </tr>
      </tbody>
    </table>

<br>
<h3>Command Structure</h3>
    <p>A command in a Discord bot is a function that executes a specific task when triggered by a user command. Here's what each part of a command does:</p>
    <ul>
        <li><strong>Decorator:</strong> This is where you define the command, its name, aliases, and a brief description of its functionality.</li>
        <li><strong>Function:</strong> The main logic of the command, typically an asynchronous function (<code>async def</code>) that performs the desired task.</li>
        <li><strong>Context (ctx):</strong> An object that contains information about the command invocation, such as the message, the author, the channel, etc.</li>
        <li><strong>Embed:</strong> An embedded message is a rich content message that can include a title, description, color, fields, and other visual elements.</li>
        <li><strong>Message Sending:</strong> The part where the bot sends the message, optionally deleting it after a specified time.</li>
    </ul>
    <h3>Ping Command Example</h3>
    <p>In v4, the existing ping command lives inside <code>create_bot</code> in <code>main.py</code>. To adapt this educational example, edit that existing function there; do not add a second ping command at module level. Uppercase aliases are handled automatically by <code>case_insensitive=True</code>.</p>
    <pre><code>@bot.command(name='ping', aliases=['PING'], help='Verifies the bot\'s latency')
async def ping(ctx):
    # Create an embed with the bot's latency
    embed = discord.Embed(
        title="Pong!   🏓",
        description=f'{round(bot.latency * 1000)} ms',
        color=discord.Color.red()
    )
    # Send the embed to the channel and delete it after 30 seconds
    await ctx.send(embed=embed, delete_after=30)
    </code></pre>
    <h3>Explanation</h3>
    <ul>
        <li><strong>Decorator:</strong>
            <pre><code>@bot.command(name='ping', aliases=['PING'], help='Verifies the bot\'s latency')</code></pre>
            <ul>
                <li><code>name='ping'</code>: The name of the command.</li>
                <li><code>aliases=['PING']</code>: Alternate names for the command.</li>
                <li><code>help='Verifies the bot\'s latency'</code>: A brief description of what the command does, shown in the help menu.</li>
            </ul>
        </li>
        <li><strong>Function:</strong>
            <pre><code>async def ping(ctx):</code></pre>
            <ul>
                <li><code>async def</code>: Defines an asynchronous function.</li>
                <li><code>ping(ctx)</code>: The function name and context parameter.</li>
            </ul>
        </li>
        <li><strong>Embed:</strong>
            <pre><code>embed = discord.Embed(
    title="Pong!   🏓",
    description=f'{round(bot.latency * 1000)} ms',
    color=discord.Color.red()
)</code></pre>
            <ul>
                <li><code>discord.Embed()</code>: Creates a new embed object.</li>
                <li><code>title</code>: The title of the embed.</li>
                <li><code>description</code>: The main content of the embed, here showing the bot's latency in milliseconds.</li>
                <li><code>color</code>: The color of the embed's sidebar, here set to red.</li>
            </ul>
        </li>
        <li><strong>Message Sending:</strong>
            <pre><code>await ctx.send(embed=embed, delete_after=30)</code></pre>
            <ul>
                <li><code>ctx.send(embed=embed)</code>: Sends the embed to the channel.</li>
                <li><code>delete_after=30</code>: Deletes the message after 30 seconds. This is optional and can be omitted if you don't want the message to be automatically deleted.</li>
            </ul>
        </li>
    </ul>
    <h3>Customization</h3>
    <ul>
        <li><strong>Embed Content:</strong> You can add more fields to the embed using <code>embed.add_field(name='Field Name', value='Field Value', inline=False)</code>.</li>
        <li><strong>Embed Color:</strong> Change the color to match your bot's theme using <code>discord.Color.&lt;color_name&gt;()</code> or a hex code.</li>
        <li><strong>Delete Time:</strong> Adjust or remove the <code>delete_after</code> parameter based on your needs.</li>
    </ul>
    <h3>🎨 Message Customization System (New in v3.0)</h3>
    <p>The refactored version introduces a centralized message system through the <code>constants.py</code> file. This makes it easy to customize all bot messages, help text, and configuration without touching the main code.</p>
    <h4>Constants File Structure</h4>
    <p>All static data is organized in <code>constants.py</code>:</p>
    <pre><code># Command response messages
MESSAGES = { 
# Error messages
"not_in_voice": "You're not in a Voice Channel",
"queue_empty": "The queue is empty",
"song_not_found": "I could not find that song",

    # Success messages
    "paused": "Paused",
    "resumed": "Resumed",
    "song_skipped": "Song skipped",

    # Status messages
    "queued": "Queued",
    "now_playing": "Now Playing",

    # Loop messages
    "loop_song": "🔂 Loop mode: **Song** - Current song will repeat",
    "loop_queue": "🔁 Loop mode: **Queue** - Queue will repeat",
    "loop_off": "▶️ Loop mode: **Off** - Normal playback"

}</code></pre>

<h4>Easy Customization</h4>
<p>To customize bot messages, simply edit the values in <code>constants.py</code>:</p>
<ul>
<li><strong>Language Translation:</strong> Change all messages to your preferred language</li>
<li><strong>Custom Branding:</strong> Add your server's personality to the messages</li>
<li><strong>Emoji Customization:</strong> Change or add emojis to make messages more fun</li>
<li><strong>Error Messages:</strong> Make error messages more helpful or friendly</li>
</ul>
<h4>Configuration Options</h4>
<p>Presentation settings remain in <code>constants.py</code>. Extraction/audio settings and validated runtime defaults now live in <code>config.py</code>:</p>
<ul>
<li><strong>QUEUE_SONGS_PER_PAGE:</strong> Number of songs displayed per page in queue (default: 10)</li>
<li><strong>VIEW_TIMEOUT:</strong> How long interactive buttons stay active (default: 300 seconds)</li>
<li><strong>DEFAULT_LOOP_MODE:</strong> Starting loop mode when bot starts (default: "off")</li>
<li><strong>LOOP_ICONS:</strong> Emojis used for different loop modes</li>
</ul>
<h4>Advanced Customization</h4>
<p>For developers who want to add new features:</p>
<ul>
<li><strong>Add New Messages:</strong> Simply add new keys to the MESSAGES dictionary</li>
<li><strong>Create New Categories:</strong> Add new command categories to the help system</li>
<li><strong>Modify Embed Styles:</strong> Change colors and formatting by editing the embed creation methods in <code>player.py</code> and <code>views.py</code></li>
</ul>
<p><strong>💡 Pro Tip:</strong> After making changes to <code>constants.py</code>, restart the bot to see your customizations take effect!</p>

  </div>
  <hr>
  <div align="center">
    <h2>Report Issues</h2>
    <p>We apologize for any errors you may be experiencing.</p>
    <p>Please keep in mind that this was made just for fun, other functionalities could be added with collaboration work. However, if you encounter a problem while using the bot, please <a href="https://github.com/MarcoTheBigCreator/DiscordMusicBot/issues">open an issue</a> and we will work to resolve it as soon as possible</p>
<p>When reporting an issue, please make sure to include your command, package versions and sanitized error code; never attach .env, cookies, tokens or temporary audio URLs. Thank you for your patience.</p>
  </div>
</div>


## v4 notes: installation, playback and maintenance

The illustrated tutorial, original help buttons, emoji messages and customization examples above remain the starting point. v4 separates configuration (`config.py`), typed songs (`models.py`), extraction (`media.py` / `media_worker.py`), playback (`player.py`), commands (`music_commands.py`) and views (`views.py`). `uv run bot` is the short launch command; `uv run --locked bot` enforces the current lock. `uv run --locked python main.py` remains supported. `uv run bot --help` never loads credentials or connects to Discord.

### What stays the same for music

Both `-p go blackpink` and `-p https://www.youtube.com/watch?v=2GJfWMYCWY0` work through a full yt-dlp extraction. The first returned audio URL goes straight to `FFmpegPCMAudio`; there is no second lookup before playing a fresh song. The original `m4a/bestaudio/best` selector and FFmpeg reconnect/`-vn` flags are preserved. Queued URLs older than two minutes and repeated songs are resolved again using that video's original URL, never a replacement search result.

FFmpeg must produce a PCM frame before the bot says **Now Playing**. This catches empty streams and initial HTTP 403 failures. It proves decoding started; it does not prove listeners can hear the bot in Discord.

**Compatibility record (2026-11-03):** the original global environment used Python 3.12.2, yt-dlp 2026.10.21 and discord.py 2.7.1. Anonymous extraction followed by a two-second PCM read succeeded. Updated environments that added yt-dlp's default extras, or used Python 3.14 in the tested combinations, returned HTTP 403. Python **3.12.16** with yt-dlp **2026.10.26** and the original transport libraries successfully decoded the same song. v4 uses this checked combination, with current security fixes. These comparisons do not establish a universal cause for YouTube's 403 responses.

There is one dependency set for the bot: yt-dlp with its official default dependencies, including the matching EJS solver (0.8.0 for the current lock), mutagen and pycryptodomex. `uv sync --locked` installs everything; `uv run bot` starts the bot and `uv run test` runs its tests. Deno is an external requirement. Cookies remain optional and are configured only through YTDLP_COOKIES_FILE. Startup reports missing Deno/EJS before connecting to Discord. Read the [official EJS guide](https://github.com/yt-dlp/yt-dlp/wiki/EJS). We do not automatically download remote solver code or update packages at startup. No combination guarantees every YouTube video will remain available.

### Optional YouTube cookies, step by step

Leave `YTDLP_COOKIES_FILE=` empty first. Cookies are optional, operator-controlled session secrets; no Discord command uploads them or changes their path. They cannot reliably solve bot verification, rate limits or every HTTP 403.

If a video actually requires your account's access:

1. Read the [official cookie export instructions](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies) and [Netscape format FAQ](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp). Account use can lead to restrictions or suspension; use an account you are willing to risk.
2. Use an exporter listed by the FAQ, such as **Get cookies.txt LOCALLY** for Chrome or **cookies.txt** for Firefox. Check the publisher carefully, allow it only the required sites, and enable it in private/incognito mode. Do not install an unrelated extension with a similar name.
3. Open one private/incognito window, sign in at YouTube and check that the video plays there. In that same tab, open `https://www.youtube.com/robots.txt`. Export the `youtube.com` cookies in **Netscape** format using the extension. Close the private window immediately afterward and do not reopen that browser session; this reduces cookie rotation. The FAQ's normal `--cookies-from-browser` export does not export this private session.
4. Save the file **outside this repository and OneDrive**, for example `C:/Users/YOUR_NAME/AppData/Local/Crummy/youtube.cookies.txt`. Its first line must be `# Netscape HTTP Cookie File` or `# HTTP Cookie File`. Do not paste its contents into chat or a bug report. Restrict file access to your operator account (on Linux/macOS: `chmod 600 /absolute/path/youtube.cookies.txt`).
5. Set the absolute path in your local `.env`, using forward slashes on Windows:

   ```dotenv
   YTDLP_COOKIES_FILE=C:/Users/YOUR_NAME/AppData/Local/Crummy/youtube.cookies.txt
   ```

6. Stop the old instance, run `uv sync --locked`, then `uv run bot`. If cookies expire, repeat the export and replace the file. To use anonymous access, clear YTDLP_COOKIES_FILE and restart. The installation and launch commands remain the same. If the file leaks, sign out/revoke that Google session and delete exposed copies. `.gitignore` helps with common filenames, but is not a substitute for storing secrets outside the repository.

### Queue, controls and separate servers

One bot process serves several Discord servers, each with its own connection, current song, pending songs, preparation requests, loop mode and prefix. You do not need a separate bot account per server.

- Queue numbering starts at **1 for the current/preparing song**, then pending songs. Paused songs keep their position.
- `skip` and `remove 1` stop the current song even when paused or in loop-song mode. In loop queue, `skip` moves the skipped entry to the end; with only one entry it restarts that song. With loop off or loop song, skip discards the current entry. `remove` always deletes the selected entry permanently, regardless of loop mode. A failed song is dropped rather than retried forever.
- `shuffle` mixes **pending songs only** and preserves current audio. It needs two pending songs.
- `jump N` rotates earlier songs to the end, starts N, and keeps each entry once. `move A B` reorders entries; if position 1 changes, audio switches to the new first song. A switch starts playing even if the previous song was paused.
- `clear` stops audio and cancels earlier preparation requests, retaining the connection and loop mode. `leave` also disconnects and resets repetition. An unexpected disconnect clears the session; a new `play` can connect again.
- Share the bot's voice channel to control it. `play` from another channel is refused instead of moving an active session. `help` works in a server without joining voice; music commands do not run in direct messages.
- `prefix` / `pre` requires **Manage Server**. Prefixes persist per server in `data/prefixes.json` using atomic writes; `.env` is never rewritten. Run one bot process per data directory.

### Limits and settings

Concurrency limits can be set in your local `.env` using the optional variables in `.env.template`; restart the bot after changing them. If omitted, `Settings` in `config.py` supplies conservative defaults: **3 extraction processes globally, 1 active request per server, 3 accepted requests per server and 12 globally**, including the active request. Requests are FIFO within each server; different servers can prepare concurrently. Controls do not wait for extraction locks. A playlist streams prepared entries progressively, up to **50 entries**, into a queue capped at **200**. A partial failure retains entries already prepared. The two-minute stream age is a refresh threshold, not a metadata cache. Connection timeout is 30 seconds, extraction timeout 60 seconds once it reaches the extraction service (including global capacity wait), and the first PCM read has a 20-second timeout. Earlier per-server requests may add waiting time. By default at most two initial PCM reads run simultaneously; this does not limit the number of servers already playing music. Clearing a request waits for the real extraction process to be terminated before releasing capacity.

| Variable | Default | Meaning |
| --- | --- | --- |
| `WORKERS` | `3` | Maximum active extraction processes across servers; still one per server, FIFO |
| `AUDIO_WORKERS` | `2` | Concurrent FFmpeg startup/first-frame checks, not ongoing playback sessions |
| `REQUESTS` | `12` | Accepted preparation requests globally, including active ones |
| `GUILD_REQUESTS` | `3` | Accepted preparation requests per server, including the active one |
| `PLAYLIST_LIMIT` | `50` | Maximum playlist entries per request |
| `QUEUE_LIMIT` | `200` | Maximum songs in each server's playback queue |
| `EXTRACT_TIMEOUT` | `60` | Extraction timeout in seconds, including worker-capacity wait |
| `CONNECT_TIMEOUT` | `30` | Voice connection timeout in seconds |
| `STREAM_MAX_AGE` | `120` | Age in seconds after which a temporary stream is resolved again |

The original seven operator variables are preserved with their previous defaults. `AUDIO_WORKERS=2` and `STREAM_MAX_AGE=120` are optional advanced settings. The recently introduced `CRUMMY_*` names remain lower-priority aliases; the names in the table take precedence if both are set.

Counts must be positive integers; extraction and connection timeouts must be finite and positive; stream age must be finite and nonnegative. Raising the global worker count permits more servers to prepare concurrently; it does not parallelize requests within one server. Controls continue responding during preparation. No changes to the operator's existing `.env` are made by this refactor.

Environment options are listed in `.env.template`: token, default prefix, optional cookie file, FFmpeg executable and data directory. There is no automatic login through Deno. Install/update Deno separately if needed (`winget install --id DenoLand.Deno -e` on Windows; reopen your terminal and check `deno --version`).

### Customize your bot's personality

Keep editing `MESSAGES`, `HELP_CATEGORIES` and `COMMAND_CATEGORIES` in `constants.py`. Existing keys, emojis and positional placeholders are retained: `"song_removed_format": "Removed {}"`, for example. Keep the same number/order of `{}` placeholders. `invalid_arguments` uses the named `{prefix}` placeholder. Help examples use the actual server prefix. Presentation styles live in `views.py` and `player.py`; technical extraction settings live in `config.py`.

### Checks and controlled updates

To run the whole offline suite, use `uv run test` (or `uv run test -q` for a shorter report). Extra pytest arguments work, for example `uv run test -k loop`. The command runs tests only; lint, format and the network-based dependency audit remain separate checks.

From the project directory:

```sh
uv sync --locked
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked test -q
uv run --locked pip-audit --skip-editable --progress-spinner off
uv run --locked python scripts/diagnose_audio.py "go blackpink"
```

Unit/internal integration tests use doubles and local audio, without Internet, tokens or cookies. The diagnostic is a separate network check: it uses the production extractor and FFmpeg path, defaults to anonymous access, prints sanitized results, and never connects to Discord or loads `.env`. To diagnose account access deliberately, pass `--cookies-file /absolute/path/youtube.cookies.txt`; its contents and path are not printed. An extraction success with `audio_read_ok: false` is still a playback failure.

To update yt-dlp to the newest stable release and review it before running the bot:

```sh
uv lock --upgrade-package yt-dlp
uv sync --locked
uv run --locked test -q
uv run --locked pip-audit --skip-editable --progress-spinner off
uv run --locked python scripts/diagnose_audio.py "go blackpink"
```

Use `uv lock --upgrade-package discord.py` for Discord updates, then repeat the checks. Review `uv.lock` and perform a real listening test before accepting an update. Do not use plain `pip install -U` inside the locked environment. Latest stable yt-dlp at the compatibility check: [2026.10.26](https://github.com/yt-dlp/yt-dlp/releases/tag/2026.10.26).

Python 3.12.16 is a [security release](https://www.python.org/downloads/release/python-31216/); pip-audit audits Python packages, not the interpreter, Deno or FFmpeg. Direct `PyNaCl>=1.6.2` and `davey` retain voice support without discord.py's older voice-extra pin (see the [maintainer discussion](https://github.com/Rapptz/discord.py/discussions/10425)). Brotli 1.2.1 fixes [CVE-2026-111497](https://github.com/advisories/GHSA-9v8h-qqgm-4m35), which affected the original global Brotli 1.2.0. Updating PyNaCl 1.5.0 to 1.6.2 also removes the libsodium advisory CVE-2025-69277 from the installed package set; the maintainer notes Discord does not use the affected low-level custom cryptography operations. A clean audit means no known findings in that database at that time, not a guarantee of complete security. CI fails on audit findings **and** audit service failures; inspect the output to distinguish them.

### Manual acceptance before treating playback as verified

Only the operator performs this test with their bot token:

1. Stop the old bot instance, run `uv run bot`, join voice and use `-p go blackpink`. Confirm you actually hear music, then try the direct YouTube URL.
2. Add two songs, pause/resume, skip while paused and in loop-song mode. Check shuffle, move, jump and remove against the displayed numbers; verify no duplicates or missing entries.
3. Start a playlist/search, immediately clear or leave, and confirm late results do not refill the queue. Disconnect the bot manually and try a new play. If available, use a second server and confirm independent playback/prefixes.
4. Try control from another voice channel and prefix change without Manage Server. Verify both are refused. Restart and check that an authorized prefix change persists.
5. Start anonymously; test cookies only when needed, then test an expired/invalid file and recovery. Check errors without sharing secrets.

An initial HTTP 403 should stop the announcement and report an audio error. First check the locked versions and diagnostic rather than repeatedly exporting cookies. The final Discord listening test and Heroku deployment are deliberately not performed by the automated checks.


**Validation recorded during this refactor:** 168 offline/internal tests passed and pip-audit reported no known package vulnerabilities. A real anonymous name search through the refactored media/PCM path returned a 3,840-byte frame. A separate clean environment installed all 23 runtime packages successfully. Its direct-link diagnostic was blocked by YouTube bot verification; the original global extractor was then tested with that same direct link and was blocked by the same verification. Direct-link live acceptance was not passed in that check. The operator subsequently confirmed audible Discord playback after the davey compatibility correction; the newer control changes still require their manual acceptance. No .env, account cookies or Discord login were used for these checks. CI configuration is present but hosted Linux/Windows runs have not been executed here.

Name searches use Discord’s typing indicator instead of a “Looking for your music” message. Playlists retain their original loading embed, which is removed after preparation. `format_unavailable` now identifies a missing playable format separately from video availability; the bot does not infer deletion from the generic phrase “not available”. An anonymous live diagnostic for `black papermoon` successfully decoded a PCM frame during this follow-up. This does not establish the cause of the earlier failure.


**Voice compatibility fix:** keep `davey==0.1.4` with discord.py 2.7.1, matching the original audible bot. davey 0.2.0 introduced [breaking transition/key-management changes](https://github.com/Snazzah/davey/wiki/Migrating-to-0.2.0); this discord.py version calls `process_commit` / `process_welcome` but does not perform the newly required session `prepare_transition` / `execute_transition` calls. Decoded PCM and a Now Playing embed cannot validate that encryption path. The refactor initially upgraded davey to 0.2.0 incorrectly; uv.lock and generated requirements now restore 0.1.4. Do not upgrade davey independently of the Discord integration. Restart the running bot after syncing so it loads the corrected native library. DAVE encryption remains enabled; no encryption bypass or protocol downgrade is used. The regression tests and package audit passed after the correction, but audible Discord acceptance still requires the operator's listening test.


### Reading the console logs

Each request receives a short `request` ID, shared by its extraction and audio events. `server` shows the server name and ID; global startup/library events use `-`. Server names are restricted to a single printable line. Logs do not include searches, song titles, tokens, cookie paths/contents or signed stream URLs. Error events use fixed codes such as `format_unavailable`, plus exception type when relevant.

Logs, operator errors and project documentation use English. The original customizable Discord messages retain their wording, emojis and personality. For example (illustrative, not benchmark data):

```text
2026-11-03 18:24:22.166 INFO | server=Example (123) | request=000001 | Request accepted | operation=request guild_requests=1 global_requests=1
2026-11-03 18:24:26.326 INFO | server=Example (123) | request=000001 | Extraction finished | operation=extract result=ok elapsed_ms=4157 tracks=1 failed=0
2026-11-03 18:24:26.550 INFO | server=Example (123) | request=000001 | Discord audio player started | operation=play state=playing pending=0 loop=off startup_ms=224 request_to_start_ms=4384
```

| Metric | What it measures |
| --- | --- |
| `guild_wait_ms` | Time waiting behind previous preparation requests in that server |
| `worker_wait_ms` on extract | Time waiting for extraction capacity, including that server's stream-refresh capacity |
| `elapsed_ms` on extract | Worker lifetime and cleanup, including time suspended while progressive results are consumed; not a pure YouTube network benchmark |
| `queue_wait_ms` | Time from adding this entry to the playback queue until audio preparation begins |
| `worker_wait_ms` on audio | Wait for a first-frame decoding slot |
| `decode_ms` | FFmpeg creation through its first PCM frame |
| `startup_ms` | Audio preparation, including refresh/capacity waits when needed |
| `request_to_start_ms` | Accepted request through starting Discord's player, including playback queue wait; omitted for later loop repeats |

Starting Discord's player does not prove a listener received audio. Playlist preparation and first-song playback can overlap, so an audio-start event may precede the completion of the whole playlist request. No audio format, encoder bitrate, FFmpeg flags, extraction client or dependency version is changed by this logging update. No performance speedup is claimed. Restart the existing bot before `uv sync --locked` if Windows reports that `bot.exe` is locked.

Extraction failures now preserve only allowlisted diagnostic hints, such as `signature_challenge_failed`, `n_challenge_failed`, `javascript_runtime_missing`, `solver_components_warning` and `po_token_warning`. These hints can help explain a generic failure; they do not prove its cause, and a solver warning can coexist with successful playback. Raw yt-dlp warnings remain excluded to protect signed URLs and cookie paths. `bot_verification` identifies a YouTube challenge, not a fixed song-count limit; changing workers or repeatedly retrying is not a verified fix. No automatic verification retries or extractor-option changes were added in this diagnostic follow-up.


### Cookie input and concurrency tuning

The exported Netscape cookie file is operator-managed input. Each extraction loads it into its own memory stream; yt-dlp can update that job's cookie jar, but closing the job does not rewrite the original export. This prevents concurrent workers from overwriting the same file. Renew the export manually when needed. Expired-cookie warnings are retained as `cookies_expired_warning` diagnostics without logging their original text or paths. A valid file format does not prove that its account session is current or has access to an age-restricted video.

For an authenticated troubleshooting check, first confirm the same account can play the exact video in the browser, then configure YTDLP_COOKIES_FILE locally, restart the bot and request that exact URL. Report only the safe error code and diagnostic hints, never the cookie file or .env. Unit tests use fictitious cookies and no network; they do not validate the operator's account session.

`WORKERS=3` is a conservative starting limit retained from the operator's previous configuration, not a hardware-derived or gaming-tested maximum. It caps extraction processes across servers, not ongoing playback sessions. Each server still prepares one extraction at a time; increasing global workers does not accelerate that server's individual searches. `REQUESTS` and `GUILD_REQUESTS` bound accepted work rather than allocating CPU threads. Queue entries are metadata, not hundreds of running FFmpeg instances. AUDIO_WORKERS limits initial decoding; each server already playing can keep its own FFmpeg/audio-encoding work active.

For light use while gaming, keep the default limits first. Consider a small increase only when several servers genuinely extract at once and `worker_wait_ms` is consistently significant. Measure game frame times and CPU/RAM usage during representative concurrent work before declaring a higher limit stable. More workers do not improve audio quality or solve YouTube verification, and can increase request pressure. No load benchmark or gaming-stability guarantee is implied by the defaults.


### YouTube JavaScript and account access

The bot now has one installation workflow:

```powershell
uv sync --locked
uv run bot
```

EJS is part of the normal dependencies. Deno must be installed separately. Optional account access is controlled only by YTDLP_COOKIES_FILE; there are no separate dependency profiles or extra flags to remember.

An operator report showed `age_restricted` with `n_challenge_failed`, `po_token_warning` and `solver_components_warning` even though the account played the same video in a browser. After installing the matching EJS solver, the operator confirmed audible playback with cookies, with a recorded player startup time of 7.33 seconds. Its PO-token warning did not block that request. This validates that request, not every video or session.

A known limitation remains: a previous anonymous reference probe returned HTTP 403 with EJS installed, while the earlier solver-free environment decoded PCM. At the operator's request, the project now consistently includes EJS rather than requiring profile selection. Anonymous access is still attempted when cookies are absent, but is not guaranteed to succeed for every public video. No forced client, encryption bypass or automatic retry loop was added.

Safe hints `auth_cookies_recognized` and `auth_cookies_missing` show whether the extractor recognizes expected authentication cookies. Recognition does not prove that the session is current or has age access. To deliberately diagnose your own file without Discord, use:

```powershell
uv run python scripts/diagnose_audio.py "https://www.youtube.com/watch?v=oRSijEW_cDM" --cookies-file "C:/absolute/private/path/youtube.cookies.txt"
```

Only the operator runs this account check. Share safe error codes and hints, never the file or .env. Unit tests use fictitious cookies, not personal credentials.

The repository uses pyproject.toml and uv.lock as its dependency source; requirements.txt is not needed for uv or CI. Deployments that specifically require pip can generate an export from uv.lock when needed. The temporary baseline probe was removed; scripts/diagnose_audio.py remains the supported manual audio diagnostic. Local review notes, environments, caches, build output, .env and common cookie filenames are excluded from commit candidates. Procfile is retained for the documented optional Heroku worker.
