from flask import Flask, render_template, request, redirect, url_for
from gogoscraper import (get_anime_info, get_stream_url, sanitize_name, 
                         get_search_results, get_home_page)
from dbhandler import (follow_anime, unfollow_anime, get_following_list, 
                      get_last_watched_ep, update_watched_ep)
import re

from flask import Flask , render_template ,redirect,request , url_for,abort, session
import sqlite3
from gogoscraper import *
from dbhandler import *


app = Flask(__name__)

# Home/Index route
@app.route('/')
@app.route('/index')
def index():
    # Get anime from home page
    season_anime = get_home_page()
    following_list = get_following_list()
    
    context = {
        'season': season_anime,
        'following_list': following_list
    }
    
    return render_template('index.html', context=context)

# Search route
@app.route('/search')
def search():
    query = request.args.get('query', '')
    if not query:
        return redirect(url_for('index'))
    
    search_results = get_search_results(query)
    following_list = get_following_list()
    
    context = {
        'results': search_results,
        'query': query,
        'following_list': following_list
    }
    
    return render_template('search_results.html', context=context)

# Anime info route
@app.route('/info/<name>')
def info(name):
    # Get anime info using the gogoscrapers function
    sanitized_name = sanitize_name(name)
    anime_info = get_anime_info(sanitized_name)
    
    # Get following list to check if anime is followed
    following_list = get_following_list()
    
    # Get last watched episode if anime is being followed
    last_watched_ep = get_last_watched_ep(name) if name in following_list else 0
    
    # Add the sanitized name to context for video URL generation
    context = anime_info.copy()
    context['anime_name'] = sanitized_name  # This is the key fix
    context['last_watched_ep'] = last_watched_ep
    context['original_name'] = name  # Keep original name for follow/unfollow
    
    return render_template('anime_info.html', 
                         context=context, 
                         following_list=following_list)


def get_stream_url(episode_url, ep_num=None):
    """Scrape the iframe URL from a full episode page."""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(episode_url, headers=headers, timeout=10)
        r.raise_for_status()
    except requests.RequestException:
        return None, 0

    page_soup = soup(r.text, "html.parser")

    # Correct selector for the actual embedded video iframe
    iframe_tag = page_soup.select_one("div.player-embed iframe")
    if not iframe_tag:
        return None, 0

    # Make the URL absolute if it starts with //
    video_url = iframe_tag["src"]
    if video_url.startswith("//"):
        video_url = "https:" + video_url

    # You can optionally count total episodes from the page or set as 1
    total_eps = 1

    return video_url, total_eps



# Video player route
@app.route("/video/<string:anime_name>/<ep_num>")
def video(anime_name, ep_num):
    from gogoscraper import get_anime_info, get_iframe_from_url
    from dbhandler import get_last_watched_ep, update_watched_ep

    # Normalize episode number
    ep_num_clean = float(ep_num.replace("-", "."))

    # Get anime info
    anime_info = get_anime_info(anime_name)
    episode_links = anime_info.get("episode_links", [])

    if not episode_links:
        return f"No episodes found for {anime_name}", 404

    # Count total episodes
    total_eps = len(episode_links)

    # Find the real episode URL
    real_url = next(
        (ep["url"] for ep in episode_links if str(ep["num"]) == str(int(ep_num_clean))),
        None
    )
    print("DEBUG: Episode URL =", real_url)

    if not real_url:
        return f"Episode {ep_num_clean} not found for {anime_name}", 404

    # Get actual iframe
    video_url = get_iframe_from_url(real_url)
    if not video_url:
        return f"Video not found for {anime_name} episode {ep_num_clean}", 404

    # Update watched episode
    update_watched_ep(anime_name, int(ep_num_clean))

    # Prepare context
    context = {
        "anime_name": anime_name,
        "cur_ep_id": int(ep_num_clean),
        "video_feed": video_url,
        "episodes": total_eps,
        "episode_links": episode_links,
        "last_watched_ep": get_last_watched_ep(anime_name),
        "title": anime_info.get("title", anime_name)
    }

    return render_template("video_player.html", context=context)


# Follow anime route
@app.route('/follow/<name>')
def follow(name):
    # You might want to get the image URL as well
    # For now, using a placeholder
    sanitized_name = sanitize_name(name)
    anime_info = get_anime_info(sanitized_name)
    img_url = anime_info.get('img_url', '')
    
    follow_anime(name, img_url)
    
    # Redirect back to the previous page or anime info
    return redirect(request.referrer or url_for('info', name=name))

# Unfollow anime route
@app.route('/unfollow/<name>')
def unfollow(name):
    unfollow_anime(name)
    
    # Redirect back to the previous page or anime info
    return redirect(request.referrer or url_for('info', name=name))

# Following list route (optional - if you want a dedicated following page)
@app.route('/following')
def following():
    from dbhandler import get_following_anime
    following_anime = get_following_anime()
    
    context = {
        'following': following_anime
    }
    
    return render_template('following.html', context=context)

# 404 error handler
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# 500 error handler
@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)