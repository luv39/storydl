#! /usr/bin/python
# -*-encoding=utf-8-*-

import os
import shutil
import time
import requests
import re


def getHtmlText(url):
    '''getHtmlText(url)

    get html and return
    '''
    key={'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0'}
    try:
        r = requests.get(url, timeout=3, headers=key)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        text = r.text.encode('utf-8')
        return text
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
        time.sleep(1)
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
        print '没有找到小说名,请确认输入了正确的URL fail'
        return 404
    print storyname[0] + ' start download'
    return storyname[0]

def findHomePage(storyname, text):
    try:
        homepageurl = re.findall('<div id="fmimg"><img alt="" src="(.*?)"', text)[0]
    except:
        return 404
    r = requests.get(homepageurl)
    f = open('%s/OEBPS/cover.jpg'%storyname, 'wb')
    f.write(r.content)
    f.close()

def findMulu(text):
    '''findMulu(url)

    get dir from the html. if get failed, it will return 404
    '''
    if text == 404:
        print '网络错误 fail'
        return 404
    mulu = re.findall('<dd><a href="(.*?)">', text)
    if len(mulu) == 0:
        print '没有找到目录,请确认输入了正确的URL fail'
        return 404
    return mulu

def findTitle(text):
    '''findTitle(text)

    find title in text
    '''
    try:
        title = re.findall('<h1>(.*?)</h1>', text)[0]
    except:
        print "未找到title fail"
        return 404
    return title

def findStory(text):
    '''findStory(text)

    find story in text and return it, if failed, return 404
    '''
    try:
        story = re.findall('<div id="content">(.*?)</div>', text, re.S)[0]
    except:
        print "未找到正文 fail"
        return 404
    story = re.findall('(.*?)<br/>', story)
    return story

def init(storyname):
    isExists = os.path.exists(storyname)

    if not isExists:
        os.makedirs('%s/META-INF'%storyname)
        os.makedirs('%s/OEBPS'%storyname)
        print storyname + ' creat success'
    else:
        print storyname + ' is exists'
        return False

    shutil.copy('mimetype', '%s'%storyname)
    shutil.copy('container.xml', '%s/META-INF'%storyname)
    shutil.copy('stylesheet.css', '%s/OEBPS'%storyname)

def writeFile(filename, line):
    f = open(filename, 'a')
    f.write(line + '\n')
    f.close()

def removeFile(filename):
    if os.path.exists(filename):
        os.remove(filename)

def creatMetadata(storyname):
    writeFile('%s/metadata' % storyname, '''<?xml version='1.0' encoding='utf-8'?>''')
    writeFile('%s/metadata' % storyname, '''<package xmlns="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/" unique-identifier="bookid" version="2.0">''')
    writeFile('%s/metadata' % storyname, '''<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">''')
    writeFile('%s/metadata' % storyname, '<dc:title>' + storyname + '</dc:title>')
    writeFile('%s/metadata' % storyname, '<dc:language>zh-cn</dc:language>')
    writeFile('%s/metadata' % storyname, '</metadata>')

def creatManifestAndSpineAndNavmap(href, id, chapter, title, storyname):
    writeFile('%s/manifest' % storyname, '<item href="' + href + '" id="' + id + '" media-type="application/xhtml+xml"/>' )
    writeFile('%s/spine' % storyname, '<itemref idref="' + id + '"/>')
    writeFile('%s/navmap' % storyname, '<navPoint id="%s" playOrder="%d"><navLabel><text>%s</text></navLabel><content src="%s"/></navPoint>' % (id, chapter, title, href))

def creatContent(storyname):
    f = open('%s/metadata' % storyname,'r')
    metadata = f.readlines()
    f.close()
    for line in metadata:
        writeFile('%s/OEBPS/content.opf'%storyname, line)

    writeFile('%s/OEBPS/content.opf'%storyname, '<manifest>')
    f = open('%s/manifest' % storyname, 'r')
    manifest = f.readlines()
    f.close()
    for line in manifest:
        writeFile('%s/OEBPS/content.opf'%storyname, line)
    writeFile('%s/OEBPS/content.opf'%storyname, '<item href="stylesheet.css" id="css" media-type="text/css"/>')
    writeFile('%s/OEBPS/content.opf'%storyname, '<item href="toc.ncx" media-type="application/x-dtbncx+xml" id="ncx"/>')
    writeFile('%s/OEBPS/content.opf'%storyname, '<item href="cover.jpg" id="cover" media-type="jpeg"/>')
    writeFile('%s/OEBPS/content.opf'%storyname, '</manifest>')

    writeFile('%s/OEBPS/content.opf'%storyname, '<spine toc="ncx">')
    f = open('%s/spine' % storyname, 'r')
    spine = f.readlines()
    for line in spine:
        writeFile('%s/OEBPS/content.opf' % storyname, line)
    writeFile('%s/OEBPS/content.opf'%storyname, '</spine><guide><reference href="cover.jpg" type="cover" title="封面"/></guide></package>')

    removeFile('%s/manifest' % storyname)
    removeFile('%s/metadata' % storyname)
    removeFile('%s/spine' % storyname)

def creatToc(storyname):
    writeFile('%s/OEBPS/toc.ncx' % storyname, "<?xml version='1.0' encoding='utf-8'?>")
    writeFile('%s/OEBPS/toc.ncx' % storyname, '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">')
    writeFile('%s/OEBPS/toc.ncx' % storyname, '<docTitle><text>%s</text></docTitle>' % storyname)
    writeFile('%s/OEBPS/toc.ncx' % storyname, '<navMap>')
    f = open('%s/navmap' % storyname,'r')
    navmap = f.readlines()
    f.close()
    for line in navmap:
        writeFile('%s/OEBPS/toc.ncx' % storyname, line)
    writeFile('%s/OEBPS/toc.ncx' % storyname, '</navMap></ncx>')

    removeFile('%s/navmap' % storyname)

def creatChapter(storyname, href, title, story):
    writeFile('%s/OEBPS/%s'%(storyname, href), '''<?xml version="1.0" encoding="utf-8" standalone="no"?>''')
    writeFile('%s/OEBPS/%s' % (storyname, href), '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">''')
    writeFile('%s/OEBPS/%s' % (storyname, href), '''<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN">''')
    writeFile('%s/OEBPS/%s' % (storyname, href), '''<head>''')
    writeFile('%s/OEBPS/%s' % (storyname, href), '''<title>%s</title>'''%title)
    writeFile('%s/OEBPS/%s' % (storyname, href), '''<link href="stylesheet.css" type="text/css" rel="stylesheet"/><style type="text/css">''')
    writeFile('%s/OEBPS/%s' % (storyname, href), '''@page { margin-bottom: 5.000000pt; margin-top: 5.000000pt; }</style>''')
    writeFile('%s/OEBPS/%s' % (storyname, href), '''</head>''')
    writeFile('%s/OEBPS/%s' % (storyname, href), '''<body>''')
    writeFile('%s/OEBPS/%s' % (storyname, href), '''<h2><span style="border-bottom:1px solid">%s</span></h2>'''%title)
    for line in story:
        writeFile('%s/OEBPS/%s' % (storyname, href), '<p>%s</p>'%line)
    writeFile('%s/OEBPS/%s' % (storyname, href), '<div class="mbppagebreak"></div></body></html>')


def storyDownLoad(url):
    main_text = getText(url)

    storyname = findStoryName(main_text)
    if storyname == 404:
        print 'task ' + url + ' download fail'
        return 404
    init(storyname)
    creatMetadata(storyname)
    homepage = findHomePage(storyname, main_text)
    if homepage == 404:
        print 'homepage cant find fail'
        return 404
    mulu_urls = findMulu(main_text)

    if mulu_urls == 404:
        print storyname + " download fail"
        return 404

    chapter = 1

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

        id = 'chapter' + '%d'%chapter
        href = id + '.xhtml'

        creatManifestAndSpineAndNavmap(href, id, chapter, title, storyname)
        creatChapter(storyname, href, title, story)
        print title + ' pass'

        chapter += 1

    print 'start make epub'
    creatContent(storyname)
    creatToc(storyname)
    print 'epub make success'
    os.chdir('./%s' % storyname)
    os.system('zip -r %s.epub *' % storyname)
    os.system('mv %s.epub ~/Documents' % storyname)
    os.chdir('..')


if __name__ == '__main__':
    url = 'http://www.biquge5200.com/79_79883/'

    storyDownLoad(url)
