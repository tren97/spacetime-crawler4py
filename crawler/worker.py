from threading import Thread

from utils.download import download
from utils import get_logger
from scraper import scraper
from operator import itemgetter
import time


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        super().__init__(daemon=True)
        
    def run(self):
        uniqueUrls = open('./uniqueurls.txt', 'a')
        highWord = open('./highword.txt', 'a')
        fiftyWords = open('./fiftywords.txt', 'a')

        seen_urls = {}
        disallowed_urls = {}
        words = {}
        highWordUrl = ""
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                uniqueUrls.write(str(len(seen_urls)))
                highWord.write(str(highWordUrl))
                words = sorted(words.items(), key=itemgetter(1))
                for i, val in enumerate(words):
                    if i > 49:
                        break
                    else:
                        fiftyWords.write(val[0] + "\n")
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper(tbd_url, resp, seen_urls, disallowed_urls, words, highWordCount)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
