# Discord Music Bot CRUMMY v3.0 (Refactored)

<div align="center">
  <img src="https://user-images.githubusercontent.com/86860760/220523513-b32c0c1d-c003-408a-9569-a0c1d7d81ec5.jpg">
  <h1 align="center"> Discord Music Bot "Crummy" [New Version 3.0 - Refactored]</h1>
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
  <h3>Now Deployable on Heroku!</h3>
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
          <li><strong>Save it</strong> to some file or blog notes (you can only view it once, so make sure you have successfully saved it before moving on to the next step).</li>
        </ol>
        <img src="https://user-images.githubusercontent.com/86860760/221341089-cc655ce9-fa36-4e64-85f9-5ba35765659f.png">
      </li>
      <br>
      <li>
        <strong>Scroll down</strong> and <strong>enable</strong> these options.
        <img src="https://user-images.githubusercontent.com/86860760/221394463-ce9b9b09-1cb2-4af7-be3d-66ce08d04985.png">
      </li>
      <br>
      <li>
        <strong>Scroll down</strong> to "Bot Permissions" and <strong>click</strong> on "Administrator" and <strong>save changes</strong> <strong>(You can set the necessary permissions one by one if you do not want to give "Administrator")</strong>.
        <img src="https://user-images.githubusercontent.com/86860760/221341382-dae43315-6e62-4db8-948f-71b0751b67bf.png">
      </li>
      <br>
      <li>
        <strong>Click</strong> on "OAuth2" settings and <strong>go to</strong> "URL Generator" option.
        <ol>
          <li>
            <strong>Select</strong> "Bot" in "Scopes" and <strong>scroll down and select</strong> "Administrator" in "Bot Permissions.
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
    <strong>Follow the steps of</strong><a href="https://youtu.be/5xgegeBL0kw"> How to install FFmpeg</a> to proceed to the final step (the video is not mine so I would ask you to leave your support for the creator with a like or a comment).
  </div>
  <div align="left">
    <h3>Step 3: Download and configure the Program</h3>
    <strong>It is expected having Python and optionally Git installed already, If not click on</strong><a href="https://youtu.be/nU2Egc3Zx3Q?si=0JEnBFNEuXjVf-j1"> How to Install Python</a> and <a href="https://git-scm.com/downloads"> Git Download Page</a> to proceed with the process (the video is not mine so I would ask you to leave your support for the creator with a like or a comment).
    <ol>
      <li><strong>Clone</strong> the repo.</li>
      <pre><code>git clone https://github.com/MarcoTheBigCreator/DiscordMusicBot.git</code></pre>
      <p>If Git is not installed. <strong>Download</strong> manually the repo.</p>
      <img src="https://github.com/MarcoTheBigCreator/DiscordMusicBot/assets/86860760/4f4b1a12-002f-4738-9511-66258acaa11a">
      <br>
      <br>
      <li><strong>Install</strong> the dependencies (make sure you're on the repo's folder to execute the command).</li>
      <pre><code>pip install -r requirements.txt</code></pre>
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
      <pre><code>python main.py</code></pre>
      <br>
      <li><strong>Optional:</strong> you can make a shortcut of the main.py file and move it to the desktop to run it directly, as well as assign some icon to it.</li>
    </ol>
  </div>
  <br>

  <!-- Heroku Deploying -->
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
      <!-- <br>
      <li><strong>Optional: Install</strong> the dependencies (make sure you're on the repo's folder to execute the command).</li>
      <pre><code>pip install -r requirements.txt</code></pre> -->
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
    <li><strong>Modify</strong> the runtime.txt with the latest version of Python (in order to make a change to commit).</li>
      <img src="https://github.com/MarcoTheBigCreator/DiscordMusicBot/assets/86860760/cd121a58-9213-47c5-8074-9d01d3831180">
      <br>
      <br>
    <li><strong>Commit</strong> the runtime.txt change.</li>
    <pre><code>git commit -m "update runtime version"</code></pre>
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
    <p>Below is a list of commands available for Crummy v3.0 (Refactored), along with their aliases and functions. Use these commands to control the music playback in your server.</p>
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
          <td>Shuffle queue</td>
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
          <td>Change bot prefix</td>
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
<p>Other customizable settings in <code>constants.py</code>:</p>
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
<li><strong>Modify Embed Styles:</strong> Change colors and formatting by editing the embed creation methods in <code>music_bot.py</code></li>
</ul>
<p><strong>💡 Pro Tip:</strong> After making changes to <code>constants.py</code>, restart the bot to see your customizations take effect!</p>

  </div>
  <hr>
  <div align="center">
    <h2>Report Issues</h2>
    <p>We apologize for any errors you may be experiencing.</p>
    <p>Please keep in mind that this was made just for fun, other functionalities could be added with collaboration work. However, if you encounter an error while attempting an exercise that should have answers, please <a href="https://github.com/MarcoTheBigCreator/DiscordMusicBot/issues">open an issue</a> and we will work to resolve it as soon as possible</p>
<p>When reporting an issue, please make sure to include the URL for the exercise. Thank you for your patience.</p>
  </div>
</div>
