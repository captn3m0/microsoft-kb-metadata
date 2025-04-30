import json
import re
import datetime
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from urllib.request import HTTPRedirectHandler
from requests import Session

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

SKIPPABLE_REGEX = r"(vulnerabilityresearchadvisories|securitybulletinsummaries|securitybulletins|securityadvisories)\/(199[89]|20[01][0-9]|202[0-4])"
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
        if d>31:
            return None
        date_s = f"{d} {m.group('month').title()} {y}"
        date = datetime.datetime.strptime(date_s, "%d %B %Y").strftime("%Y-%m-%d")
        return {
            "date": date,
            "uuid": slug[-36:],
            "slug": slug,
            "url": f"https://support.microsoft.com/help/{kb_id}"
        }

def get_url_slug(session, kb_id):
    url = f"https://support.microsoft.com/help/{kb_id}"
    response = session.head(url, allow_redirects=False, timeout=5)
    if 'location' in response.headers:
        l = response.headers['location']
        return l.split('/')[-1]

def update_mapping(session, kb_ids):
    print(f"Total Count: {len(kb_ids)}")
    kb = None
    updated = False
    with open('data.json', 'r') as f:
        kb = json.load(f)

    i = 0
    for kb_id in kb_ids:
        i=i+1
        if kb_id not in kb:
            slug = get_url_slug(session, kb_id)
            if slug:
                new_data = parse_redirect(kb_id, slug)
                if new_data:
                    updated = True
                    kb[kb_id] = new_data
                    print(f"Status: {i}/{len(kb_ids)}")

    if updated:
        with open('data.json', 'w') as f:
            f.write(json.dumps(kb, indent=2))

def fetch_kb_mentions(session, url):
    with session.get(url, timeout=10) as response:
        print(url)
        soup = BeautifulSoup(response.text, features="html5lib")
        for a in soup.find('div', class_='content').find_all('a', href=True):
            l = a['href']
            if l.startswith('https://support.microsoft.com/kb/') or l.startswith('https://support.microsoft.com/help/'):
                yield l.split('/')[4]



def skippable(url):
    m = re.search(SKIPPABLE_REGEX, url)
    if m:
        return True
    return False

if __name__ == "__main__":
    kbs = []
    s = Session()
    retries = Retry(
        total=3,
        backoff_factor=0.1,
        status_forcelist=[502, 503, 504],
        allowed_methods={'GET'},
    )
    s.mount('https://', HTTPAdapter(max_retries=retries))
    with open('discovery.txt', 'r') as f:
        for url in f.readlines():
            url = url.strip()
            if skippable(url):
                continue
            for kb_id in fetch_kb_mentions(s, url):
                kbs.append(kb_id)
    update_mapping(s, kbs)