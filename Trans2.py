import os
import sys
import time
import logging
from googletrans import Translator, LANGUAGES
from tqdm import tqdm
import questionary

# Configure logging
logging.basicConfig(filename='translation_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def translate_text(text, src='auto', dest='en'):
    translator = Translator()
    translated_text = []
    parts = []
    progress_bar = tqdm(total=len(text), desc="Translating", unit="char")

    while text:
        if len(text) > 450:
            split_pos = text.rfind('.', 0, 450) + 1 or text.rfind(' ', 0, 450)
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
            progress_bar.update(len(part))
        except Exception as e:
            logging.error(f"Translation failed for a part: {e}")
            continue

    progress_bar.close()
    return ' '.join(translated_text)

def translate_file(input_file_path, output_file_path, src_language='auto', dest_language='en'):
    try:
        start_time = time.time()
        with open(input_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        translated_content = translate_text(content, src=src_language, dest=dest_language)
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(translated_content)
        total_time = time.time() - start_time
        logging.info(f"Translation complete: {output_file_path} in {total_time:.2f}s")
        print(f"Translation complete. Output file created: {output_file_path}")
        print(f"Translation took {total_time:.2f} seconds.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")

def select_file_and_languages():
    path = os.getcwd()
    files = [f for f in os.listdir(path) if os.path.isfile(f)]
    files.append('Enter file path manually...')
    file_response = questionary.select("Choose a file to translate or manually enter a file path:", choices=files).ask()

    if file_response == 'Enter file path manually...':
        file_response = questionary.text("Enter the full file path:").ask()

    # Language selection
    languages = list(LANGUAGES.values())
    src_language = questionary.select("Select the source language (auto for automatic detection):", choices=['auto'] + languages).ask()
    dest_language = questionary.select("Select the target language:", choices=languages).ask()

    src_code = next(key for key, value in LANGUAGES.items() if value == src_language) if src_language != 'auto' else 'auto'
    dest_code = next(key for key, value in LANGUAGES.items() if value == dest_language)

    return file_response, src_code, dest_code

if __name__ == "__main__":
    input_file_path, src_language, dest_language = select_file_and_languages()

    if not os.path.exists(input_file_path):
        print("File does not exist. Please check the path and try again.")
        sys.exit(1)

    base, ext = os.path.splitext(input_file_path)
    output_file_path = f"{base}_translated_{dest_language.upper()}{ext}"
    translate_file(input_file_path, output_file_path, src_language, dest_language)
