from operator import itemgetter
from bs4 import BeautifulSoup
from bs4.element import Comment
import lxml
import urllib.robotparser as RobotParser
from urllib.parse import urljoin
from urllib.parse import urlparse
import re
import requests
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

valid_domain = {'ics.uci.edu': 0, 'cs.uci.edu': 0, 'informatics.uci.edu': 0, 'stat.uci.edu': 0,
                'today.uci.edu/department/information_computer_sciences': 0}

def myfunc1(para, para2, para3, para4, para5, para6):
    para['hello'] = 1
    para2['hello'] = 1
    para3['hello'] = 1
    para4['hello'] = 1
    para5[0] = "hello"
    para6[0] = 1
    #myfunc2(para, para2, para3, para4,para5, para6)
    return

def myfunc2(para, para2, para3, para4, para5, para6):
    para['hello'] +=1
    para2['hello'] += 1
    para3['hello'] += 1
    para4['hello'] += 1
    para5[0] = "helloworld"
    para6[0] += 1
    return

def isAllowed(mainurl, urlinquestion):
    ### Takes the stock website url and another url and checks if the given url is present in the main url's robot.txt file
    ### Adds the prohibited URL to seen URLS dict
    rp = RobotParser.RobotFileParser()
    rp.set_url(mainurl + "/robots.txt")
    rp.read()
    return rp.can_fetch('*', urlinquestion)


def remove_url_fragment(url):
    fragment_index = url.find('#')
    if fragment_index == -1:
        return url
    return url[:fragment_index]


def scraper(url, resp):
    links = list()
    if url not in seen_urls:
        links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    # Implementation requred.
    if str(resp.status) == "404":
        disallowed_urls[url] = 1

    if url in disallowed_urls:
        return list()

    trash_log = open('./trashlinks.txt', 'a')
    repeat_visit_log = open('./repeats.txt', 'a')
    child_log = open('./childpages.txt', 'a')
    test_log = open('./testlog.txt', 'a')

    if resp.raw_response is None:
        return list()
    page_content = resp.raw_response.content
    # The fact the value is bool is just a placeholder for now.
    links = []

    soup = BeautifulSoup(page_content, 'lxml')
    for tag in soup.find_all('a', href=True):
        tag['href'] = remove_url_fragment(tag['href'])
        if not isAllowed(url, url + tag['href']):
            print("disallowed " + url + tag['href'])
            continue
        if (url + tag['href']) in seen_urls:
            print('already seen ' + url + tag['href'])
            continue
        if '#' in tag['href']:
            tag['href'] = remove_url_fragment(tag['href'])
            test_log.write('\nRemoved fragment: ' + tag['href'])
        if tag['href'].startswith('http'):
            if tag['href'] in seen_urls:
                seen_urls[tag['href']] += 1
                repeat_visit_log.write('\nVisited: ' + tag['href'] + ' ' + str(seen_urls[tag['href']]) + ' times.')
                continue
            # gets all the http and https pages
            seen_urls[tag['href']] = 1
            links.append(tag['href'])
        elif tag['href'].startswith('//'):
            tag['href'] = tag['href'][2:]
            # test_log.write('\n' + tag['href'])
            if tag['href'] not in seen_urls:
                seen_urls[tag['href']] = 1
                links.append(tag['href'])
            else:
                seen_urls[tag['href']] += 1
        elif tag['href'].startswith('/'):
            # Pages beginning with a / or // are paths within the url.
            # I'm not 100% sure what the // means, but / is definitely
            # a child directory of the current directory
            print('---->' + url + tag['href'])
            if (url + tag['href']) not in seen_urls:
                seen_urls[url + tag['href']] = 1
                links.append(url + tag['href'])
                child_log.write('\nOn website: ' + url + ' found child page \n\t' + tag['href'])
            else:
                seen_urls[url + tag['href']] += 1
        else:
            # grabs a lot of mailto's and fragments (#) maybe some other unimportant stuff as well
            print('got some trash link: ' + tag['href'])
            trash_log.write('\nFound some garbage (or did I?): ' + tag['href'])
    return links


# Refining this part to ignore the trash links :D
def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        test_log = open('./testlog.txt', 'a')
        curr = str(parsed.netloc)

        # this removes www
        if curr.startswith('www'):
            curr = str(parsed.netloc)[4:]
            test_log.write('\nStarts with www and now equals: ' + curr)

        # if the url we are looking at is in the dict we return True
        if curr in valid_domain:
            test_log.write('\n Got a good one: ' + curr)
            return True
        # Bail out this is for the repeating path problem, fucking trap yo
        if '/community/events/competition' in url:
            return False
        else:
            test_log.write('\n Trash: ' + curr)
            return False

        # Need to check that the url can be crawled (robots.txt)
        # Need to check if the url is within the allowed domains
        # Need to check if the url has been visited before

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print("TypeError for ", parsed)
        raise


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(soup1):
    texts = soup1.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


def computeWordFrequencies(TextFilePath):
    d = {}
    str1 = ""
    with open(TextFilePath) as f:
        for line in f:
            for c in line:
                if (c.isalnum() and c.isascii()) or c == " ":
                    str1 += c
                else:
                    str1 += " "
    for word in str1.split():
        word = word.lower()
        if word in d:
            d[word] += 1
        else:
            d[word] = 1
    return sum(d.values())


# seenUrls = open('./seenurls.txt', 'a')
# highWord = open('./highword.txt', 'a')
# fiftyWords = open('./fiftywords.txt', 'a')
# icsUrls1 = open('./icsurls.txt', 'a')
# repeat_visit_log = open('./repeats.txt', 'a')
# child_log = open('./childpages.txt', 'a')
# test_log = open('./testlog.txt', 'a')
#
# seen_urls = {}
# disallowed_urls = {}
# words = {}
# icsUrls = {}
# highWordUrl = ""
# highWordNum = 0
# stop_words = set(stopwords.words('english'))
#
# urls = ["https://en.wikipedia.org/wiki/Lindell_Wigginton", "https://en.wikipedia.org/wiki/Canyon_Barry", "https://en.wikipedia.org/wiki/Billy_Volek"]
# i = 0
# while True:
#
#     if i > 2:
#         seenUrls.write(str(len(seen_urls)))
#         highWord.write(str(highWordUrl))
#         icsUrls = sorted(icsUrls.items(), key=itemgetter(1), reverse=True)
#         for val in icsUrls:
#             icsUrls1.write(val[0] + ', ' + val[1] + "\n")
#         words = sorted(words.items(), key=itemgetter(1), reverse=True)
#         for i, val in enumerate(words):
#             if i > 49:
#                 break
#             else:
#                 fiftyWords.write(val[0] + "\n")
#         print("done")
#         break
#     url = urls[i]
#     site = requests.get(url)
#     page_content = site.content
#     soup = BeautifulSoup(page_content, 'lxml')
#     if '.ics.uci.edu' in url:
#         if url in icsUrls:
#             icsUrls[url] += 1
#         else:
#             icsUrls[url] = 1
#     tokenizer = RegexpTokenizer(r'\w+')
#     tokens = tokenizer.tokenize(text_from_html(soup))
#     if len(tokens) > highWordNum:
#         highWordUrl = url
#     filtered_sentence = [w for w in tokens if not w in stop_words]
#     for word in filtered_sentence:
#         if word in words:
#             words[word] += 1
#         else:
#             words[word] = 1
#     links = []
#
#     for tag in soup.find_all('a', href=True):
#         tag['href'] = remove_url_fragment(tag['href'])
#         if not isAllowed(url, url + tag['href']):
#             # print("disallowed " + url + tag['href'])
#             continue
#         if (url + tag['href']) in seen_urls:
#             # print('already seen ' + url + tag['href'])
#             continue
#         if '#' in tag['href']:
#             tag['href'] = remove_url_fragment(tag['href'])
#             test_log.write('\nRemoved fragment: ' + tag['href'])
#         if tag['href'].startswith('http'):
#             if tag['href'] in seen_urls:
#                 seen_urls[tag['href']] += 1
#                 repeat_visit_log.write('\nVisited: ' + tag['href'] + ' ' + str(seen_urls[tag['href']]) + ' times.')
#                 continue
#             # gets all the http and https pages
#             seen_urls[tag['href']] = 1
#             links.append(tag['href'])
#         elif tag['href'].startswith('//'):
#             tag['href'] = tag['href'][2:]
#             # test_log.write('\n' + tag['href'])
#             if tag['href'] not in seen_urls:
#                 seen_urls[tag['href']] = 1
#                 links.append(tag['href'])
#             else:
#                 seen_urls[tag['href']] += 1
#         elif tag['href'].startswith('/'):
#             # Pages beginning with a / or // are paths within the url.
#             # I'm not 100% sure what the // means, but / is definitely
#             # a child directory of the current directory
#             # print('---->' + url + tag['href'])
#             if (url + tag['href']) not in seen_urls:
#                 seen_urls[url + tag['href']] = 1
#                 links.append(url + tag['href'])
#                 child_log.write('\nOn website: ' + url + ' found child page \n\t' + tag['href'])
#             else:
#                 seen_urls[url + tag['href']] += 1
#         #else:
#             # grabs a lot of mailto's and fragments (#) maybe some other unimportant stuff as well
#             # print('got some trash link: ' + tag['href'])
#             #trash_log.write('\nFound some garbage (or did I?): ' + tag['href'])
#     i += 1


# with open("LocalTesting/test1.html") as fp:
# soup = BeautifulSoup(fp, features="lxml")
# print(len(re.findall(r'\w+', soup.get_text())))
# site = requests.get("https://en.wikipedia.org/wiki/Lindell_Wigginton")
# url = "https://en.wikipedia.org/wiki/Lindell_Wigginton"
# page_content = site.content
# soup = BeautifulSoup(page_content, 'lxml')
# trash_log = open('./trashlinks.txt', 'a')
# repeat_visit_log = open('./repeats.txt', 'a')
# child_log = open('./childpages.txt', 'a')
# test_log = open('./testlog.txt', 'a')
# length = open('./lengthlog.txt', 'a')
# words = open('./words.txt', 'a')
#
# links = []
# length.write(str(len(re.findall(r'\w+', soup.get_text()))))

# words.write(text_from_html(soup))
# print(computeWordFrequencies('words.txt'))
# for tag in soup.find_all('a', href=True):
#     tag['href'] = remove_url_fragment(tag['href'])
#     if not isAllowed(url, url + tag['href']):
#         # print("disallowed " + url + tag['href'])
#         continue
#     if (url + tag['href']) in seen_urls:
#         # print('already seen ' + url + tag['href'])
#         continue
#     if '#' in tag['href']:
#         tag['href'] = remove_url_fragment(tag['href'])
#         test_log.write('\nRemoved fragment: ' + tag['href'])
#     if tag['href'].startswith('http'):
#         if tag['href'] in seen_urls:
#             seen_urls[tag['href']] += 1
#             repeat_visit_log.write('\nVisited: ' + tag['href'] + ' ' + str(seen_urls[tag['href']]) + ' times.')
#             continue
#         # gets all the http and https pages
#         seen_urls[tag['href']] = 1
#         links.append(tag['href'])
#     elif tag['href'].startswith('//'):
#         tag['href'] = tag['href'][2:]
#         # test_log.write('\n' + tag['href'])
#         if tag['href'] not in seen_urls:
#             seen_urls[tag['href']] = 1
#             links.append(tag['href'])
#         else:
#             seen_urls[tag['href']] += 1
#     elif tag['href'].startswith('/'):
#         # Pages beginning with a / or // are paths within the url.
#         # I'm not 100% sure what the // means, but / is definitely
#         # a child directory of the current directory
#         # print('---->' + url + tag['href'])
#         if (url + tag['href']) not in seen_urls:
#             seen_urls[url + tag['href']] = 1
#             links.append(url + tag['href'])
#             child_log.write('\nOn website: ' + url + ' found child page \n\t' + tag['href'])
#         else:
#             seen_urls[url + tag['href']] += 1
#     else:
#         # grabs a lot of mailto's and fragments (#) maybe some other unimportant stuff as well
#         # print('got some trash link: ' + tag['href'])
#         trash_log.write('\nFound some garbage (or did I?): ' + tag['href'])
# print(links)
# print(disallowed_urls)
# print(seen_urls)
