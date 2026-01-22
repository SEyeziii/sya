import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

HEADERS = {'User-Agent': 'Mozilla/5.0'}
BASE_URL = 'https://www.vesselfinder.com'


def resolve_vessel_page(start_url):
    try:
        resp = requests.get(start_url, headers=HEADERS, timeout=30)
        html = BeautifulSoup(resp.text, 'html.parser')

        found = [
            (BASE_URL + a['href']) if a['href'].startswith('/') else a['href']
            for a in html.select('a[href*="/vessels/details/"]')
        ]

        if '/vessels/details/' in resp.url:
            return resp.url

        if len(found) == 1:
            return found[0]

        return None
    except Exception:
        return None


def parse_vessel_data(page_url):
    empty = {'Название': 'unknown', 'IMO': 'unknown', 'MMSI': 'unknown', 'Тип': 'unknown'}

    try:
        resp = requests.get(page_url, headers=HEADERS, timeout=30)
        text = resp.text
        soup = BeautifulSoup(text, 'html.parser')

        name_tag = soup.find('h1')
        name = name_tag.get_text(strip=True) if name_tag else 'unknown'

        imo_match = re.search(r'vu_imo=(\d{7})', text)
        mmsi_match = re.search(r'MMSI=(\d{9})', text)

        vessel_type = 'unknown'
        for label in soup.select('td.n3'):
            if 'AIS тип' in label.get_text():
                value = label.find_next_sibling('td')
                if value:
                    vessel_type = value.get_text(strip=True)
                break

        return {
            'Название': name,
            'IMO': imo_match.group(1) if imo_match else 'unknown',
            'MMSI': mmsi_match.group(1) if mmsi_match else 'unknown',
            'Тип': vessel_type
        }

    except Exception:
        return empty


def run():
    source = pd.read_excel('Links.xlsx')
    urls = source.get('Ссылка', []).dropna().tolist()

    collected = []

    total = len(urls)
    for idx, src_url in enumerate(urls, start=1):
        print(f'Обработка {idx} из {total}')

        vessel_page = resolve_vessel_page(src_url)
        if vessel_page:
            collected.append(parse_vessel_data(vessel_page))

    if collected:
        pd.DataFrame(collected).to_excel('result.xlsx', index=False)
        print(f'Готово. Найдено судов: {len(collected)}')


if __name__ == '__main__':
    run()
