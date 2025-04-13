import requests
import xml.etree.ElementTree as ET
from xml.dom import minidom

# === CONFIG ===
USERNAME = 'jnomin'  # Replace with your GitHub username
HEADERS = {'Accept': 'application/vnd.github+json'}
BASE_URL = f'https://api.github.com/users/{USERNAME}/repos'

# === OUTPUT XML ROOT ===
root = ET.Element('repositories')

# === Get Repos ===
repos_response = requests.get(BASE_URL, headers=HEADERS)
if repos_response.status_code != 200:
    print(f"Error fetching repositories: {repos_response.status_code}")
    exit(1)

repos = repos_response.json()

for repo in repos:
    repo_name = repo['name']
    repo_url = repo['html_url']
    about = repo['description'] if repo['description'] else repo_name
    last_updated = repo['updated_at']
    commits_url = repo['commits_url'].replace('{/sha}', '')
    languages_url = repo['languages_url']

    # Get Languages
    lang_response = requests.get(languages_url, headers=HEADERS)
    languages = list(lang_response.json().keys()) if lang_response.status_code == 200 else []

    # Get Commits
    commits_response = requests.get(commits_url, headers=HEADERS, params={'per_page': 1})
    commits = commits_response.headers.get('Link')

    # Extract commit count from headers (API pagination trick)
    if commits and 'rel="last"' in commits:
        last_page = commits.split('rel="last"')[0].split('page=')[-1].split('>')[0]
        commit_count = int(last_page)
    else:
        commit_count = 1 if commits_response.status_code == 200 else None

    # Build XML structure
    repo_elem = ET.SubElement(root, 'repository')
    ET.SubElement(repo_elem, 'url').text = repo_url
    ET.SubElement(repo_elem, 'about').text = about
    ET.SubElement(repo_elem, 'last_updated').text = last_updated
    ET.SubElement(repo_elem, 'languages').text = ', '.join(languages) if languages else 'None'
    ET.SubElement(repo_elem, 'commits').text = str(commit_count) if commit_count else 'None'

# === Pretty print and write to XML ===
xml_str = ET.tostring(root, encoding='utf-8')
parsed = minidom.parseString(xml_str)
with open('output.xml', 'w', encoding='utf-8') as f:
    f.write(parsed.toprettyxml(indent='  '))

print("✅ GitHub repo data saved to github_repos.xml")
