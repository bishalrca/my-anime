from bs4 import BeautifulSoup as soup
import requests
import re
from anime import Anime
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}  # for all requests


def sanitize_name(title):
    """Convert title to URL-friendly series name (no episode numbers)."""
    title = re.sub(r'[^a-zA-Z0-9\s\-]', '', title).lower().replace(" ", "-")
    # remove "-episode-xx-english-subbed"
    title = re.sub(r'-episode-\d+-english-subbed', '', title)
    return title



def get_stream_url(anime_name, ep_id):
    anime_name = sanitize_name(anime_name)
    url = f"https://anitaku.io/{anime_name}-episode-{ep_id}-english-subbed/"
    
    data_html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    data_soup = soup(data_html.text,"html.parser")

    iframe = data_soup.find('iframe')
    if not iframe:
        return None, 0
    stream_link = iframe['src']

    episodes = data_soup.find('ul', {'id': 'episode_page'})
    eps = 0
    if episodes:
        ep_links = episodes.find_all('a')
        if ep_links:
            eps = int(ep_links[-1].get('ep_end', len(ep_links)))

    return (stream_link, eps)



def get_search_results(anime_name):
    results = []
    anime_name = anime_name.replace(" ", "+")
    url = f"https://anitaku.io/?s={anime_name}"
    
    data_html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    data_soup = soup(data_html.text, "html.parser")
    
    animelist = data_soup.find_all('article', {'class': 'bs'})
    if not animelist:
        print("❌ No search results found")
        return results
    
    for anime in animelist:
        a_tag = anime.find('a', {'class': 'tip'})
        if not a_tag:
            continue

        title_h2 = a_tag.find('h2')
        title = title_h2.text.strip() if title_h2 else "No title"

        img_tag = a_tag.find('img')
        img_url = img_tag['src'] if img_tag else ""

        results.append(Anime(title, img_url))
    
    return results



def get_home_page():
    results = []
    url = "https://anitaku.io/home/"
    
    data_html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    data_soup = soup(data_html.text, "html.parser")
    
    animelist = data_soup.find_all('article', {'class': 'bs'})
    
    for anime in animelist:
        a_tag = anime.find('a', {'class': 'tip'})
        if not a_tag:
            continue

        title_h2 = a_tag.find('h2')
        title = title_h2.text.strip() if title_h2 else "No title"

        img_tag = a_tag.find('img')
        img_url = img_tag['src'] if img_tag else ""

        results.append(Anime(title, img_url))
    
    return results




from bs4 import BeautifulSoup
import requests

def get_anime_info(name):
    url = f"https://anitaku.io/series/{name}/"
    HEADERS = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    # IMAGE
    img_tag = soup.select_one("div.thumb img[itemprop='image']")
    img_url = img_tag["src"] if img_tag else ""

    # TITLE
    title_tag = soup.select_one("div.infox h1.entry-title[itemprop='name']")
    title = title_tag.text.strip() if title_tag else name

    # GENRE
    genre_tags = soup.select("div.genxed a")
    genre = ", ".join([a.text.strip() for a in genre_tags]) if genre_tags else "Unknown"

    # SYNOPSIS
    synopsis_tag = soup.select_one("div.bixbox.synp div.entry-content")
    synopsis = synopsis_tag.get_text(separator="\n").strip() if synopsis_tag else "No synopsis available."

    # STATUS
    status_tag = None
    for span in soup.select("div.spe span"):
        if "Status:" in span.text:
            status_tag = span
            break
    status = status_tag.text.replace("Status:", "").strip() if status_tag else "Unknown"
    
    # EPISODES & EPISODE LINKS
    episodes = 0
    episode_links = []
    ep_list_items = soup.select("div.eplister ul li")
    episodes = len(ep_list_items)  # total number of episodes
    for li in ep_list_items:
        a_tag = li.select_one("a")
        ep_num_div = li.select_one("div.epl-num")
        if a_tag and ep_num_div:
            try:
                ep_num = int(ep_num_div.text.strip())
                episode_links.append({"num": ep_num, "url": a_tag["href"]})
            except ValueError:
                continue

    return {
        "img_url": img_url,
        "title": title,
        "synopsis": synopsis,
        "genre": genre,
        "status": status,
        "episodes": episodes,
        "episode_links": episode_links
    }




