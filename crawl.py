from BeautifulSoup import BeautifulSoup as bs
import requests
import csv

base_url = 'https://news.zing.vn/tra-cuu-diem-thpt-2018.html'

#sbd: string
def crawl(sbd):
    student = {}
    res = requests.get(base_url,
        params={'location': '0', 'q': sbd},
        allow_redirects=True,
        headers= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36'}
        )
    html = bs(res.text)

    # check if not exist
    if (html.find('h3', {'class': 'title-info alert'}) != None):
        return None
    tr_list = html.find('tbody').contents
    assert(len(tr_list) % 2 == 1)
    for i in range((len(tr_list) - 3) / 2):
        tr = tr_list[i * 2 + 1]
        subject = tr['data-name']
        score = float(tr.contents[5].contents[0].string)
        student[subject] = score
    return student

for pref in 
print(crawl('63000100'))
csvfile = open('out.csv', 'wb')
csvwriter = csv.writer(csvfile)
csvwriter.writerow(['hello', '', 'myworld'])
csvwriter.writerow(['another hello', None, 'myworld'])
