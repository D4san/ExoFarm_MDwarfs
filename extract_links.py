import urllib.request
from bs4 import BeautifulSoup

url = "https://natashabatalha.github.io/PandExo/installation.html"
html = urllib.request.urlopen(url).read()
soup = BeautifulSoup(html, 'html.parser')
for a in soup.find_all('a', href=True):
    if "box.com" in a['href'] or "stsci.edu" in a['href'] or "tar.gz" in a['href']:
        print(a.text.strip(), a['href'])
