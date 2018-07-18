from BeautifulSoup import BeautifulSoup as bs
import requests
import csv
import sys
import time

base_url = 'https://news.zing.vn/tra-cuu-diem-thpt-2018.html'
#time interval in seconds
time_interval = 0.5
max_retry = 10
retry_interval = 1
pref_start = 1
pref_end = 63
sbd_id_start = 0
sbd_id_end = 99999
last_fail_pref = 1
last_fail_sbd_id = 499

# verbose each 10 students
verbose_range = 10

# if there no data in 100 consecutive students -> quit that pref
stop_threshold = 100

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
        print("Unexpected error when crawling %s. Status code = %d" % (sbd, res.status_code))
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

def scan_all(pref_start, pref_end, sbd_id_start, sbd_id_end, last_fail_pref, last_fail_sbd_id):
    for pref in range(max(pref_start, last_fail_pref), pref_end + 1):
        cnt = 0
        notfound_cnt = 0
        if pref == last_fail_pref:
            start_index = max(last_fail_sbd_id, sbd_id_start)
        else:
            start_index = sbd_id_start
        print("Start crawling pref id %d" % pref)
        for sbd_id in range(start_index, sbd_id_end + 1):
            retry = 0
            if (sbd_id % verbose_range == 0):
                print("crawling student (%d, %d) (cnt = %d)" % (pref, sbd_id, cnt))
            while retry < max_retry:
                try:
                    if crawl_and_write(pref, sbd_id):
                        cnt += 1
                        notfound_cnt = 0
                    else:
                        notfound_cnt += 1
                    retry = max_retry
                except:
                    retry += 1
                    time.sleep(retry_interval)
                    print("Crawling student (%d, %d) failed, retry %d" %(pref, sbd_id, retry))
            if notfound_cnt >= stop-stop_threshold:
                break
            time.sleep(time_interval)
        if cnt == 0:
            print("No student data in pref code %d" % pref)

scan_all(pref_start, pref_end, sbd_id_start, sbd_id_end, last_fail_pref, last_fail_sbd_id)
# crawl_and_write(63, 100)
# crawl_and_write(63, 100)
row = ['prefecture', 'student_id']
for subject, index in subjects.iteritems():
    force_set(row, index + 2, subject)
csvwriter.writerow(row)
