from threading import Thread

from utils.download import download
from utils import get_logger
from scraper import scraper
from scraper import is_valid
from operator import itemgetter
import time


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        super().__init__(daemon=True)
        
    def run(self):
        seenUrls = open('./seenurls.txt', 'a')
        highWord = open('./highword.txt', 'a')
        fiftyWords = open('./fiftywords.txt', 'a')
        icsUrlsFile = open('./icsurls.txt', 'a')

        seen_urls = {}
        disallowed_urls = {}
        words = {}
        icsUrls = {}
        highWordUrl = [0]*1
        highWordNum = [0]*1

        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                seenUrls.write(str(len(seen_urls)))
                highWord.write(str(highWordUrl[0]) + '\n')
                highWord.write(str(highWordNum[0]))
                icsUrls = sorted(icsUrls.items(), key=itemgetter(1), reverse=True)
                for val in icsUrls:
                    icsUrlsFile.write(str(val[0]) + ', ' + str(val[1]) + "\n")
                words = sorted(words.items(), key=itemgetter(1), reverse=True)
                for i, val in enumerate(words):
                    if i > 49:
                        break
                    else:
                        fiftyWords.write(str(val[0]) + "\n")
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper(tbd_url, resp, seen_urls, disallowed_urls, words, icsUrls, highWordUrl, highWordNum)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)

