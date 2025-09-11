from bs4 import BeautifulSoup as soup
import requests
import re
from anime import Anime




def get_stream_url(anime_name, ep_id):
    anime_name = sanitize_name(anime_name)
    print(anime_name)
    url = f"https://www.anitaku.to/{anime_name}-episode-{ep_id}"
    
    data_html = requests.get(url)
    data_soup = soup(data_html.text,"html.parser")

    link = data_soup.find('iframe')
    episodes  = data_soup.find('ul',{'id':'episode_page'})
    eps=episodes.find_all('a')
    eps = int(eps[-1]['ep_end'])
    
    return (link['src'].strip(),eps)
   

def get_search_results(anime_name):
    results = []
    anime_name = anime_name.replace(" ", "%20")
    url = f"https://www.anitaku.to/search.html?keyword={anime_name}"
    
    data_html = requests.get(url)
    data_soup = soup(data_html.text,"html.parser")
    animelist = data_soup.find('ul',{'class':'items'}).find_all('li')
    for anime in animelist:
        text = anime.p.text
        
        
        
       
        image = anime.img['src']
        results.append(Anime(text,image))
    
    return results

def get_home_page():
    results = []
    url = 'https://www.anitaku.to/home.html'
    data_html  = requests.get(url)
    data_soup = soup(data_html.text,"html.parser")
    animelist = data_soup.find('ul',{'class':'items'}).find_all('li')
    for anime in animelist:
        title = anime.p.text
        image_url = anime.img['src']
        episodes = anime.find('p',{'class':'episode'}).text.split(' ')[1]
        
        results.append(Anime(title,image_url,episodes =episodes))

    return results

def get_anime_info(name):
    
    anime_data = {}
    name= name.strip()
    url = f"https://www.anitaku.to/category/{name}"
    print(url)
    data_html = requests.get(url)
    data_soup = soup(data_html.text,"html.parser")

        
    anime_info = data_soup.find('div',{'class':'anime_info_body_bg'})
    anime_data['title'] = anime_info.h1.text
    anime_data['img_url'] = anime_info.img['src']
    anime_info = anime_info.find_all('p')
    anime_data['atype'] = anime_info[1].a['title']
    anime_data['synopsis'] = anime_info[2].text.split(': ')[1]

    genres= anime_info[3].find_all('a')
    genre = " "
    for i in genres:
        genre += i.text
    
    anime_data['genre'] = genre
    anime_data['released'] = anime_info[4].text.split(': ')[1]
    anime_data['status'] = anime_info[5].text.split(':')[1]
    episodes  = data_soup.find('div',{'class':'anime_video_body'})
    eps=episodes.find_all('a')
    anime_data['episodes'] = int(eps[-1]['ep_end'])
    print(anime_data)
    return anime_data

def sanitize_name(title):
        
        title =  re.sub(r'[^a-zA-Z0-9\s\-]', '', title).lower().replace(" ","-")
        print(title)
        return title


