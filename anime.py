import re

class Anime:
    def __init__ (self,title,img_url,watched_ep = None , episodes=None,synopsis = None):
        self.title = title
        self.episodes = episodes
        self.watched_ep = watched_ep
        self.img_url = img_url
        self.synopsis = synopsis

    def sanitize_name(self):
        title =  re.sub(r'[^a-zA-Z0-9\s\n\-]', '', self.title).lower().replace(" ","-")
        return title

    # def set_watched_ep(self):
    #     self.set_watched_ep = 0