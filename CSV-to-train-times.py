"""
CSV to trian times.

This module houses the main function for excecuting a search for train times.
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import csv
import urllib.parse
from datetime import timedelta
from typing import Generator


def read_csv(path: str) -> Generator[list[str], None, None]:
    """Return a generator to get rows from a CSV."""
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header row
        for row in reader:
            yield row


def make_dicts(csv_data: Generator[list[str], None, None]) -> list[dict]:
    """Take in CSV data and return a list of dicts."""
    rows = list(csv_data)
    teachers = [row for row in rows if "Teacher" in row[0]]
    locations = [row for row in rows if "School" in row[0]]
    pairs = [(x[1], x[2], y[1], y[2]) for x in teachers for y in locations]
    dict_list = []
    for pair in list(pairs):
        data_dict = {}

        key = 'Teacher'
        value = [pair[0], pair[1]]
        data_dict[key] = value

        key = 'Location'
        value = [pair[2], pair[3]]
        data_dict[key] = value

        dict_list.append(data_dict)

    return dict_list


def url_from_dict(dict: dict) -> dict:
    """URL builder."""
    start = dict['Teacher'][1]
    end = dict['Location'][1]
    start_encoded = urllib.parse.quote(start)  # encode
    end_encoded = urllib.parse.quote(end)  # encode
    head = 'https://transit.yahoo.co.jp/search/result?from='
    mid = '&flatlon=&to='
    tail = '&viacode=&viacode=&viacode=&shin=&ex=&hb=&al=&lb=&sr=' \
        '&type=1&ws=3&s=&ei=&fl=1&tl=3&expkind=1&ticket=ic&mtf=1&userpass=0' \
        '&detour_id=&fromgid=&togid=&kw='
    url = head + start_encoded + mid + end_encoded + tail + end_encoded
    return {"url": url, "dict": dict}


def parse_duration_str(duration_str: str) -> timedelta:
    """Take times from Yahoo and return python time delta."""
    try:
        hours = 0
        minutes = 0
        if '時間' in duration_str:
            hours = int(duration_str.split('時間')[0].strip())
            minutes = int(duration_str.split('時間')[1].split('分')[0].strip())
        else:
            minutes = int(duration_str.split('分')[0].strip())
        return timedelta(hours=hours, minutes=minutes)
    except (ValueError, IndexError):
        return None


async def download_page(url_dict: dict) -> dict:
    """Get time from Yahoo trains."""
    await asyncio.sleep(1)  # rate limit to 1 sec
    url = url_dict["url"]
    input_dict = url_dict["dict"]
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                time = soup.select("li.time")
                arrive = time[2].select_one('span.small').text.strip()
                duration_str = time[1].select_one('span.small').text.strip()
                duration = parse_duration_str(duration_str)
                input_dict["arrive_time"] = arrive
                input_dict["duration"] = duration
                return input_dict
        except Exception as e:
            return (f"Error occurred while downloading {url}: {e}")


async def download_pages(urls: list[dict]) -> list[dict]:
    """Asycronously retrive titles from pages returned from a list of URLS."""
    tasks = [asyncio.create_task(download_page(url)) for url in urls]
    pages = await asyncio.gather(*tasks)
    return pages


async def a_main(dicts: list[dict]) -> list[dict]:
    """Run a bunch of get requests."""
    urls = [url_from_dict(link) for link in dicts]
    pages = await download_pages(urls)
    return pages


def write_duration_csv(data: list[dict]) -> None:
    """Write a csv file to disk from data."""
    teachers = list(set([d['Teacher'][0] for d in data]))
    locations = list(set([d['Location'][0] for d in data]))

    header = ['Teacher'] + locations

    durations = {t: {loc: '' for loc in locations} for t in teachers}

    for d in data:
        teacher = d['Teacher'][0]
        location = d['Location'][0]
        duration = str(d['duration'])
        durations[teacher][location] = duration

    with open('durations.csv', mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for teacher in teachers:
            row = [teacher] + [durations[teacher][loc] for loc in locations]
            writer.writerow(row)


if __name__ == "__main__":
    csv_generator = read_csv('~/CSV-to-train-times/test.csv')
    dict_list = make_dicts(csv_generator)
    pages = asyncio.run(a_main(dict_list))
    write_duration_csv(pages)
    print("Finished")
