import re
from bs4 import BeautifulSoup
import bs4
import requests as req
import lxml
from urllib.parse import urlparse

def extract_links(page_content):
    links = []
    str_http = "href=http"
    str_https = "href=https"

    soup = BeautifulSoup(page_content, 'lxml')
    for tag in soup.find_all('a', href=True):
        if tag['href'].startswith('http'):
            links.append(tag['href'])
        elif tag['href'].startswith('/'):
            print('starting with a \, needa fix this up.')
        else:
            print('got some trash link: ' + tag['href'])
    return links

def scraper(url, resp):
    links = extract_next_links(url, resp)
    page_links = extract_links(resp.raw_response.content)
    print(*page_links, sep = "\n")
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation requred.
    return list()

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
