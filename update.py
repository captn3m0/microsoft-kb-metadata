import yaml
import json
import re
import datetime
from bs4 import BeautifulSoup
import urllib.request
DATE_REGEX = r'(?:(?P<year>\d{4})-)?(?P<month>january|february|march|april|may|june|july|august|september|october|november|december)-(?P<date>\d+)(?:-(?P<year2>\d{4}))?'

# load data from data.yml
redirect_data = yaml.safe_load(open('data.yml'))

def parse_redirect(slug):
    m = re.search(DATE_REGEX, slug)
    if m == None:
        return None
    else:
        y  = m.group('year') or m.group('year2')
        date_s = f"{m.group('date')} {m.group('month').title()} {y}"
        date = datetime.datetime.strptime(date_s, "%d %B %Y").strftime("%Y-%m-%d")
        return {
            "date": date,
            "uuid": slug[-36:],
            "slug": slug,
            "url": f"https://support.microsoft.com/en-us/topic/{slug}"
        }

def get_url_slug(kb_id):
    return redirect_data[int(kb_id)]['redirect']

def update_mapping(kb_ids):
    kb = None
    updated = False
    with open('data.json', 'r') as f:
        kb = json.load(f)

    with open(kb_json_file, 'r') as f:
        for kb_id in kb_ids:
            if kb_id not in kb:
                
                slug = get_url_slug(kb_id)
                new_data = parse_redirect(slug)
                if new_data:
                    updated = True
                    kb[kb_id] = new_data

    if updated:
        with open('data.json', 'w') as f:
            f.write(json.dumps(kb, indent=2))

def fetch_kb_mentions(url):
    with urllib.request.urlopen(url, data=None, timeout=5) as response:
        soup = BeautifulSoup(response, features="html5lib")
        for a in soup.find('div', class_='content').find_all('a', href=True):
            l = a['href']
            if l.startswith('https://support.microsoft.com/kb/') or l.startswith('https://support.microsoft.com/help/'):
                yield l.split('/')[4]


if __name__ == "__main__":
    kbs = []
    with open('discovery.txt', 'r') as f:
        for url in f.readlines():
            for kb_id in fetch_kb_mentions(url):
                kbs.append(kb_id)
    update_mapping(kbs)