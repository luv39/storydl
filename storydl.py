#! /usr/bin/python
#-*- coding:utf-8 -*-

import re
import requests
import codecs
import time
import random

def getHtmlText(url):
    '''getHtmlText(url)

    get html and return
    '''
    kv = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0'}
    try:
        r = requests.get(url, timeout=30, headers=kv)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return 404

def getText(url, trytime=3):
    '''getText(url, trytime=3)

    if get html failed, try some times(3 default) more
    '''
    for i in range(trytime):
        text = getHtmlText(url)
        if text != 404:
            break

    return text

def findStoryName(text):
    '''findStoryName(text)

    get story name and return it, if failed, return 404
    '''
    if text == 404:
        print '网络错误'
        return 404
    storyname = re.findall('<h1>(.*?)</h1>', text)
    if len(storyname) == 0:
        print '没有找到小说名,请确认输入了正确的URL'
        return 404
    print storyname[0] + ' start download'
    return storyname[0]

def findMulu(text):
    '''findMulu(url)

    get dir from the html. if get failed, it will return 404
    '''
    if text == 404:
        print '网络错误'
        return 404
    mulu = re.findall('<dd><a href="(.*?)">', text)
    if len(mulu) == 0:
        print '没有找到目录,请确认输入了正确的URL'
        return 404
    return mulu

def findTitle(text):
    '''findTitle(text)

    find title in text
    '''
    try:
        title = re.findall('<h1>(.*?)</h1>', text)[0]
    except:
        print "未找到title"
        return 404
    return title

def findStory(text):
    '''findStory(text)

    find story in text and return it, if failed, return 404
    '''
    try:
        story = re.findall('<div id="content">(.*?)</div>', text, re.S)[0]
    except:
        print "未找到正文"
        return 404
    story = re.findall('(.*?)<br/>', story)
    return story

def writeFile(hang, storyname):
    '''writeFile(hang, storyname)

    creat a file named storyname and write hang in it
    '''
    storyname = storyname + '.txt'
    f = codecs.open(storyname, "a", "utf-8")
    f.write(hang + "\n")
    f.close()

def storyDownload(url):
    '''storyDownload(url)

    download story and save it
    '''
    main_text = getText(url)

    storyname = findStoryName(main_text)
    if storyname == 404:
        print 'task ' + url + ' download fail'
        return 404

    mulu_urls = findMulu(main_text)

    if mulu_urls == 404:
        print storyname + " download fail"
        return 404

    for mulu_url in mulu_urls:
        text = getText(mulu_url)
        if text == 404:
            print mulu_url + ' connect fail'
            continue

        title = findTitle(text)
        if title == 404:
            print mulu_url + " download fail"
            continue
        story = findStory(text)
        if story == 404:
            print mulu_url + " download fail"
            continue
        writeFile(title, storyname)
        for hang in story:
            writeFile(hang, storyname)
        print title + ' pass'
        timedelay = random.randint(1, 3)
        time.sleep(timedelay)


if __name__ == '__main__':
    f = open('storydl.config', 'r')
    urls = f.readlines()
    f.close()

    for url in urls:
        mark = storyDownload(url)
        if mark == 404:
            continue


