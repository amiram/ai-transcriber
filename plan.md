Purpose:
Transcriber will use whisper model locally to transcribe audio files.
The transcribed text will be saved in a text file with the same name as the audio file by default.

Program will have a UI but will also support command line arguments for batch processing.
Program will have a windows installer and a portable version.

UI:
text box for audio file path (with browse button)
text box for output file path (with browse button).
When selecting an audio file and the output path is empty, it will automatically fill with the same name as the audio file but with .txt extension.
dropdown to select whisper model (tiny, base, small, medium, large). last used model will be remembered and selected by default.
dropdown to select language. last used language will be remembered and selected by default. Show all languages supported by whisper.
checkbox to enable GPU acceleration (if available). default checked. last used setting will be remembered.
start transcription button.
stop transcription button (if user wants to cancel an ongoing transcription).
progress bar to show transcription progress
log area to show status messages and errors
warn the user if the output file already exists and ask for confirmation to overwrite, or save with a suffix like (1).

publish on github with a detailed README including installation instructions, usage guide, and troubleshooting tips.

Installer will add a context menu entry for audio files to transcribe directly from the file explorer, using the recently settings for model, language, and GPU acceleration.

Add a github action to automatically build and release new versions when changes are pushed to the main branch.

Add a file menu with open and exit.

Add a command line switch --help to show usage instructions in the terminal.
Last param to the command line is the file name, one or more.
Add help menu with links to documentation and support, to the github repository, and to report issues.

I added 3 files to the repository to be the base for the project.
- `transcriber.py`: main program file that will contain the logic for transcribing audio files using the whisper model.
- transcribe_audio.bat: a batch script to run the transcriber from the command line for batch processing.
- add_transcribe_menu_fixed.reg: a registry file to add a context menu entry for audio files in Windows Explorer to transcribe directly from the file explorer.
You don't have to use them as is, they are just base.

UI element should support english and hebrew according to the system language.
