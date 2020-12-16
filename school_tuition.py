import requests
from bs4 import BeautifulSoup
import re
import csv

csv_file = open('ranking_university_USnews.csv', 'wb', buffering=0)
writer = csv.writer(csv_file)

urls = ['https://www.usnews.com/best-graduate-schools/top-business-schools/mba-rankings']
records = []
ranks1 = []
names = []
locations = []
headers={ 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:67.0) Gecko/20100101 Firefox/67.0' }
for url in urls:
    r = requests.get(url,headers=headers)
    for rank in soup.findAll('span', attrs={'class': 'rankscore-bronze cluetip cluetip-stylized'}):
        ranks1.append(int(re.findall('\d+', rank.text)[0]))
    for college in soup.findAll('a', attrs={'class': 'school-name'}):
        names.append(college.text)
    for location in soup.findAll('p', attrs={'class': 'location'}):
        print(location)
        locations.append(location.text)

ranks2 = range(203, 281)
ranks = ranks1+list(ranks2)

for i in range(len(ranks)):
    records.append(i+1)
    records.append(ranks[i])
    records.append(names[i].encode('utf-8'))
    records.append(locations[i])
    writer.writerow(records)
    records = []
