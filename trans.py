import os
from googletrans import Translator
import questionary

def translate_text(text, src='auto', dest='en'):
    """Translate text using Google Translate."""
    translator = Translator()
    translated_text = []
    parts = []
    while text:
        if len(text) > 450:
            split_pos = text.rfind('.', 0, 450) + 1 if text.rfind('.', 0, 450) != -1 else text.rfind(' ', 0, 450)
            if split_pos == -1:
                split_pos = 450
            parts.append(text[:split_pos])
            text = text[split_pos:]
        else:
            parts.append(text)
            break

    for part in parts:
        try:
            translated = translator.translate(part, src=src, dest=dest)
            translated_text.append(translated.text)
        except Exception as e:
            print(f"Failed to translate a part: {e}")
            continue

    return ' '.join(translated_text)

def translate_file(input_file_path, output_file_path, src_language='auto'):
    """Read, translate and write the translation to a new file."""
    try:
        with open(input_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        translated_content = translate_text(content, src=src_language)
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(translated_content)
        print(f"Translation complete. Check the translated text at {output_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def select_file():
    """Let user choose a file from the current directory or type a path."""
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    files.append("Enter a different file path manually...")
    response = questionary.select("Choose a file to translate or enter your own:", choices=files).ask()
    if response == "Enter a different file path manually...":
        response = questionary.text("Enter the file path:").ask()
    return response

if __name__ == "__main__":
    input_file_path = select_file()
    if input_file_path and os.path.exists(input_file_path):
        base, ext = os.path.splitext(input_file_path)
        output_file_path = f"{base}EN{ext}"
        translate_file(input_file_path, output_file_path)
    else:
        print("Invalid file path or the file does not exist.")
