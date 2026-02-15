import whisper
import sys
import os

# Get file path from command line argument
if len(sys.argv) < 2:
    print("Usage: python transcribe_hebrew_v4.py <audio_file_path>")
    sys.exit(1)

audio_file = sys.argv[1]

# Ask user for model choice
print("\n" + "="*60)
print("Choose Whisper model:")
print("="*60)
print("1. Large   (Best quality, slowest)")
print("2. Medium  (High quality, slower)")
print("3. Small   (Balanced - recommended)")
print("4. Base    (Fast, decent quality)")
print("5. Tiny    (Fastest, least accurate)")
print("="*60)

while True:
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        model_name = "large"
        break
    elif choice == "2":
        model_name = "medium"
        break
    elif choice == "3":
        model_name = "small"
        break
    elif choice == "4":
        model_name = "base"
        break
    elif choice == "5":
        model_name = "tiny"
        break
    else:
        print("Invalid choice. Please enter a number between 1-5.")

print(f"\nLoading {model_name} model...")
model = whisper.load_model(model_name)

print("Starting transcription...")
# Get detailed segments for paragraph formatting
result = model.transcribe(audio_file, language="he", fp16=False, verbose=False)

print("\n" + "="*60)
print(f"Transcription (Model: {model_name}):")
print("="*60)

# Format with paragraphs - split by segments
segments = result.get("segments", [])
paragraphs = []
current_paragraph = []

for i, segment in enumerate(segments):
    text = segment["text"].strip()
    current_paragraph.append(text)
    
    # Create new paragraph every 3-4 segments or at natural pauses
    if len(current_paragraph) >= 3 or (i < len(segments) - 1 and segments[i+1]["start"] - segment["end"] > 2.0):
        paragraph_text = " ".join(current_paragraph)
        paragraphs.append(paragraph_text)
        current_paragraph = []

# Add any remaining text
if current_paragraph:
    paragraphs.append(" ".join(current_paragraph))

# Print formatted text
formatted_text = "\n\n".join(paragraphs)
print(formatted_text)
print("="*60)

# Save to file - same directory as audio file
audio_dir = os.path.dirname(audio_file)
audio_name = os.path.splitext(os.path.basename(audio_file))[0]
output_file = os.path.join(audio_dir, f"{audio_name}_transcription_{model_name}.txt")

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"Model: {model_name}\n")
    f.write("="*60 + "\n\n")
    f.write(formatted_text)
    
print(f"\nTranscription saved to: {output_file}")
