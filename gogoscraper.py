from bs4 import BeautifulSoup as soup
import requests
import re
from anime import Anime
from requests.adapters import HTTPAdapter, Retry

HEADERS = {"User-Agent": "Mozilla/5.0"}  # default header


def format_ep_num(ep_num):
    """
    Format episode number for URL:
    0.5 -> 0-5
    1.0 -> 1
    """
    try:
        ep_float = float(ep_num)
    except ValueError:
        return str(ep_num)

    if ep_float % 1 == 0:
        return str(int(ep_float))
    else:
        # Convert decimal to hyphenated format for AniTaku
        s = str(ep_float).split('.')
        return f"{s[0]}-{s[1]}"



def sanitize_name(title):
    """Convert title to URL-friendly series name (no episode numbers)."""
    title = re.sub(r'[^a-zA-Z0-9\s\-]', '', title).lower().replace(" ", "-")
    title = re.sub(r'-episode-\d+-english-subbed', '', title)
    return title


def get_stream_url(anime_name, ep_num):
    """Get video iframe URL and total number of episodes (supports fractional episodes)."""
    ep_str = format_ep_num(ep_num)
    anime_url_name = anime_name.lower().replace(" ", "-")
    url = f"https://anitaku.io/{anime_url_name}-episode-{ep_str}-english-subbed/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None, 0

    page_soup = soup(response.text, "html.parser")

    # Video iframe
    video_tag = page_soup.select_one("div.play-video iframe")
    video_url = video_tag['src'] if video_tag else None

    # Count total episodes (supports float numbers)
    ep_links = page_soup.select("div.eplister li div.epl-num")
    ep_nums = []
    for div in ep_links:
        try:
            ep_text = div.text.strip()
            ep_nums.append(float(ep_text))
        except ValueError:
            continue

    total_episodes = max(ep_nums) if ep_nums else 1

    return video_url, total_episodes

def get_search_results(anime_name):
    results = []
    query = anime_name.replace(" ", "+")
    url = f"https://anitaku.io/?s={query}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        return results

    page_soup = soup(response.text, "html.parser")
    animelist = page_soup.find_all('article', {'class': 'bs'})
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

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        return results

    page_soup = soup(response.text, "html.parser")
    animelist = page_soup.find_all('article', {'class': 'bs'})
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


def get_anime_info(name):
    url = f"https://anitaku.io/series/{name}/"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
    except requests.RequestException:
        return {}

    page_soup = soup(r.text, "html.parser")

    # Image
    img_tag = page_soup.select_one("div.thumb img[itemprop='image']")
    img_url = img_tag["src"] if img_tag else ""

    # Title
    title_tag = page_soup.select_one("div.infox h1.entry-title[itemprop='name']")
    title = title_tag.text.strip() if title_tag else name

    # Genre
    genre_tags = page_soup.select("div.genxed a")
    genre = ", ".join([a.text.strip() for a in genre_tags]) if genre_tags else "Unknown"

    # Synopsis
    synopsis_tag = page_soup.select_one("div.bixbox.synp div.entry-content")
    synopsis = synopsis_tag.get_text(separator="\n").strip() if synopsis_tag else "No synopsis available."

    # Status
    status_tag = None
    for span in page_soup.select("div.spe span"):
        if "Status:" in span.text:
            status_tag = span
            break
    status = status_tag.text.replace("Status:", "").strip() if status_tag else "Unknown"

    # Episodes & episode links
    ep_list_items = page_soup.select("div.eplister ul li")
    episode_links = []
    for li in ep_list_items:
        a_tag = li.select_one("a")
        ep_num_div = li.select_one("div.epl-num")
        if a_tag and ep_num_div:
            try:
                ep_num = int(ep_num_div.text.strip())
                episode_links.append({"num": ep_num, "url": a_tag["href"]})
            except ValueError:
                continue
    total_episodes = len(ep_list_items)

    return {
        "img_url": img_url,
        "title": title,
        "synopsis": synopsis,
        "genre": genre,
        "status": status,
        "episodes": total_episodes,
        "episode_links": episode_links
    }

def get_iframe_from_url(episode_url):
    """Get the actual iframe video URL from the episode page."""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(episode_url, headers=headers, timeout=10)
        r.raise_for_status()
    except requests.RequestException:
        return None

    page_soup = soup(r.text, "html.parser")
    iframe_tag = page_soup.select_one("div.player-embed iframe")
    if not iframe_tag:
        return None

    video_url = iframe_tag["src"]
    if video_url.startswith("//"):
        video_url = "https:" + video_url
    return video_url


import requests
from bs4 import BeautifulSoup

def scrape_anime(query):
    url = f"https://anitaku.io/?s={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    results = []

    # anitaku puts search results inside divs with class "bsx"
    for item in soup.select(".bsx"):
        a_tag = item.select_one("a")
        img_tag = item.select_one("img")

        if not a_tag:
            continue

        title = a_tag.get("title") or a_tag.text.strip()
        link = a_tag.get("href")
        img_url = img_tag.get("src") if img_tag else ""

        results.append({
            "title": title,
            "url": link,
            "img_url": img_url,
            "sanitize_name": lambda t=title: sanitize_name(t)
        })

    return results
