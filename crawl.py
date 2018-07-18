from BeautifulSoup import BeautifulSoup as bs
import requests
import csv
import sys
import time

base_url = 'https://news.zing.vn/tra-cuu-diem-thpt-2018.html'
#time interval in seconds
time_interval = 0.3

#sbd: string
def crawl(sbd):
    try:
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
    except:
        print("Unexpected error when crawling %s: " % sbd, sys.exc_info()[0])
        print(res.text, res, res.status_code)
        raise
        return None

csvfile = open('out.csv', 'wb')
csvwriter = csv.writer(csvfile)
subjects = {}

def force_set(lst, idx, val):
    while len(lst) <= idx:
        lst.append('')
    lst[idx] = val
    return lst

def write_student(pref, sbd_id, student):
    row = [pref, sbd_id]
    for subject, score in  student.iteritems():
        if subject in subjects:
            index = subjects[subject]
        else:
            index = len(subjects)
            subjects[subject] = index
        force_set(row, index + 2, score)
    csvwriter.writerow(row)

def crawl_and_write(pref, sbd_id):
    sbd = "%02d0%05d" % (pref, sbd_id)
    student = crawl(sbd)
    if (student != None):
        write_student(pref, sbd_id, student)
        return True
    return False

def scan_all(pref_start, pref_end, sbd_id_start, sbd_id_end):
    for pref in range(pref_start, pref_end + 1):
        found = False
        for sbd_id in range(sbd_id_start, sbd_id_end + 1):
            try:
                if crawl_and_write(pref, sbd_id):
                    found = True
                time.sleep(time_interval)
            except:
                return
        if not found:
            print("No student data in pref code %d\n" % pref)

scan_all(1, 63, 0, 99999)
# crawl_and_write(63, 100)
# crawl_and_write(63, 100)
row = ['prefecture', 'student_id']
for subject, index in subjects.iteritems():
    force_set(row, index + 2, subject)
csvwriter.writerow(row)
