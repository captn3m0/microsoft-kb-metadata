import yaml
import json
import re
import datetime
from bs4 import BeautifulSoup
from urllib import request
import urllib.error

class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None



DATE_REGEX = r'(?:(?P<year>\d{4})-)?(?P<month>january|february|march|april|may|june|july|august|september|october|november|december)-(?P<date>\d+)(?:-(?P<year2>\d{4})-)?'

def parse_redirect(kb_id, slug):
    m = re.search(DATE_REGEX, slug)
    if m == None:
        return None
    else:
        y  = m.group('year') or m.group('year2')
        d = int(m.group('date'))
        if y == None:
            # if date actually contains the year
            # set date to 1, and set year to date
            if d>1900 and d<2030:
                y = d
                d = 1
            else:
                return None
        if d>30:
            return None
        date_s = f"{d} {m.group('month').title()} {y}"
        date = datetime.datetime.strptime(date_s, "%d %B %Y").strftime("%Y-%m-%d")
        return {
            "date": date,
            "uuid": slug[-36:],
            "slug": slug,
            "url": f"https://support.microsoft.com/help/{kb_id}"
        }

def get_url_slug(kb_id):
    request.install_opener(request.build_opener(NoRedirect))
    url = f"https://support.microsoft.com/help/{kb_id}"
    r = urllib.request.Request(url, method="HEAD")
    try:
        response = urllib.request.urlopen(r, data=None, timeout=5)
    except urllib.error.HTTPError as response:
        if 'location' in response.headers:
            l = response.headers['location']
            print(l)
            return l.split('/')[-1]
        else:
            return None
    return None

def update_mapping(kb_ids):
    print(f"Total Count: {len(kb_ids)}")
    kb = None
    updated = False
    with open('data.json', 'r') as f:
        kb = json.load(f)

    i = 0
    for kb_id in kb_ids:
        i=i+1
        if kb_id not in kb:
            print(kb_id)
            slug = get_url_slug(kb_id)
            if slug:
                print(slug)
                new_data = parse_redirect(kb_id, slug)
                print(new_data)
                if new_data:
                    updated = True
                    kb[kb_id] = new_data
                    print(f"Status: {i}/{len(kb_ids)}")
            else:
                print("no slug")

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