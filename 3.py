import os
import re
import sys
import threading
from queue import Queue, Empty
import click
from googletrans import Translator, LANGUAGES
from tqdm import tqdm

# Set up advanced logging
import logging
logging.basicConfig(filename='translation_log_detailed.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class TranslationManager:
    def __init__(self, src_lang='auto', dest_lang='en', num_threads=5):
        self.src_lang = src_lang
        self.dest_lang = dest_lang
        self.translator = Translator()
        self.queue = Queue()
        self.num_threads = num_threads
        self.lock = threading.Lock()

    def translate_chunk(self, text):
        try:
            translated = self.translator.translate(text, src=self.src_lang, dest=self.dest_lang)
            return translated.text
        except Exception as e:
            logging.error(f"Translation error: {e} - Retrying.")
            return self.translate_chunk(text)  # Retry logic

    def worker(self):
        while True:
            try:
                original, result_list, index = self.queue.get(timeout=3)  # 3 seconds timeout
                translated = self.translate_chunk(original)
                with self.lock:
                    result_list[index] = translated
                self.queue.task_done()
            except Empty:
                return

    def translate_text_concurrently(self, texts):
        result_list = [None] * len(texts)
        for index, text in enumerate(texts):
            self.queue.put((text, result_list, index))

        threads = [threading.Thread(target=self.worker) for _ in range(self.num_threads)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        return ' '.join(result_list)

class FileTranslator:
    def __init__(self, file_path, file_type, src_lang, dest_lang):
        self.file_path = file_path
        self.file_type = file_type
        self.src_lang = src_lang
        self.dest_lang = dest_lang
        self.manager = TranslationManager(src_lang=src_lang, dest_lang=dest_lang)

    def smart_split(self, text, max_chunk_size=500):
        punctuation = '.!?'
        parts = []
        last_cut = 0
        last_punct = 0

        for i, char in enumerate(text):
            if char in punctuation and i - last_cut < max_chunk_size:
                last_punct = i + 1
            elif i - last_cut >= max_chunk_size:
                if last_punct > last_cut:
                    parts.append(text[last_cut:last_punct])
                    last_cut = last_punct
                else:
                    parts.append(text[last_cut:i+1])
                    last_cut = i+1
        if last_cut < len(text):
            parts.append(text[last_cut:])
        return parts

    def translate_script_content(self, content):
        code_pattern = re.compile(r'(\'\'\'[\s\S]*?\'\'\'|"""[\s\S]*?"""|#.*?$|\'[^\'\\]*(?:\\.[^\'\\]*)*\'|"[^"\\]*(?:\\.[^"\\]*)*")', re.MULTILINE)
        parts = code_pattern.split(content)
        parts_types = code_pattern.findall(content)
        translated_parts = self.manager.translate_text_concurrently(parts)
        return ''.join(translated_parts)

    def translate(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        if self.file_type == 'script':
            translated_content = self.translate_script_content(content)
        else:
            parts = self.smart_split(content)
            translated_content = self.manager.translate_text_concurrently(parts)

        output_file_path = f"{os.path.splitext(self.file_path)[0]}_translated.txt"
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(translated_content)
        print(f"Translation completed. The translated file is saved as {output_file_path}")

@click.command()
@click.option('--file-path', prompt='Enter the file path', help='Path to the file to be translated')
@click.option('--file-type', type=click.Choice(['plain', 'script'], case_sensitive=False), prompt=True)
@click.option('--src-lang', default='auto', prompt='Source language (auto for detection)', type=click.Choice(['auto'] + list(LANGUAGES.values()), case_sensitive=False))
@click.option('--dest-lang', prompt='Target language', type=click.Choice(list(LANGUAGES.values()), case_sensitive=False))
def main(file_path, file_type, src_lang, dest_lang):
    if not os.path.isfile(file_path):
        click.echo("File does not exist. Please check the path and try again.")
        return

    translator = FileTranslator(file_path, file_type, src_lang, dest_lang)
    translator.translate()

if __name__ == '__main__':
    main()
