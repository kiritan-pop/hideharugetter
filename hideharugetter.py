# -*- coding: utf-8 -*-
#
# ex.)
# python hideharugetter.py --hashtag="情報処理部今日のまとめ,野菜観察日記"

from mastodon import Mastodon
import re, os, json
from datetime import datetime
from time import sleep
from pprint  import pprint as pp
import argparse
from bs4 import BeautifulSoup

SAVE_DIR = "results/"

url_ins = open("instance.txt").read()  # https://friends.nico/ とか

mastodon = Mastodon(
    access_token='user.secret',
    api_base_url=url_ins)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hashtag", type=str, default=None)
    args = parser.parse_args()
    return args

#######################################################
# トゥート内容の標準化・クレンジング
def content_cleanser(content):
    tmp = BeautifulSoup(content.replace("<br />", "___R___").strip(), 'lxml')
    hashtags = []
    for x in tmp.find_all("a", rel="tag"):
        hashtags.append(x.span.text)
    for x in tmp.find_all("a"):
        x.extract()

    if tmp.text == None:
        return ""

    rtext = ''
    ps = []
    for p in tmp.find_all("p"):
        ps.append(p.text)
    rtext += '\n'.join(ps)
    rtext = re.sub(r'___R___', r'\n', rtext)

    for hashtag in hashtags:
        rtext += " #" + hashtag

    return rtext

def support_datetime_default(o):
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(repr(o) + " is not JSON serializable")

if __name__ == '__main__':
    args = get_args()
    if args.hashtag:
        tags = args.hashtag.split(",")
        func = mastodon.timeline_hashtag
    else:
        exit()

    for tag in tags:
        save_dir = os.path.join(SAVE_DIR, tag)
        os.makedirs(save_dir, exist_ok=True)

        max_id = None
        
        while True:
            sleep(2)
            statuses = func(tag, max_id=max_id, only_media=False)
            # pp(statuses)
            if len(statuses) == 0:
                break

            for status in statuses:
                max_id=status["id"]

                output_text = content_cleanser(status["content"])

                filename_json = os.path.join(
                    save_dir, str(status["id"])+".json")
                filename_text = os.path.join(
                    save_dir, str(status["id"])+".txt")

                with open(filename_text, "w") as fout:
                    fout.write(output_text)

                with open(filename_json, "w") as fout:
                    json.dump(status, fout, indent=4, ensure_ascii=False,
                              default=support_datetime_default)

                sleep(3)

