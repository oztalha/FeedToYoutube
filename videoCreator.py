# -*- coding: utf-8 -*-

from episode import Episode
from PIL import Image, ImageFont, ImageDraw
from hashlib import md5
import moviepy.editor as mpe
import moviepy.config as cf
import requests
import os
import sys
from mutagen import mp3

class VideoCreator:
    @property
    def feed(self):
        return self.feed

    @feed.setter
    def feed(self, value):
        self.feed = value

    @property
    def backgroundImage(self):
        return self.backgroundImage

    @backgroundImage.setter
    def backgroundImage(self, value):
        self.backgroundImage = value

    def run(self, feed):
        if not hasattr(feed, 'getNewEpisodes'):
            return None
        cf.change_settings({"FFMPEG_BINARY": r'C:\Program Files\ImageMagick-7.0.3-Q16-HDRI\ffmpeg.exe'})
        newEpisodes = feed.getNewEpisodes()
        for episode in newEpisodes:
            localMp3 = self.download(episode.link)
            audioClip = mpe.AudioFileClip(localMp3)
            print "duration", audioClip.duration

            print "\t creating image " + episode.title
            self.make_image1(episode)

    def download(self, link):
        # todo check if the file aready exists
        file_name = self.config.temp_path + os.path.basename(link)
        with open(file_name, "wb") as f:
            print "Downloading %s" % file_name
            response = requests.get(link, stream=True)
            total_length = response.headers.get('content-length')

            if total_length is None:  # no content length header
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                    sys.stdout.flush()
        return file_name

    def get_dynamic_font_size(self, text, img, canvas_fraction=0.9):
        font_size = 18  # todo min font size -> config
        font = ImageFont.truetype(self.config.font, font_size)
        while font.getsize(text)[0] < canvas_fraction * img.size[0]:
            if font_size > 90:  # todo max font size ->config
                break
            font_size += 1
            font = ImageFont.truetype(self.config.font, font_size)
        return font

    def make_image1(self, episode=None):
        # load background image
        if hasattr(self.config, "background_image"):
            cnt = 0
            for chapter in episode.chapters:
                img = Image.open(self.config.background_image)
                self.draw_title(episode, img)
                self.draw_chapter(chapter, img)
                img.save('tmp/' + md5(episode.title.encode('utf-8')).hexdigest() + '_' + str(cnt) + '.png')
                cnt += 1
        pass

    def draw_title(self, episode, img):
        if hasattr(self.config, "font"):
            img_fraction_title = 0.8
            font_size = 18  # todo min font size -> config
            text_pos_top = (img.size[1] / 2) - font_size / 2
            text_pos_top -= 100  # todo -> config
            self.draw_dynamic_centered_text(episode.title, img, img_fraction_title, font_size,
                                            text_pos_top=text_pos_top)

    def draw_chapter(self, chapter, img):
        if hasattr(self.config, "font"):
            img_fraction = 0.6  # todo -> config
            font_size = 18  # todo -> config
            text_pos_top = (img.size[1] / 2) - font_size / 2
            text_pos_top -= -200  # todo -> config
            self.draw_dynamic_centered_text(chapter.title, img, img_fraction, font_size, text_pos_top=text_pos_top)

    def draw_dynamic_centered_text(self, text, img, img_fraction=0.9, min_font_size=18, text_pos_top=0):
        if hasattr(self.config, "font"):
            draw = ImageDraw.Draw(img)
            dynamic_font = self.get_dynamic_font_size(text, img, canvas_fraction=img_fraction)
            font_x_pos, font_y_pos = dynamic_font.getsize(text)
            text_pos_left = (img.size[0] / 2) - font_x_pos / 2
            draw.text((text_pos_left, text_pos_top), text, (128, 128, 128), font=dynamic_font)

    def __init__(self, config):
        self.config = config