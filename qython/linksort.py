import re
links = open('links.txt','r', encoding='utf-8').read()
out = open('links_sorted.txt','w', encoding='utf-8')
exp = r'(\[url=.*?(article|video|question)/.*?(\d{1,}).*?\](.*?)\[/url\])'

all_links = re.findall(exp, links)
all_links = sorted(all_links, key=lambda k:-int(k[2]))

def filt(key):
    return ''.join(
        [bbcode+'\r\n' for bbcode, type, id, text in all_links if type==key]
    )

questions = filt('question')
articles = filt('article')
videos = filt('video')
out.write('问题：\r\n{}文章：\r\n{}视频：\r\n{}'.format(questions,articles,videos))
