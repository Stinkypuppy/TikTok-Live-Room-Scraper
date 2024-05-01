import os
import re
import logging
from googletrans import Translator, LANGUAGES
from rich.console import Console
from rich.progress import Progress
from rich.traceback import install
import typer
import inquirer

# Enhance error visibility
install()

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
            cut_point = last_punct if last_punct > last_cut else i + 1
            parts.append(text[last_cut:cut_point])
            last_cut = cut_point
    if last_cut < len(text):
        parts.append(text[last_cut:])
    return parts

def translate_text(text, src='auto', dest='en'):
    translator = Translator()
    parts = smart_split(text)
    translated_text = []

    with Progress() as progress:
        task = progress.add_task("[cyan]Translating...", total=len(parts))
        for part in parts:
            try:
                translated = translator.translate(part, src=src, dest=dest)
                translated_text.append(translated.text)
                progress.update(task, advance=1)
            except Exception as e:
                logging.error(f"Failed to translate part: {part}. Error: {e}")
                console.print(f"[red]Skipping a part due to an error: {e}[/red]")
    return ' '.join(translated_text)

def choose_file():
    choices = ['Enter file path manually'] + [f for f in os.listdir('.') if os.path.isfile(f)]
    questions = [
        inquirer.List('file',
                      message="Choose a file to translate or enter manually:",
                      choices=choices,
                     ),
    ]
    answer = inquirer.prompt(questions)
    selected_file = answer['file']
    if selected_file == 'Enter file path manually':
        selected_file = typer.prompt("Enter the full file path")
    return selected_file

@app.command()
def main():
    file_path = choose_file()
    if not os.path.isfile(file_path):
        console.print("[red]File does not exist. Please check the path and try again.[/red]")
        raise typer.Exit()

    file_type = typer.prompt("File type (Plain text / Script):", default="Plain text")
    src_language = typer.prompt("Source language (auto for detection):", default="auto")
    dest_language = typer.prompt("Target language:", default="en")

    src_code = 'auto' if src_language == 'auto' else next(k for k, v in LANGUAGES.items() if v == src_language)
    dest_code = next(k for k, v in LANGUAGES.items() if v == dest_language)

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        translated_content = translate_text(content, src=src_code, dest=dest_code)
        output_file_path = f"{os.path.splitext(file_path)[0]}_translated.txt"
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(translated_content)
        console.print(f"[green]Translation completed. The translated file is saved as {output_file_path}[/green]")
    except Exception as e:
        console.print(f"[red]An error occurred during the translation process: {e}[/red]")

if __name__ == "__main__":
    app()
