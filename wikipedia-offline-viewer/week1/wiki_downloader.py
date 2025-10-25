"""
Wikipedia Page Downloader
Downloads a wikipedia page and saves it to a file
"""

import urllib.request

def download_page(url, filename):
    # download the page
    response = urllib.request.urlopen(url)
    content = response.read()

    # save it to a file
    with open(filename, 'wb') as file:
        file.write(content)

    print(f"Page saved to {filename}")

# main program
print("Wikipedia Page Downloader")
print("=" * 30)

# get url from user
page_url = input("Enter Wikipedia URL: ")

# get filename
output_file = input("Enter output filename (default: wiki_page.html): ")
if output_file == "":
    output_file = "wiki_page.html"

# download the page
try:
    download_page(page_url, output_file)
    print("Success!")
except:
    print("Error downloading page. Make sure the URL is correct.")
