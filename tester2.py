import testLocal

seen_urls = {}
disallowed_urls = {}
words = {}
icsUrls = {}
highWordUrl = [0]*1
highWordNum = [0]*1

testLocal.myfunc1(seen_urls, disallowed_urls, words, icsUrls, highWordUrl, highWordNum)

testLocal.myfunc2(seen_urls, disallowed_urls, words, icsUrls, highWordUrl, highWordNum)

print(seen_urls)
print(disallowed_urls)
print(words)
print(icsUrls)
print(highWordUrl)
print(highWordNum)

