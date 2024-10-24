from concurrent.futures import ThreadPoolExecutor
import requests
import re
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.traceback import install
import html
import time
import markdownify
install()

CLEANR = re.compile('<.*?>')

def cleanhtml(raw_html):
  cleantext = re.sub(CLEANR, '', raw_html)
  return cleantext

def main():
    start = requests.get('https://www.gesetze-im-internet.de/bgb/')
    # use regex to get all links
    links = re.findall(r'<a.*?href=["\'](.*?)["\']', start.text)
    
    links = list(filter(lambda x: x.startswith('__'), links))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Fortschritt", justify="right"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        TimeRemainingColumn(),
        ) as progress:
        update_task = progress.add_task("Fetching texts", total=len(links))
        with ThreadPoolExecutor(max_workers=1) as pool:
            for link in links:
                pool.submit(process, link, progress, update_task)
                

def process(link, progress, task_id):
    try:
        text = html.unescape(requests.get(f'https://www.gesetze-im-internet.de/bgb/{link}').text)
        paragraph = re.findall(r"<span class=\"jnenbez\">(?:§|&#167;) (\d*?\w?)<\/span>", text)
        titel = re.findall(r"<span class=\"jnentitel\">([\w\W]*?)<\/span>", text)
        gesetz = re.findall(r"<div class=\"jnhtml\">([\w\W]*?)<div id=\"fusszeile\">", text)
        if len(gesetz) == 0:
            progress.console.log(f'No gesetz found in {link}', style='bold red')
            return
        gesetz = gesetz[0]
        gesetz = re.sub('<d[dt][^>]*?>', ' ', gesetz)
        gesetz = re.sub('<\/d[dt][^>]*?>', "\n", gesetz)
        # save to file
        if len(paragraph) == 0:
            progress.console.log(f'No § found in {link}', style='bold red')
            return
        if len(titel) == 0:
            progress.console.log(f'No title found in {link}', style='bold red')
            return
        if gesetz == '':
            progress.console.log(f'No gesetz found in {link}', style='bold red')
            return
        
        # split gesetz at \(\d+\) and add new line before
        gesetz = re.sub(r'\((\d+)\)', '\n\n## Abs. \g<1>\n\n', gesetz)
        
        with open(f'data/{paragraph[0]}.md', 'w') as f:
            f.write(f'# {titel[0]}\n\n')
            f.write(markdownify.markdownify(gesetz))
        progress.console.log(f'Saved [cyan]§{paragraph[0]}[/cyan]', style='bold green')
    except Exception as e:
        progress.console.log(e, style='bold red', log_locals=True)
        pass
    finally:
        progress.advance(task_id)

if __name__ == "__main__":
    main()
