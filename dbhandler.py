import sqlite3
from anime import Anime

def follow_anime(name,img_url):
    conn = sqlite3.connect('following.db')
    c = conn.cursor
    conn = sqlite3.connect('following.db')
    c = conn.cursor()

        
    c.execute("INSERT INTO  following (anime_name,img_url,watched_ep) VALUES (?,?,?)",(name,img_url,0))
    conn.commit()
    conn.close()

def get_following_list():
    following_list = []
    conn= sqlite3.connect('following.db')
    c= conn.cursor()

    c.execute("SELECT anime_name FROM following")
    data = c.fetchall()
    for anime in data:
        following_list.append(anime[0])
    return following_list
    
    

def unfollow_anime(name):
    conn= sqlite3.connect('following.db')
    c = conn.cursor()
    c.execute("DELETE FROM following WHERE anime_name = ?",(name,))
    conn.commit()
    conn.close()
    return 

def update_watched_ep(anime_name,ep_id):
    try:
        conn = sqlite3.connect("following.db")
        c= conn.cursor()
        c.execute(f"SELECT watched_ep from following  WHERE anime_name = '{anime_name}'")
        cur_ep_id = int(c.fetchone()[0])
        if ep_id < cur_ep_id:
            ep_id = cur_ep_id
        else:
            ep_id = ep_id
        c.execute(f"UPDATE following SET watched_ep = {ep_id} WHERE anime_name = '{anime_name}'")
        conn.commit()
        conn.close()
        return
    except TypeError:
        pass

def get_following_anime():
    following_list = []
    conn= sqlite3.connect("following.db")
    c= conn.cursor()
    c.execute('SELECT * from following')
    results = c.fetchall()
    for result in results:
        following_list.append(Anime(result[0],result[1],result[2]))
       

    return (following_list)


def get_last_watched_ep(anime_name):
    try:
        conn = sqlite3.connect('following.db')
        c = conn.cursor()
        c.execute(f"SELECT watched_ep from following where anime_name = '{anime_name}'")
        result = int(c.fetchone()[0])
        return result
    except TypeError:
        return 0