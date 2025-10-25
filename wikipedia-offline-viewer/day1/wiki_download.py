# my first python progarm!
# download wikipedia page

import urllib.request

# i found this on stack overflow - downloads webpage
url = 'https://en.wikipedia.org/wiki/Python_(programming_language)'
response = urllib.request.urlopen(url)
webContent = response.read()

# save to file
f = open('wikipedia.html', 'w')
f.write(webContent)
f.close()

print('done!')
