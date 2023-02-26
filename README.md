<div align="center">
  <img src="https://user-images.githubusercontent.com/86860760/220523513-b32c0c1d-c003-408a-9569-a0c1d7d81ec5.jpg">
  <h1 align="center"> Discord Music Bot "Crummy" </h1>
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
  <br>
  <br>
  <a href="https://github.com/MarcoTheBigCreator/DiscordMusicBot/stargazers"><strong>Give to Crummy a Star!</strong></a>
</div>
<div>
  <br>
  <h2 align="center"> How does it look? </h2>
  <p align="center">
  <img src="https://user-images.githubusercontent.com/86860760/220539038-a159bc06-9bd5-4447-a39c-ecab82c1413c.png" style="width: 60%;">
  <img src="https://user-images.githubusercontent.com/86860760/220539054-b0668e49-b4f2-4868-9e05-1511c3018d46.png" style="width: 46%;">
  <img src="https://user-images.githubusercontent.com/86860760/220660246-e1aa7530-5e02-4eea-890a-5a799dae0034.png" style="width: 31%;">
  <br>
</div>
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
        <strong>Scroll down and enable these options</strong>.
        <img src="https://user-images.githubusercontent.com/86860760/221393810-47983733-5351-4342-8dc1-d2c39b1e0107.png">
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
        <strong>Paste</strong> the link in a new tab to invite your bot to the server of your choice.
      </li>
    </ol>
  </div>
  <div align="left">
    <h3>Step 2: Install FFmpeg</h3>
    <strong>Follow the steps of</strong><a href="https://youtu.be/5xgegeBL0kw"> How to install FFmpeg</a> to proceed to the final step (the video is not mine so I would ask you to leave your support for the creator with a like or a comment).
  </div>  
  <div align="left">
    <h3>Step 3: Install the Program</h3>
    <ol>
      <li><strong>Clone</strong> the repo.</li>
      git clone https://github.com/MarcoTheBigCreator/DiscordMusicBot.git
      <br>
      <li><strong>Install</strong> the dependencies.</li>
      <pre>pip install -r requirements.txt</pre>
      <br>
      <li><strong>Open</strong> main.py in a code editor and <strong>insert</strong> your Bot's Token (the one you previously copied and saved).</li>
      <img src="https://user-images.githubusercontent.com/86860760/221344485-6e98f07b-924f-4b46-8d0c-212031d89eba.png">
      <br>
      <br>
      <li><strong>Run</strong> the program.</li>
      <pre>python main.py</pre>
      <br>
      <li><strong>Write</strong> "-help" in the chat of the server where the bot is located to show all commands.</li>
      <br>
      <li><strong>Optional:</strong> you can make a shortcut of the main.py file and move it to the desktop to run it directly, as well as assign some icon to it.</li>
    </ol>
  </div>
  <br>
  <div align="center">
    <h2>Report Issues</h2>
    <p>We apologize for any errors you may be experiencing.</p>
    <p>Please keep in mind that this was made just for fun, other functionalities could be added with collaborational work. However, if you encounter an error while attempting an exercise that should have answers, please <a href="https://github.com/MarcoTheBigCreator/DiscordMusicBot/issues">open an issue</a> and we will work to resolve it as soon as possible</p>
<p>When reporting an issue, please make sure to include the URL for the exercise. Thank you for your patience.</p>
  </div>
</div>
