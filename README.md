**Linux & Bash**

for Complete Beginners

*A friendly guide to deploying your AI Voice Assistant on the Radxa Dragon Q6A*

This guide explains the commands needed to get your AI voice assistant up and running on your Radxa device. Each command is broken down into plain English so you always understand exactly what is happening and why.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>What you will need</strong></p>
<p>A Radxa Dragon Q6A device connected to your local network</p>
<p>Your laptop or desktop computer (Windows, Mac, or Linux)</p>
<p>The voice assistant project files (from a USB drive or download)</p>
<p>A terminal application open on your laptop</p></td>
</tr>
</tbody>
</table>

**01 Getting the Files onto your Radxa**

Before anything else, the project files need to live on the Radxa. There are two ways to do this. You only need to choose **one** of them.

**Option A — git clone (files on GitHub)**

Use this if your project is hosted online at GitHub or GitLab. The **git clone** command downloads the entire project folder in a single step.

|                                                       |
|-------------------------------------------------------|
| git clone https://github.com/yourname/voice-assistant |
| cd voice-assistant                                    |

|                        |                                                                 |
|------------------------|-----------------------------------------------------------------|
| **Command**            | **What it does**                                                |
| **git clone \<url\>**  | Downloads all project files from the internet into a new folder |
| **cd voice-assistant** | Moves you inside that folder (cd = change directory)            |

**Option B — scp (files on your laptop)**

Use this if the files are already on your laptop and you just want to copy them over your home network. **scp** stands for Secure Copy Protocol. Think of it as **cp** (copy), but over a network connection.

|                                                           |
|-----------------------------------------------------------|
| \# Run this on YOUR LAPTOP (not the Radxa)                |
| scp -r ./voice_assistant radxa@192.168.1.100:/home/radxa/ |

|                         |                                                        |
|-------------------------|--------------------------------------------------------|
| **Part**                | **Meaning**                                            |
| **scp**                 | The copy-over-network command                          |
| **-r**                  | Copy recursively (the whole folder, not just one file) |
| **./voice_assistant**   | The folder on your laptop you want to copy             |
| **radxa@192.168.1.100** | Username @ IP address of your Radxa on the network     |
| **/home/radxa/**        | The destination folder on the Radxa                    |

After copying, SSH into the Radxa to continue working there:

|                         |
|-------------------------|
| ssh radxa@192.168.1.100 |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>How to find your Radxa's IP address</strong></p>
<p>On the Radxa, run: hostname -I</p>
<p>Or check your router's admin page — usually http://192.168.1.1 — and look for a device named radxa or rock.</p></td>
</tr>
</tbody>
</table>

**02 Making the Script Executable**

|                   |
|-------------------|
| chmod +x setup.sh |

When you copy a **.sh** script onto a Linux system, it arrives as a plain text file. Linux will **not** run it until you explicitly grant it permission. That is what **chmod +x** does.

|              |                                                         |
|--------------|---------------------------------------------------------|
| **Part**     | **Meaning**                                             |
| **chmod**    | Change Mode — the command that manages file permissions |
| **+x**       | Add the execute permission to this file                 |
| **setup.sh** | The file you are granting permission to                 |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>What happens if you skip this?</strong></p>
<p>Running <strong>./setup.sh</strong> without first running <strong>chmod +x</strong> will produce: Permission denied. This is Linux protecting you from accidentally running untrusted scripts.</p></td>
</tr>
</tbody>
</table>

**03 The && Operator**

|                                 |
|---------------------------------|
| chmod +x setup.sh && ./setup.sh |

The **&&** symbol chains two commands together with a condition: **only run the second command if the first one succeeded.**

|                    |                                |
|--------------------|--------------------------------|
| **Scenario**       | **What happens**               |
| **chmod succeeds** | ./setup.sh runs automatically  |
| **chmod fails**    | ./setup.sh is skipped entirely |

This is a safety pattern. Without **&&** you would need to type each command separately and visually check that nothing went wrong before proceeding. Chaining with **&&** automates that check for you.

**04 Running the Script with ./**

|            |
|------------|
| ./setup.sh |

The **./** prefix tells Linux: look for this file **in the current folder**. This might seem strange at first, so here is why it exists.

When you type a command like **ls** or **python3** , Linux searches a list of known system folders (called **PATH** ) to find the program. Your current folder is **not** in that list by default. So if you typed just **setup.sh** , Linux would say command not found even though the file is sitting right there.

|              |                                         |
|--------------|-----------------------------------------|
| **Symbol**   | **Meaning**                             |
| **.**        | The current folder you are in right now |
| **/**        | A separator between folder and filename |
| **setup.sh** | The script to run                       |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Mental model</strong></p>
<p>Think of <strong>./</strong> as saying: not the system version of this command, but the one right here in my folder.</p></td>
</tr>
</tbody>
</table>

**05 Putting it All Together**

Here is the complete sequence you run, in order, from start to finish:

**1** Get the files onto the Radxa (choose git clone or scp)

|                                                           |
|-----------------------------------------------------------|
| \# If using GitHub:                                       |
| git clone https://github.com/yourname/voice-assistant     |
| cd voice-assistant                                        |
|                                                           |
| \# If copying from your laptop (run on laptop first):     |
| scp -r ./voice_assistant radxa@192.168.1.100:/home/radxa/ |
| ssh radxa@192.168.1.100                                   |
| cd voice_assistant                                        |

**2** Make the setup script executable, then run it

|                                 |
|---------------------------------|
| chmod +x setup.sh && ./setup.sh |

**3** Wait for setup to finish, then start the assistant

|                                 |
|---------------------------------|
| source ~/voice_env/bin/activate |
| python3 assistant.py            |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>What setup.sh does automatically</strong></p>
<p>Installs system packages (audio libraries, Python, ffmpeg)</p>
<p>Installs Ollama and downloads the Qwen2.5:7B language model</p>
<p>Creates a Python virtual environment and installs all dependencies</p>
<p>Pre-downloads the Whisper speech recognition model</p>
<p>Registers a systemd service so the assistant starts on boot</p></td>
</tr>
</tbody>
</table>

**06 Quick Reference**

|                                     |                                                    |
|-------------------------------------|----------------------------------------------------|
| **Command**                         | **Plain English meaning**                          |
| **git clone \<url\>**               | Download a project from the internet               |
| **scp -r folder user@ip:path**      | Copy a folder to another computer over the network |
| **ssh user@ip**                     | Log into another computer via the terminal         |
| **cd folder**                       | Move into a folder                                 |
| **chmod +x file.sh**                | Allow a script to be executed                      |
| **./script.sh**                     | Run a script in the current folder                 |
| **cmd1 && cmd2**                    | Run cmd2 only if cmd1 succeeded                    |
| **source ~/voice_env/bin/activate** | Activate the Python virtual environment            |
| **python3 assistant.py**            | Start the voice assistant                          |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>If something goes wrong</strong></p>
<p>Check the log: tail -f /tmp/voice_assistant.log</p>
<p>Check if Ollama is running: systemctl status ollama</p>
<p>Re-run setup safely at any time: chmod +x setup.sh &amp;&amp; ./setup.sh</p></td>
</tr>
</tbody>
</table>

**Running on Windows**

Setting up WSL2 + Ubuntu for VS Code

*How to get a full Linux environment running inside Windows so you can deploy the AI voice assistant without a separate Linux machine*

WSL stands for **Windows Subsystem for Linux**. It lets you run a real Ubuntu Linux terminal directly inside Windows with no virtual machine, no dual boot, and no separate computer needed. VS Code integrates with it seamlessly so everything feels native.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>What you will need</strong></p>
<p>Windows 10 version 2004 or later, or Windows 11 (any version)</p>
<p>An internet connection for downloading Ubuntu</p>
<p>About 5 minutes and one restart</p></td>
</tr>
</tbody>
</table>

**01 Check if WSL is Already Installed**

Open PowerShell or Command Prompt and run:

|              |
|--------------|
| wsl --status |

Then check which distributions are installed:

|                      |
|----------------------|
| wsl --list --verbose |

|                                  |                                                        |
|----------------------------------|--------------------------------------------------------|
| **Result**                       | **What it means**                                      |
| **Default Distribution: Ubuntu** | WSL and Ubuntu are ready — skip to section 04          |
| **docker-desktop only**          | WSL installed but Ubuntu is missing — go to section 03 |
| **wsl: command not found**       | WSL is not installed at all — go to section 02         |

**02 Install WSL2 (if not installed)**

Open PowerShell as Administrator — right-click the Start menu and choose Windows Terminal (Admin) or PowerShell (Admin) — then run:

|               |
|---------------|
| wsl --install |

This single command enables WSL2, downloads Ubuntu, and sets everything up automatically. When it finishes, **restart your machine**. This step is required — WSL will not work until after a restart.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Must run as Administrator</strong></p>
<p>If you run this in a normal PowerShell window you will get an Access Denied error. Right-click PowerShell and choose Run as Administrator before running the command.</p></td>
</tr>
</tbody>
</table>

**03 Install Ubuntu (if WSL exists but Ubuntu is missing)**

If WSL is already installed but only docker-desktop appears in the list, install Ubuntu separately:

|                         |
|-------------------------|
| wsl --install -d Ubuntu |

After it finishes, Ubuntu will launch automatically and ask you to create a Linux username and password:

|                                |
|--------------------------------|
| Enter new UNIX username: sagar |
| New password:                  |
| Retype new password:           |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Important notes about the password prompt</strong></p>
<p>Nothing appears on screen when you type your password — this is normal Linux behaviour. It is still registering every keystroke, it just hides the characters for security.</p>
<p>The username does not need to match your Windows username.</p>
<p>Remember this password — you will need it whenever a command requires sudo (administrator access inside Linux).</p></td>
</tr>
</tbody>
</table>

**04 Verify Ubuntu is Ready**

Run this in PowerShell to confirm Ubuntu is installed:

|                      |
|----------------------|
| wsl --list --verbose |

You should see Ubuntu listed alongside docker-desktop:

|                             |
|-----------------------------|
| NAME STATE VERSION          |
| \* docker-desktop Running 2 |
| Ubuntu Stopped 2            |

Open Ubuntu to confirm it works:

|               |
|---------------|
| wsl -d Ubuntu |

Your prompt changes from **PS C:\\..\>** to something like:

|                   |
|-------------------|
| sagar@DESKTOP:~\$ |

That **\$** prompt means you are now inside Linux. You can run any Linux command from here.

**05 Connect VS Code to WSL**

VS Code has a built-in WSL extension that lets you work inside Ubuntu while staying in the VS Code interface you already know.

**1** Install the WSL extension in VS Code

Press Ctrl + Shift + X to open the Extensions panel. Search for WSL and install the extension published by Microsoft.

**2** Connect to Ubuntu

Click the green **\>\<** button in the very bottom-left corner of VS Code. Select Connect to WSL using Distro, then select Ubuntu.

**3** Confirm the connection

VS Code will reopen. You will see **WSL: Ubuntu** in the bottom-left corner. Every terminal you open in VS Code now runs inside Ubuntu automatically.

**06 Navigate to Your Project Files**

Inside WSL, your Windows **C:** drive is mounted at **/mnt/c/** . Your Downloads folder on Windows is accessible from Linux at:

|                               |
|-------------------------------|
| /mnt/c/Users/sagar/Downloads/ |

Navigate to the voice assistant project folder:

|                                                    |
|----------------------------------------------------|
| cd /mnt/c/Users/sagar/Downloads/ai_voice_assistant |

Confirm the three project files are there:

|     |
|-----|
| ls  |

You should see:

|                                        |
|----------------------------------------|
| assistant.py requirements.txt setup.sh |

You are now ready to run the setup script exactly as described in Part 1 of this guide:

|                                 |
|---------------------------------|
| chmod +x setup.sh && ./setup.sh |

**07 WSL Quick Reference**

|                             |                                                      |
|-----------------------------|------------------------------------------------------|
| **Command**                 | **What it does**                                     |
| **wsl --install**           | Install WSL2 and Ubuntu (run in PowerShell as Admin) |
| **wsl --install -d Ubuntu** | Install Ubuntu specifically                          |
| **wsl --list --verbose**    | List all installed Linux distributions               |
| **wsl --status**            | Show WSL version and default distribution            |
| **wsl -d Ubuntu**           | Open Ubuntu terminal from PowerShell                 |
| **wsl --shutdown**          | Stop all running WSL distributions                   |
| **cd /mnt/c/Users/...**     | Navigate to Windows files from inside Linux          |
| **explorer.exe .**          | Open current Linux folder in Windows Explorer        |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Tip — wsl commands only work in PowerShell</strong></p>
<p>Once you are inside Ubuntu (your prompt shows <strong>$</strong> ), wsl commands will say command not found. That is normal — wsl is a Windows tool. Switch back to PowerShell to use it.</p></td>
</tr>
</tbody>
</table>

**Voice Assistant**

Setup & Launch Guide

*Step-by-step instructions to install, configure, and run the AI voice assistant — from a fresh Ubuntu terminal to speaking your first response*

These steps are identical whether you are on a Radxa Dragon Q6A or running Ubuntu via WSL2 on Windows.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>What gets installed</strong></p>
<p>Ollama — the local LLM runtime that runs Qwen2.5:7B on your machine</p>
<p>Qwen2.5:7B — the language model that generates responses (approx. 5 GB download)</p>
<p>Whisper base — the speech-to-text model that transcribes your voice</p>
<p>Python virtual environment with all required libraries</p>
<p>Systemd service for auto-start on boot (Radxa and native Linux only)</p></td>
</tr>
</tbody>
</table>

**01 Get the Project Files Ready**

All three files must be in the same folder before you begin:

|                      |                                                |
|----------------------|------------------------------------------------|
| **File**             | **Purpose**                                    |
| **assistant.py**     | The main voice assistant program               |
| **setup.sh**         | The install script that sets everything up     |
| **requirements.txt** | The Python packages that setup.sh will install |

Navigate to that folder. On WSL (Windows users) if the files are already in your Windows Downloads folder:

|                                                    |
|----------------------------------------------------|
| cd /mnt/c/Users/sagar/Downloads/ai_voice_assistant |

On Radxa or native Linux:

|                      |
|----------------------|
| cd ~/voice_assistant |

**Copying files to a remote device over the network (scp)**

If you want to copy the project from your laptop to another machine on the same network — for example, from your Windows/WSL terminal to a Radxa — use **scp** . This is exactly the command used in this project:

|                                                           |
|-----------------------------------------------------------|
| scp -r ./ai_voice_assistant sagar@192.172.0.45:~/projects |

|                          |                                                           |
|--------------------------|-----------------------------------------------------------|
| **Part**                 | **Meaning**                                               |
| **scp**                  | Secure Copy — copies files over the network via SSH       |
| **-r**                   | Recursive — copies the entire folder, not just one file   |
| **./ai_voice_assistant** | The folder on your local machine you want to copy         |
| **sagar@192.172.0.45**   | Username and IP address of the target device (your Radxa) |
| **:~/projects**          | Destination path on the remote device (~/projects folder) |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>How to find your device IP address</strong></p>
<p>On the Radxa or target Linux device, run: hostname -I</p>
<p>Or check your router admin page (usually http://192.168.0.1 or http://192.168.1.1) and look for a device named radxa or similar.</p></td>
</tr>
</tbody>
</table>

After scp finishes, SSH into the remote device and navigate to the copied folder:

|                                  |
|----------------------------------|
| ssh sagar@192.168.0.38           |
| cd ~/projects/ai_voice_assistant |

Confirm all three files are present:

|     |
|-----|
| ls  |

Expected output:

|                                        |
|----------------------------------------|
| assistant.py requirements.txt setup.sh |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Missing files?</strong></p>
<p>Do not proceed if any of the three files are missing. Copy them into the same folder first. setup.sh will fail immediately if requirements.txt is not alongside it.</p></td>
</tr>
</tbody>
</table>

**02 Run the Setup Script**

This single command makes the script executable and immediately runs it:

|                                 |
|---------------------------------|
| chmod +x setup.sh && ./setup.sh |

The script works through nine steps automatically:

|                         |                                                            |
|-------------------------|------------------------------------------------------------|
| **Step**                | **What is happening**                                      |
| **1 — System packages** | Installs audio drivers, Python, ffmpeg via apt-get         |
| **2 — Ollama install**  | Downloads and installs the Ollama LLM runtime              |
| **3 — Ollama service**  | Starts Ollama running in the background                    |
| **4 — Qwen2.5:7B pull** | Downloads the 5 GB language model (takes 5 to 15 mins)     |
| **5 — Python venv**     | Creates an isolated Python environment at ~/voice_env      |
| **6 — Python packages** | Installs all packages listed in requirements.txt           |
| **7 — Whisper model**   | Pre-downloads the Whisper base speech recognition model    |
| **8 — Audio check**     | Lists your available microphone and speaker devices        |
| **9 — Systemd service** | Registers auto-start on boot (Radxa and native Linux only) |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>The model download is the slow part</strong></p>
<p>Step 4 downloads Qwen2.5:7B which is approximately 5 GB. On a typical home broadband connection this takes 5 to 15 minutes. A progress bar will appear — just leave it running and wait for it to finish.</p></td>
</tr>
</tbody>
</table>

When setup completes you will see:

|                                              |
|----------------------------------------------|
| ============================================ |
| Setup complete!                              |
| ============================================ |

**03 Start the Voice Assistant**

Every time you want to run the assistant in a new terminal, activate the Python environment first then launch the program:

|                                 |
|---------------------------------|
| source ~/voice_env/bin/activate |
| python3 assistant.py            |

|                                     |                                                                     |
|-------------------------------------|---------------------------------------------------------------------|
| **Command**                         | **Why it is needed**                                                |
| **source ~/voice_env/bin/activate** | Switches Python to the isolated environment where all packages live |
| **python3 assistant.py**            | Starts the voice assistant program                                  |

When it starts successfully you will see:

|                                                         |
|---------------------------------------------------------|
| Loading Whisper \[base\] on cpu...                      |
| ✓ Whisper loaded                                        |
| 🔊 Speaking: Voice assistant ready. How can I help you? |
| 🎙 Listening... (speak now)                              |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Why activate the environment every time?</strong></p>
<p>Activating the virtual environment only lasts for the current terminal session. If you close the terminal and open a new one, run the source command again before starting the assistant. The environment itself never needs to be recreated — only activated.</p></td>
</tr>
</tbody>
</table>

**04 How the Assistant Works**

Once running, the assistant continuously loops through four stages:

|                    |                                                                   |
|--------------------|-------------------------------------------------------------------|
| **Stage**          | **What happens**                                                  |
| **1 — Listen**     | Records your voice until 1.5 seconds of silence is detected       |
| **2 — Transcribe** | Whisper converts the audio to text (typically 0.4 to 0.9 seconds) |
| **3 — Think**      | Qwen2.5:7B generates a response via Ollama (1 to 4 seconds)       |
| **4 — Speak**      | pyttsx3 reads the response aloud through your speakers            |

Built-in voice commands you can say at any time:

|                                    |                                                |
|------------------------------------|------------------------------------------------|
| **Say this**                       | **What it does**                               |
| **reset or clear history**         | Wipes the conversation memory and starts fresh |
| **goodbye or bye or exit or quit** | Stops the assistant gracefully                 |

**05 Run as a Background Service (Radxa / Native Linux)**

On Radxa or native Linux, setup.sh registers a systemd service so the assistant starts automatically on every boot — no terminal, no manual activation needed.

**Start the service now**

|                                      |
|--------------------------------------|
| sudo systemctl start voice-assistant |

**Enable auto-start on every boot**

|                                       |
|---------------------------------------|
| sudo systemctl enable voice-assistant |

**Check if the service is running**

|                                       |
|---------------------------------------|
| sudo systemctl status voice-assistant |

**Stop the service**

|                                     |
|-------------------------------------|
| sudo systemctl stop voice-assistant |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>WSL users — systemd is not supported</strong></p>
<p>WSL2 does not support systemd by default. On Windows, start the assistant manually each session using the source and python3 commands shown in section 03.</p></td>
</tr>
</tbody>
</table>

**06 Fix Audio on Radxa (SSH Sessions)**

When running the assistant over SSH, a common error is: **aplay: main:834: audio open error: Invalid argument** . This happens because SSH sessions do not automatically attach to an audio device. Follow these steps to fix it.

**Step 1 — list available audio devices**

Run this to see every playback device the Radxa can see:

|          |
|----------|
| aplay -l |

You will see output similar to this:

|                                                                                  |
|----------------------------------------------------------------------------------|
| \*\*\*\* List of PLAYBACK Hardware Devices \*\*\*\*                              |
| card 0: QCS6490RadxaDra \[QCS6490-Radxa-Dragon-Q6A\], device 0: MultiMedia1 (\*) |
| card 1: MS \[Jabra EVOLVE 20 MS\], device 0: USB Audio \[USB Audio\]             |

|            |                                                   |
|------------|---------------------------------------------------|
| **Device** | **What it is**                                    |
| **card 0** | Radxa onboard audio chipset                       |
| **card 1** | USB headset or external audio device (e.g. Jabra) |

**Step 2 — set the default audio device**

Create (or overwrite) the ALSA configuration file to tell Linux which card to use by default. Use the card number from the output above — card 1 if you have a USB headset, card 0 for onboard audio:

|                  |
|------------------|
| nano ~/.asoundrc |

Add these two lines — replace 1 with your card number if different:

|                     |
|---------------------|
| defaults.pcm.card 1 |
| defaults.ctl.card 1 |

Save the file: press Ctrl+O then Enter, then exit with Ctrl+X.

**Step 3 — test speaker playback**

Run a speaker test on the chosen device. Replace 1,0 with your card and device numbers:

|                                    |
|------------------------------------|
| speaker-test -t wav -c 2 -D hw:1,0 |

You should hear white noise or a tone through the speaker or headset. Press Ctrl+C to stop.

**Step 4 — test microphone recording**

This records 5 seconds of audio then immediately plays it back so you can confirm both mic and speaker are working:

|                                                                                     |
|-------------------------------------------------------------------------------------|
| arecord -D hw:1,0 -f S16_LE -r 16000 -c 1 -d 5 test.wav && aplay -D hw:1,0 test.wav |

Speak into the microphone while it records. You should hear your own voice played back after 5 seconds.

|                     |                                                      |
|---------------------|------------------------------------------------------|
| **Part of command** | **Meaning**                                          |
| **arecord**         | Record audio from microphone                         |
| **-D hw:1,0**       | Use card 1, device 0 (match to your aplay -l output) |
| **-f S16_LE**       | Audio format: 16-bit signed little-endian            |
| **-r 16000**        | Sample rate: 16000 Hz (required by Whisper)          |
| **-c 1**            | Mono channel (single microphone)                     |
| **-d 5**            | Record for 5 seconds then stop                       |
| **test.wav**        | Save recording to this file                          |
| **&& aplay ...**    | If recording succeeded, immediately play it back     |

**Step 5 — run the assistant**

Once speaker and microphone tests both pass, start the assistant normally:

|                                 |
|---------------------------------|
| source ~/voice_env/bin/activate |
| python3 assistant.py            |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Using a USB headset like the Jabra EVOLVE 20</strong></p>
<p>A USB headset is the most reliable option on Radxa because it is self-contained — mic and speaker in one device on a single card number. Plug it in before running aplay -l and use that card number in ~/.asoundrc.</p></td>
</tr>
</tbody>
</table>

**07 Speed Up the Voice Assistant**

If the assistant feels slow at any stage — listening, transcribing, or thinking — each problem has a different fix. This section covers all three and also how to improve the voice quality.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Summary of all speed and quality improvements</strong></p>
<p>Fix _rms normalisation bug + calibrate silence_threshold → silence detected instantly</p>
<p>silence_duration 0.6 + chunk_size 200ms → saves ~0.9s per turn during recording</p>
<p>faster-whisper tiny int8 → approximately 4x faster transcription than standard Whisper</p>
<p>qwen2.5:0.5b or 1.5b → approximately 10x faster LLM responses than 7B</p>
<p>Piper TTS → significantly more natural sounding voice than espeak-ng</p></td>
</tr>
</tbody>
</table>

**Fix 1 — Slow listening (audio recording)**

The silence detection settings control how long the assistant waits after you stop speaking before it starts transcribing. Reducing these cuts dead time at the end of every turn.

In the CONFIG block in assistant.py change:

|                                                                          |
|--------------------------------------------------------------------------|
| "silence_threshold": 0.005, \# calibrated to your microphone — see below |
| "silence_duration": 0.6, \# was 1.5 — stops recording sooner             |

Also increase the audio chunk size in the AudioRecorder to reduce Python loop overhead during recording. Find this line in the record_until_silence method:

|                                                           |
|-----------------------------------------------------------|
| chunk_size = int(self.sample_rate \* 0.1) \# 100ms chunks |

Change it to:

|                                                                               |
|-------------------------------------------------------------------------------|
| chunk_size = int(self.sample_rate \* 0.2) \# 200ms chunks — less CPU overhead |

|                             |                                                                             |
|-----------------------------|-----------------------------------------------------------------------------|
| **Setting**                 | **What it does**                                                            |
| **silence_threshold 0.005** | Sits above background noise floor, below speech — calibrated value          |
| **silence_duration 0.6**    | Stops recording after 0.6s of silence instead of 1.5s — saves 0.9s per turn |
| **chunk_size 200ms**        | Fewer Python loop iterations per second — less CPU overhead while recording |

**Important — fix the RMS normalisation bug first**

The **\_rms** method in the original **AudioRecorder** class has a bug — it calculates RMS on raw int16 values (range -32768 to +32767) instead of normalised float values (range -1.0 to +1.0). This means the threshold values in CONFIG are on a completely different scale to what the code is actually measuring, so silence detection never works correctly.

Find the \_rms method in assistant.py:

|                                                         |
|---------------------------------------------------------|
| def \_rms(self, data):                                  |
| return np.sqrt(np.mean(data.astype(np.float32) \*\* 2)) |

Replace it with this corrected version:

|                                                                   |
|-------------------------------------------------------------------|
| def \_rms(self, data):                                            |
| \# Normalise int16 range (-32768 to 32767) to float (-1.0 to 1.0) |
| normalised = data.astype(np.float32) / 32768.0                    |
| return np.sqrt(np.mean(normalised \*\* 2))                        |

|                  |                                        |
|------------------|----------------------------------------|
| **Version**      | **What it measures**                   |
| **Old (broken)** | Raw int16 amplitude — scale of tens    |
| **New (fixed)**  | Normalised float — scale of 0.0 to 1.0 |

**How to calibrate silence_threshold for your microphone**

Every microphone and room has a different background noise floor. Rather than guessing, measure it first. Save this as a file called rms_test.py:

|                                                                             |
|-----------------------------------------------------------------------------|
| import sounddevice as sd                                                    |
| import numpy as np                                                          |
|                                                                             |
| print('Silence test — stay quiet...')                                       |
| rec = sd.rec(int(5 \* 16000), samplerate=16000, channels=1, dtype='int16')  |
| sd.wait()                                                                   |
| for i, chunk in enumerate(rec.reshape(-1, 1600)\[:10\]):                    |
| rms = np.sqrt(np.mean((chunk.astype('float32') / 32768.0) \*\* 2))          |
| print(f'Chunk {i:02d}: RMS = {rms:.6f}')                                    |
|                                                                             |
| print('Now speak normally for 3 seconds...')                                |
| rec2 = sd.rec(int(3 \* 16000), samplerate=16000, channels=1, dtype='int16') |
| sd.wait()                                                                   |
| for i, chunk in enumerate(rec2.reshape(-1, 1600)):                          |
| rms = np.sqrt(np.mean((chunk.astype('float32') / 32768.0) \*\* 2))          |
| print(f'Speech {i:02d}: RMS = {rms:.6f}')                                   |

Run it with:

|                     |
|---------------------|
| python3 rms_test.py |

Run this twice — once in silence, once while speaking. Then set silence_threshold to a value clearly between the two:

|                 |                 |
|-----------------|-----------------|
| **Silence RMS** | **Speech RMS**  |
| **~0.0009**     | ~0.017 to 0.030 |
| **~0.002**      | ~0.020 to 0.040 |
| **~0.005**      | ~0.030 to 0.060 |
| **~0.010**      | ~0.050 to 0.080 |

The rule is: set threshold to roughly 5 times your silence RMS value. This gives enough gap above background noise that hum and breathing never trigger it, while still catching speech immediately.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Real calibration result — Jabra EVOLVE 20 on Radxa</strong></p>
<p>Silence floor: RMS = 0.0009</p>
<p>Speech peak: RMS = 0.030</p>
<p>Threshold set: 0.005 (5.5x above noise floor, 6x below speech start)</p></td>
</tr>
</tbody>
</table>

**Fix 2 — Slow transcribing (Whisper)**

Two options here — quick wins with standard Whisper, or a full replacement with faster-whisper which is 4x faster on CPU.

**Option A — tune standard Whisper (quick fix)**

In the CONFIG block change:

|                          |
|--------------------------|
| "whisper_model": "tiny", |
| "whisper_device": "cpu", |

Then find the transcribe method inside the WhisperSTT class and replace the model.transcribe call with:

|                                   |
|-----------------------------------|
| result = self.model.transcribe(   |
| audio_path,                       |
| language="en",                    |
| fp16=False,                       |
| condition_on_previous_text=False, |
| temperature=0,                    |
| best_of=1,                        |
| beam_size=1,                      |
| )                                 |

|                          |                                                                |
|--------------------------|----------------------------------------------------------------|
| **Setting**              | **What it does**                                               |
| **tiny instead of base** | Smaller model — roughly 3x faster, minimal accuracy loss       |
| **beam_size=1**          | Stops Whisper running multiple passes — biggest single speedup |
| **best_of=1**            | Only generates one candidate transcription instead of several  |
| **temperature=0**        | Deterministic output — no random sampling overhead             |

**Option B — replace with faster-whisper (recommended)**

faster-whisper is a reimplementation of Whisper using CTranslate2. It runs approximately **4x faster** on CPU and uses less memory than standard Whisper. This is the most impactful single change you can make to listening speed.

Install it:

|                            |
|----------------------------|
| pip install faster-whisper |

Then replace the entire WhisperSTT class in assistant.py with this:

|                                                                               |
|-------------------------------------------------------------------------------|
| class WhisperSTT:                                                             |
| def \_\_init\_\_(self, model_name="tiny", device="cpu"):                      |
| from faster_whisper import WhisperModel                                       |
| console.print(f"\[cyan\]Loading faster-whisper \[{model_name}\]...\[/cyan\]") |
| self.model = WhisperModel(                                                    |
| model_name,                                                                   |
| device=device,                                                                |
| compute_type="int8", \# 8-bit quantisation — faster on ARM CPU                |
| )                                                                             |
| console.print("\[green\]✓ faster-whisper loaded\[/green\]")                   |
|                                                                               |
| def transcribe(self, audio_path: str, language="en") -\> str:                 |
| segments, \_ = self.model.transcribe(                                         |
| audio_path,                                                                   |
| language=language,                                                            |
| beam_size=1,                                                                  |
| best_of=1,                                                                    |
| temperature=0,                                                                |
| vad_filter=True, \# skips silent parts automatically                          |
| vad_parameters=dict(                                                          |
| min_silence_duration_ms=300,                                                  |
| ),                                                                            |
| )                                                                             |
| return " ".join(s.text.strip() for s in segments)                             |

|                                 |                                                                                    |
|---------------------------------|------------------------------------------------------------------------------------|
| **Setting**                     | **What it does**                                                                   |
| **compute_type="int8"**         | Runs inference in 8-bit integers instead of 32-bit floats — ~4x faster on ARM      |
| **vad_filter=True**             | Built-in voice activity detection — skips silent audio before it reaches the model |
| **min_silence_duration_ms=300** | Treats gaps over 300ms as silence — prevents splitting mid-sentence                |
| **beam_size=1 + temperature=0** | Single pass, no sampling — fastest possible transcription                          |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Verify faster-whisper is installed in the virtual environment</strong></p>
<p>Make sure (voice_env) is shown in your prompt before running pip install faster-whisper. Installing outside the venv means the assistant will not find it when it runs.</p></td>
</tr>
</tbody>
</table>

**Fix 3 — Slow thinking (LLM)**

Pull a smaller model. The 0.5B model fits under 1 GB RAM and responds in 2 to 4 seconds on Radxa:

|                          |
|--------------------------|
| ollama pull qwen2.5:0.5b |

Or if you want slightly better answers, the 1.5B is a good middle ground:

|                          |
|--------------------------|
| ollama pull qwen2.5:1.5b |

Then in assistant.py CONFIG update:

|                                                         |
|---------------------------------------------------------|
| "model": "qwen2.5:0.5b", \# or qwen2.5:1.5b             |
| "num_predict": 80, \# was 256 — shorter answers, faster |

Also reduce the request timeout since responses should now be fast. Find this line in the QwenLLM.chat method:

|                                                          |
|----------------------------------------------------------|
| resp = requests.post(self.url, json=payload, timeout=60) |

Change it to:

|                                                          |
|----------------------------------------------------------|
| resp = requests.post(self.url, json=payload, timeout=30) |

|                  |                |
|------------------|----------------|
| **Model**        | **RAM needed** |
| **qwen2.5:0.5b** | ~0.8 GB        |
| **qwen2.5:1.5b** | ~1.5 GB        |
| **qwen2.5:3b**   | ~4 GB          |
| **qwen2.5:7b**   | ~8 GB          |

**Fix 4 — Robotic voice (TTS)**

The default pyttsx3 uses espeak-ng which sounds very robotic. Replace it with **Piper** — a natural sounding TTS designed specifically for ARM edge devices like the Radxa.

Install Piper and the resampling library:

|                       |
|-----------------------|
| pip install piper-tts |
| pip install scipy     |

Download a voice model:

|                                                                                                                       |
|-----------------------------------------------------------------------------------------------------------------------|
| mkdir -p ~/piper-voices                                                                                               |
| cd ~/piper-voices                                                                                                     |
| wget -c https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx      |
| wget -c https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json |

Verify both files downloaded correctly — the .onnx should be around 61 MB:

|                        |
|------------------------|
| ls -lh ~/piper-voices/ |

Replace the entire TextToSpeech class in assistant.py with this final working version:

|                                                                         |
|-------------------------------------------------------------------------|
| class TextToSpeech:                                                     |
| def \_\_init\_\_(self):                                                 |
| from piper import PiperVoice                                            |
| self.voice = PiperVoice.load(                                           |
| "/home/sagar/piper-voices/en_US-lessac-medium.onnx",                    |
| config_path="/home/sagar/piper-voices/en_US-lessac-medium.onnx.json",   |
| )                                                                       |
|                                                                         |
| def speak(self, text: str):                                             |
| console.print(f"\[green\]🔊 Speaking:\[/green\] {text}")                |
| import numpy as np                                                      |
| from scipy.signal import resample_poly                                  |
| from math import gcd                                                    |
|                                                                         |
| chunks = list(self.voice.synthesize(text))                              |
| if not chunks:                                                          |
| log.warning("Piper returned no audio chunks")                           |
| return                                                                  |
|                                                                         |
| \# Concatenate all sentence chunks into one array                       |
| audio = np.concatenate(\[chunk.audio_float_array for chunk in chunks\]) |
| samplerate = chunks\[0\].sample_rate \# 22050                           |
|                                                                         |
| \# Resample from 22050 to 48000 Hz for Jabra                            |
| target_rate = 48000                                                     |
| if samplerate != target_rate:                                           |
| g = gcd(int(samplerate), target_rate)                                   |
| audio = resample_poly(audio, target_rate // g, int(samplerate) // g)    |
|                                                                         |
| \# Convert mono to stereo (Jabra requires 2 channels)                   |
| stereo = np.column_stack(\[audio, audio\]).astype(np.float32)           |
|                                                                         |
| sd.play(stereo, target_rate, device=0)                                  |
| sd.wait()                                                               |

Update the VoiceAssistant \_\_init\_\_ to remove the old rate and volume arguments:

|                           |
|---------------------------|
| self.tts = TextToSpeech() |

**Issues encountered and how they were fixed**

Getting Piper working on Radxa with a Jabra USB headset required fixing several issues in sequence. Each problem and its fix is documented here so you understand what the final code is doing and why.

|                                        |                                                           |
|----------------------------------------|-----------------------------------------------------------|
| **Issue**                              | **Cause**                                                 |
| **PermissionError on .onnx.json**      | Files downloaded to /root/ but running as sagar           |
| **wave.Error: channels not specified** | wave.open needs channel info set before writing           |
| **GPU device discovery warning**       | ONNX Runtime checks for GPU, finds none on Radxa          |
| **Invalid sample rate -9997**          | Piper outputs 22050 Hz but Jabra only accepts 48000 Hz    |
| **ModuleNotFoundError: scipy**         | scipy installed outside the virtual environment           |
| **Data shape (0,) — no audio**         | synthesize is a generator — not iterated, nothing written |
| **AttributeError: speaker_id**         | Wrong synthesize signature — wav file passed as wrong arg |
| **No sound despite no errors**         | audio_float_array is float64, PortAudio needs float32     |

|                                       |                                                                |
|---------------------------------------|----------------------------------------------------------------|
| **Part of final speak() method**      | **Why it is needed**                                           |
| **list(self.voice.synthesize(text))** | Forces the generator to run and produce all audio chunks       |
| **chunk.audio_float_array**           | The actual audio data — already float32, no wav file needed    |
| **np.concatenate(...)**               | Joins multiple sentence chunks into one continuous audio array |
| **resample_poly(audio, 160, 147)**    | Converts 22050 Hz to 48000 Hz exactly — 22050x160/147 = 48000  |
| **np.column_stack(\[audio, audio\])** | Duplicates mono into stereo — Jabra requires 2 channels        |
| **sd.play(..., device=0)**            | Pins playback to Jabra explicitly so it never routes elsewhere |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Voice model path uses your username</strong></p>
<p>The paths /home/sagar/piper-voices/ in the code above are specific to this setup. If your username is different, replace sagar with your actual Linux username. You can check it by running: whoami</p></td>
</tr>
</tbody>
</table>

**09 View Logs and Troubleshoot**

If something is not working, these commands show you what is happening:

**Live assistant log**

|                                  |
|----------------------------------|
| tail -f /tmp/voice_assistant.log |

**Systemd service log (Radxa only)**

|                                  |
|----------------------------------|
| journalctl -u voice-assistant -f |

**Check if Ollama is running**

|                         |
|-------------------------|
| systemctl status ollama |

**Start Ollama manually if it stopped**

|              |
|--------------|
| ollama serve |

**Test the language model directly**

|                                                 |
|-------------------------------------------------|
| ollama run qwen2.5:7b "Hello, are you working?" |

**List audio playback devices**

|          |
|----------|
| aplay -l |

**List microphone recording devices**

|            |
|------------|
| arecord -l |

|                                        |                                                               |
|----------------------------------------|---------------------------------------------------------------|
| **Problem**                            | **Likely cause and fix**                                      |
| **audio open error: Invalid argument** | No default audio device set — follow section 06 above         |
| **Cannot reach language model**        | Ollama is not running — run: ollama serve                     |
| **No speech detected**                 | Microphone not recognised — check: arecord -l                 |
| **LLM read timed out**                 | Model too large for CPU — switch to qwen2.5:0.5b or 1.5b      |
| **Transcription very slow**            | Switch Whisper to tiny model and set beam_size=1              |
| **Voice sounds robotic**               | Replace pyttsx3 with Piper TTS — see section 07               |
| **Permission denied on setup.sh**      | Forgot chmod — run: chmod +x setup.sh first                   |
| **Package not found errors**           | requirements.txt missing — all 3 files must be in same folder |
| **Very slow first response**           | Normal — the model loads into memory on the first query       |

**10 Voice Assistant Quick Reference**

|                                           |                                                          |
|-------------------------------------------|----------------------------------------------------------|
| **Command**                               | **What it does**                                         |
| **chmod +x setup.sh && ./setup.sh**       | First-time setup — run once only                         |
| **source ~/voice_env/bin/activate**       | Activate Python environment (every new terminal session) |
| **python3 assistant.py**                  | Start the voice assistant                                |
| **ollama pull qwen2.5:0.5b**              | Download fastest small LLM model                         |
| **ollama pull qwen2.5:1.5b**              | Download balanced small LLM model                        |
| **pip install piper-tts**                 | Install natural sounding TTS engine                      |
| **aplay -l**                              | List audio playback devices                              |
| **arecord -l**                            | List microphone recording devices                        |
| **nano ~/.asoundrc**                      | Set default audio card                                   |
| **speaker-test -t wav -c 2 -D hw:1,0**    | Test speaker output on card 1                            |
| **sudo systemctl start voice-assistant**  | Start as a background service (Radxa only)               |
| **sudo systemctl enable voice-assistant** | Auto-start on every boot (Radxa only)                    |
| **sudo systemctl status voice-assistant** | Check if the service is running                          |
| **tail -f /tmp/voice_assistant.log**      | Watch live log output                                    |
| **ollama serve**                          | Start Ollama manually if it stopped                      |

**Wake Word**

Adding Alexa activation to the Voice Assistant

*How to make the assistant sleep until you say Alexa — just like a real smart speaker — using openWakeWord running locally on the Radxa*

A wake word means the assistant stays completely silent and uses almost no CPU until it hears a specific trigger word. Only after hearing that word does it activate, play a beep, and start listening for your actual question. This is exactly how Alexa, Google Home, and Siri work.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>What gets added</strong></p>
<p>openWakeWord — lightweight wake word detection library designed for edge devices</p>
<p>alexa_v0.1.onnx — the Alexa detection model (runs via ONNX Runtime on CPU)</p>
<p>WakeWordDetector class — new class added to assistant.py</p>
<p>Updated run() loop — waits for Alexa before every turn</p></td>
</tr>
</tbody>
</table>

**01 Install openWakeWord**

Install the library into your virtual environment:

|                                 |
|---------------------------------|
| source ~/voice_env/bin/activate |
| pip install openwakeword        |

Check which version installed — the API differs between versions:

|                       |
|-----------------------|
| pip show openwakeword |

This guide is written for version 0.4.0. If you have a different version the Model initialisation arguments may differ.

**02 Download the Alexa Wake Word Model**

Version 0.4.0 requires you to pass the full path to an ONNX model file directly — there are no bundled models. Download the Alexa model manually:

|                                                                                        |
|----------------------------------------------------------------------------------------|
| mkdir -p ~/wake-models                                                                 |
| cd ~/wake-models                                                                       |
| wget https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/alexa_v0.1.onnx |

Verify it downloaded correctly:

|                       |
|-----------------------|
| ls -lh ~/wake-models/ |

Expected output:

|                        |
|------------------------|
| alexa_v0.1.onnx ~1.2MB |

Save as test_wake.py and run with python3 test_wake.py to confirm the model loads:

|                                                                     |
|---------------------------------------------------------------------|
| from openwakeword.model import Model                                |
| m = Model(                                                          |
| wakeword_model_paths=\['/home/sagar/wake-models/alexa_v0.1.onnx'\], |
| vad_threshold=0.0,                                                  |
| )                                                                   |
| print('Loaded:', list(m.models.keys()))                             |

You should see: Loaded: \['alexa_v0.1'\]

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Other available wake words</strong></p>
<p>alexa_v0.1.onnx — say Alexa</p>
<p>hey_jarvis_v0.1.onnx — say Hey Jarvis</p>
<p>hey_mycroft_v0.1.onnx — say Hey Mycroft</p>
<p>ok_nabu_v0.1.onnx — say OK Nabu</p>
<p>All available at the same GitHub release URL — just swap the filename.</p></td>
</tr>
</tbody>
</table>

**03 Add WakeWordDetector to assistant.py**

Add these entries to the CONFIG block:

|                                                                     |
|---------------------------------------------------------------------|
| "wake_word_model": "/home/sagar/wake-models/alexa_v0.1.onnx",       |
| "wake_word_threshold": 0.5, \# 0.0 to 1.0 — higher = less sensitive |

Add this new class to assistant.py above the VoiceAssistant class:

|                                                                                      |
|--------------------------------------------------------------------------------------|
| class WakeWordDetector:                                                              |
| def \_\_init\_\_(self, model_path: str, threshold: float = 0.5):                     |
| from openwakeword.model import Model                                                 |
| console.print("\[cyan\]Loading wake word model (Alexa)...\[/cyan\]")                 |
| self.model = Model(                                                                  |
| wakeword_model_paths=\[model_path\],                                                 |
| vad_threshold=0.0,                                                                   |
| )                                                                                    |
| self.threshold = threshold                                                           |
| self.chunk_size = 1280 \# 80ms at 16000 Hz — required by openWakeWord                |
| console.print("\[green\]✓ Wake word model loaded — say Alexa to activate\[/green\]") |
|                                                                                      |
| def listen_for_wake_word(self):                                                      |
| console.print("\[dim\]Waiting for wake word — say Alexa...\[/dim\]")                 |
| with sd.InputStream(                                                                 |
| samplerate=16000, channels=1, dtype='int16',                                         |
| blocksize=self.chunk_size,                                                           |
| ) as stream:                                                                         |
| \# Drain first 20 chunks to flush audio device buffer                                |
| \# and clear openWakeWord internal sliding window                                    |
| for \_ in range(20):                                                                 |
| stream.read(self.chunk_size)                                                         |
| \# Reset model state after draining                                                  |
| try:                                                                                 |
| self.model.reset()                                                                   |
| except AttributeError:                                                               |
| for key in self.model.prediction_buffer:                                             |
| self.model.prediction_buffer\[key\].clear()                                          |
| console.print("\[dim\]Ready — say Alexa\[/dim\]")                                    |
| while True:                                                                          |
| chunk, \_ = stream.read(self.chunk_size)                                             |
| prediction = self.model.predict(chunk.flatten())                                     |
| score = list(prediction.values())\[0\]                                               |
| if score \>= self.threshold:                                                         |
| console.print(f"\[green\]✓ Alexa detected! (score={score:.2f})\[/green\]")           |
| return                                                                               |

Update VoiceAssistant \_\_init\_\_ to load the detector as the first component:

|                                            |
|--------------------------------------------|
| self.wake = WakeWordDetector(              |
| model_path=CONFIG\['wake_word_model'\],    |
| threshold=CONFIG\['wake_word_threshold'\], |
| )                                          |

Update the run() loop to wait for wake word before each turn and add a pause after detection:

|                                                        |
|--------------------------------------------------------|
| while self.running:                                    |
| try:                                                   |
| \# 1. Wait for wake word                               |
| self.wake.listen_for_wake_word()                       |
|                                                        |
| \# Pause so Alexa sound clears before recording starts |
| time.sleep(0.5)                                        |
|                                                        |
| \# 2. Record question                                  |
| audio_path = self.recorder.record_until_silence()      |
| \# ... rest of loop unchanged                          |

Also update the startup message in run():

|                                                                 |
|-----------------------------------------------------------------|
| self.tts.speak("Voice assistant ready. Say Alexa to activate.") |

**04 Issues Encountered and How They Were Fixed**

Several problems came up when integrating the wake word. Each one and its fix is documented here.

**Issue 1 — Wake word being transcribed as the question**

After Alexa was detected, the recorder started immediately and captured the tail end of the word Alexa — so the LLM received **Alexa.** as the question instead of the actual query.

**Fix:** Add a 0.5 second pause between detection and recording:

|                                                            |
|------------------------------------------------------------|
| self.wake.listen_for_wake_word()                           |
| time.sleep(0.5) \# let Alexa sound finish before mic opens |
| audio_path = self.recorder.record_until_silence()          |

**Issue 2 — False wake word trigger immediately after response**

After the assistant spoke a response, the wake word detector immediately fired again without anyone saying Alexa. This happened because the openWakeWord model carried over audio context from the previous detection in its internal sliding window buffer — when the stream reopened it still contained residual audio that scored above the threshold.

**Fix:** Drain the first 20 audio chunks after opening the stream to flush the device buffer and room echo, then reset the model state:

|                                                               |
|---------------------------------------------------------------|
| with sd.InputStream(...) as stream:                           |
| \# Flush 20 chunks (~1.6s) — clears device buffer + room echo |
| for \_ in range(20):                                          |
| stream.read(self.chunk_size)                                  |
| \# Clear model internal sliding window                        |
| try:                                                          |
| self.model.reset()                                            |
| except AttributeError:                                        |
| for key in self.model.prediction_buffer:                      |
| self.model.prediction_buffer\[key\].clear()                   |

|                                         |                                                |
|-----------------------------------------|------------------------------------------------|
| **Problem**                             | **Root cause**                                 |
| **Alexa transcribed as question**       | Recorder started while Alexa still audible     |
| **Immediate re-trigger after response** | Model buffer retained previous detection audio |
| **False trigger from speaker echo**     | Mic picked up TTS speaker output               |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Why 20 chunks</strong></p>
<p>Each chunk is 1280 samples at 16000 Hz = 80ms. Twenty chunks = 1600ms = 1.6 seconds. This covers: the audio device hardware buffer (~100ms), any room reverberation decay (~300ms), and the full openWakeWord sliding context window (~900ms). Discarding all of this ensures the model starts scoring genuinely fresh audio.</p></td>
</tr>
</tbody>
</table>

**05 Tuning the Wake Word Threshold**

The threshold controls how confident the model must be before triggering. A score of 1.0 means absolute certainty, 0.0 means no detection.

|               |                                       |
|---------------|---------------------------------------|
| **Threshold** | **Behaviour**                         |
| **0.3**       | Very sensitive — triggers easily      |
| **0.5**       | Balanced — good starting point        |
| **0.7**       | Strict — requires clear pronunciation |
| **0.9**       | Very strict — may miss some attempts  |

Change it in CONFIG in assistant.py:

|                                                                            |
|----------------------------------------------------------------------------|
| "wake_word_threshold": 0.5, \# adjust up or down based on your environment |

**06 Final Wake Word Flow**

With wake word fully integrated, the complete conversation loop looks like this:

|                                                               |
|---------------------------------------------------------------|
| Start → speaks: Voice assistant ready. Say Alexa to activate. |
| → drains 20 chunks (~1.6s flush)                              |
| → waiting for Alexa...                                        |
|                                                               |
| You say Alexa                                                 |
| → detected (score=0.93+)                                      |
| → 0.5s pause                                                  |
| → beep (start chime)                                          |
| → Listening...                                                |
|                                                               |
| You ask your question                                         |
| → stop beep                                                   |
| → Transcribing...                                             |
| → Thinking...                                                 |
| → speaks response                                             |
|                                                               |
| → drains 20 chunks (~1.6s flush)                              |
| → waiting for Alexa... ← back to start                        |