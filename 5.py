import os
import sys
from deep_translator import GoogleTranslator
from tqdm import tqdm
import questionary
import logging
import time

# Configure logging
logging.basicConfig(filename='translation_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def translate_text(text, src='auto', dest='en'):
    translator = GoogleTranslator(source=src, target=dest)
    try:
        parts = text.split('\n')
        translated_text = []
        progress_bar = tqdm(total=len(parts), desc="Translating", unit="line")

        for part in parts:
            if part.strip():
                translated = translator.translate(part)
                translated_text.append(translated)
            else:
                translated_text.append(part)
            progress_bar.update(1)

        progress_bar.close()
        return '\n'.join(translated_text)
    except Exception as e:
        logging.error(f"Translation failed: {e}")
        progress_bar.close()
        return None

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

    is_script = questionary.confirm("Is the file a script that needs to retain formatting?").ask()
    languages = GoogleTranslator.get_supported_languages()
    src_language = questionary.select("Select the source language (auto for automatic detection):", choices=['auto'] + languages).ask()
    dest_language = questionary.select("Select the target language:", choices=languages).ask()

    return file_response, src_language, dest_language, is_script

if __name__ == "__main__":
    input_file_path, src_language, dest_language, is_script = select_file_and_languages()
    if not os.path.exists(input_file_path):
        print("File does not exist. Please check the path and try again.")
        sys.exit(1)

    base, ext = os.path.splitext(input_file_path)
    output_file_path = f"{base}_translated_{dest_language.upper()}{ext}"
    translate_file(input_file_path, output_file_path, src_language, dest_language)
