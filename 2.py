import os
import re
import logging
from googletrans import Translator, LANGUAGES
from tqdm import tqdm
import questionary
from rich.console import Console
from rich.progress import track
import typer

app = typer.Typer()
console = Console()

logging.basicConfig(filename='translation_log_advanced.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def smart_split(text, max_chunk_size=500):
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

def translate_text(text, src='auto', dest='en'):
    translator = Translator()
    parts = smart_split(text)
    translated_text = []
    for part in track(parts, description="Translating..."):
        try:
            translated = translator.translate(part, src=src, dest=dest)
            translated_text.append(translated.text)
        except Exception as e:
            logging.error(f"Failed to translate part: {part}. Error: {e}")
            console.log(f"Skipping a part due to an error: {e}")
    return ' '.join(translated_text)

def translate_script_content(content, src='auto', dest='en'):
    code_pattern = re.compile(r'(\'\'\'[\s\S]*?\'\'\'|"""[\s\S]*?"""|#.*?$|\'[^\'\\]*(?:\\.[^\'\\]*)*\'|"[^"\\]*(?:\\.[^"\\]*)*")', re.MULTILINE)
    parts = code_pattern.split(content)
    parts_types = code_pattern.findall(content)
    translated_content = []
    translator = Translator()
    
    for i, part in enumerate(parts):
        if i % 2 == 0:
            translated_content.append(part)
        else:
            if part.startswith(('#', '"""', "'''")):
                translated_text = translate_text(part, src=src, dest=dest)
                translated_content.append(translated_text)
            else:
                translated_content.append(part)
    return ''.join(translated_content)

@app.command()
def main(file_path: str = typer.Option(..., prompt="Enter the full file path"),
         file_type: str = typer.Option("Plain text", prompt="File type (Plain text / Script)"),
         src_language: str = typer.Option("auto", prompt="Source language (auto for detection)"),
         dest_language: str = typer.Option("en", prompt="Target language")):
    if not os.path.isfile(file_path):
        console.print("[red]File does not exist. Please check the path and try again.[/red]")
        raise typer.Exit()

    src_code = 'auto' if src_language == 'auto' else next(k for k, v in LANGUAGES.items() if v == src_language)
    dest_code = next(k for k, v in LANGUAGES.items() if v == dest_language)

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        if file_type.lower() == 'script':
            translated_content = translate_script_content(content, src=src_code, dest=dest_code)
        else:
            translated_content = translate_text(content, src=src_code, dest=dest_code)

        output_file_path = f"{os.path.splitext(file_path)[0]}_translated.txt"
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(translated_content)

        console.print(f"[green]Translation completed. The translated file is saved as {output_file_path}[/green]")
    except Exception as e:
        console.print(f"[red]An error occurred during the translation process: {e}[/red]")

if __name__ == "__main__":
    app()
