import re
from bs4 import BeautifulSoup
import bs4
import requests as req
import lxml
from urllib.parse import urlparse

seen_urls = {}

def scraper(url, resp):
    links = list()
    if url not in seen_urls:
        links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation requred.
    
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
        if (url + tag['href']) in seen_urls:
            print('already seen ' + url + tag['href'])
            continue

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
            test_log.write('\n' + tag['href'])
            if tag['href'] not in seen_urls:
                seen_urls[tag['href']] = 1
                links.append(tag['href'])
            else:
                seen_urls[tag['href']] += 1
                
        elif tag['href'].startswith('/'):
            #Pages beginning with a / or // are paths within the url.
            # I'm not 100% sure what the // means, but / is definitely
            # a child directory of the current directory
            print('---->' + url + tag['href'])
            if(url + tag['href']) not in seen_urls:
                seen_urls[url + tag['href']] = 1
                links.append(url + tag['href'])
                child_log.write('\nOn website: ' + url +' found child page \n\t' + tag['href'])
            else:
                seen_urls[url + tag['href']] += 1
        else:
            # grabs a lot of mailto's and fragments (#) maybe some other unimportant stuff as well
            print('got some trash link: ' + tag['href'])
            trash_log.write('\nFound some garbage (or did I?): ' + tag['href'])
    return links

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
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
        print ("TypeError for ", parsed)
        raise
