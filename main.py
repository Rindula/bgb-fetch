import requests
import re
from rich.progress import Progress
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
    
    with Progress() as progress:
        update = progress.add_task("[green]Downloading...", total=len(links))
        for i, link in enumerate(links):
            process(link, progress)
            progress.update(update, advance=1)
            if i % 20 == 0:
                time.sleep(1)

def process(link, progress):
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
        with open(f'data/{paragraph[0]}.md', 'w') as f:
            f.write(f'# {titel[0]}\n\n')
            f.write(markdownify.markdownify(gesetz))
        progress.console.log(f'Saved [cyan]§{paragraph[0]}[/cyan]', style='bold green')
    except Exception as e:
        progress.console.log(e, style='bold red', log_locals=True)
        pass

if __name__ == "__main__":
    main()
