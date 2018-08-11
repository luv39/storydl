
#-*- coding:utf-8 -*-

import re, requests, time, random, sys, getopt, lxml
from bs4 import BeautifulSoup
from prettytable import PrettyTable, ALL

sys.setrecursionlimit(1000000)  # 设置递归最大深度

help_file = '''
-h, --help: help file
-s, --search: 需要寻找的小说的关键字
-d, --download: 需要下载小说的链接
'''

def getHtmlText(url):
    '''getHtmlText(url)

    get html and return
    '''
    key={'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0'}
    try:
        r = requests.get(url, timeout=30, headers=key)
        r.raise_for_status()
        text = r.text
    except:
        text = 404
    return text

def getText(url, trytime=3):
    '''getText(url, trytime=3)

    if get html failed, try some times(3 default) more
    '''
    for i in range(trytime):
        text = getHtmlText(url)
        if text != 404:
            break

    return text

def search_story(searchkey):
    search_res_list = {'biquge5200': {'search_url': 'https://www.biquge5200.cc/modules/article/search.php?searchkey='}}
    for keys, search_res in search_res_list.items():
        search_url = search_res.get('search_url') + searchkey
        search_result = getText(search_url)
        print(keys)
        search_result = BeautifulSoup(search_result, 'lxml').table
        story_list = search_result.find_all('tr')
        table2 = PrettyTable(header=False, hrules=ALL)
        i = 0
        for story in story_list:
            table_line_soup = story.find_all(['th', 'td'])
            story_table = []
            for table_line in table_line_soup:
                story_table.append(table_line.string[:6])
            if i == 1:
                story_table.append(story.find_all('a')[0].get('href', default='链接'))
            else:
                story_table.append('链接')
            table2.add_row(story_table)
            i = 1
        print(table2)

def find_name_and_mulu(text):
    '''findStoryName(text)

    get story name and return it, if failed, return 404
    '''
    if text == 404:
        print ('网络错误')
        return 404, 404
    try:
        story_name = BeautifulSoup(text, 'lxml').h1.string
        mulu_urls = []
        for sibling in BeautifulSoup(text, 'lxml').dl.div.next_siblings:
            if sibling.name != 'dd':
                continue
            mulu_urls.append(sibling.a.get('href'))
    except:
        return 404, 404
    return story_name, mulu_urls

def find_title_and_story(text):
    '''findTitle(text)

    find title in text
    '''
    try:
        title = BeautifulSoup(text, 'lxml').h1.string
        story = []
        soup = BeautifulSoup(text, 'lxml').body
        div_list = soup.find_all('div')
        for div in div_list:
            if div.get('id') == 'content':
                for hang in div.find_all('p'):
                    story.append(hang.string)
    except:
        print ("未找到title fail")
        return 404, 404
    return title, story

def writeFile(hang, filename):
    '''writeFile(hang, filename)

    creat a file named storyname and write hang in it
    '''

    f = open(filename, 'a')
    try:
        f.write(hang + '\n')
    except:
        pass
    f.close()
    
def storyDownload(url):
    '''storyDownload(url)

    download story and save it
    '''
    try:
        f = open('downloaded_url.tmp', 'r')
    except:
        f = open('downloaded_url.tmp', 'w+')
        f.write('please dont delete this file\n')
    downloaded_url = f.readlines()
    f.close()

    main_text = getText(url)

    story_name, mulu_urls = find_name_and_mulu(main_text)
    if story_name == 404:
        print ('task ' + url + ' download fail')
        return 404
    print(story_name + 'start download')
    for mulu_url in mulu_urls:
        if mulu_url+'\n' in downloaded_url:
            continue
        text = getText(mulu_url)
        if text == 404:
            print (mulu_url + ' connect fail')
            continue

        title, story = find_title_and_story(text)
        if title == 404:
            print (mulu_url + " download fail")
            continue
        writeFile(title, story_name+'.txt')
        for hang in story:
            writeFile(hang, story_name + '.txt')
        writeFile(mulu_url, 'downloaded_url.tmp')
        print(title + ' pass')
    print(story_name + '下载完成')
    try:
        f2 = open('downloaded_url.tmp', 'r')
    except:
        pass
    downloaded_url2s = f2.readlines()
    f2.close()
    for mulu_url in mulu_urls:
        if mulu_url+'\n' in downloaded_url2s:
            downloaded_url2s.remove(mulu_url+'\n')

    f3 = open('downloaded_url.tmp', 'w')
    for downloaded_url2 in downloaded_url2s:
        f3.write(downloaded_url2)
    f3.close()



if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hs:d:', ['help', 'search=', 'download='])
    except getopt.GetoptError:
        print(help_file)
        sys.exit()
    for opt_name, opt_value in opts:
        if opt_name in ('-h', '--help'):
            print(help_file)
            sys.exit()
        if opt_name in ('-s', '--search'):
            search_story(opt_value)
            sys.exit()
        if opt_name in ('-d', '--download'):
            storyDownload(opt_value)
            sys.exit()