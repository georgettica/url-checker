#!/usr/bin/env python

import os

import requests
from urlextract import URLExtract

# URLs to skip over
blacklisted = os.getenv("INPUT_BLACKLIST", "").split(",")

files = os.getenv("INPUT_FILES", "README.md").split(",")
repo = os.getenv("GITHUB_REPOSITORY")
if not repo:
    print("repo is required")
    exit(1)
links = []
exit_status = 0


def remove_duplicates(urls):
    return list(set(urls))


for file in files:
    print(f"Collecting URLs from {file}")
    filepath = "https://raw.githubusercontent.com/" + repo + "/master/" + file
    text = requests.get(filepath).text

    extractor = URLExtract()
    file_links = extractor.find_urls(text)

    # Remove mailto links
    links = [url for url in file_links if "mailto://" not in url]
    linksToRequest = []

    # Remove blacklisted links
    for link in links:
        if link in blacklisted:
            print(f"Removed {link}")
        else:
            linksToRequest.append(link)

    print(f"Checking URLs from {file}")

    # Remove Duplicate links
    linksToRequest = remove_duplicates(linksToRequest)

    print(f"Removing duplicate URLs from {file}")

    for url in linksToRequest:
        try:
            request = requests.get(url)
            if request.status_code == 200:
                print(f"✓ 200 {url}")
            elif request.status_code >= 400:
                print(f"✕ {request.status_code} {url}")
                exit_status = 1
            else:
                print(f"⚪ {request.status_code} {url}")

        except Exception as e:
            print(f"✕ ERR {url}")
            print(e)

            # Continue through all URLs but fail test at the end
            exit_status = 1
            continue

    # Newline to separate URLs from different files
    print()

exit(exit_status)
