import requests
import re
import tqdm
import html
import time
import markdownify

CLEANR = re.compile('<.*?>')

def cleanhtml(raw_html):
  cleantext = re.sub(CLEANR, '', raw_html)
  return cleantext

def main():
    start = requests.get('https://www.gesetze-im-internet.de/bgb/')
    # use regex to get all links
    links = re.findall(r'<a.*?href=["\'](.*?)["\']', start.text)
    
    links = list(filter(lambda x: x.startswith('__'), links))
    
    for i, link in enumerate(tqdm.tqdm(links)):
        process(link)
        if i % 20 == 0:
            time.sleep(1)

def process(link):
    try:
        text = html.unescape(requests.get(f'https://www.gesetze-im-internet.de/bgb/{link}').text)
        paragraph = re.findall(r"<span class=\"jnenbez\">\§ (\d*?)<\/span>", text)
        titel = re.findall(r"<span class=\"jnentitel\">([\w\s]*?)<\/span>", text)
        gesetz = re.findall(r"<div class=\"jnhtml\">(.*?)<\/div>", text)[0]
        gesetz = re.sub('<d[dt][^>]*?>', ' ', gesetz)
        gesetz = re.sub('<\/d[dt][^>]*?>', "\n", gesetz)
        # save to file
        with open(f'data/{paragraph[0]}.md', 'w') as f:
            f.write(f'# {titel[0]}\n\n')
            f.write(markdownify.markdownify(gesetz))
    except Exception as e:
        pass

if __name__ == "__main__":
    main()
