from BeautifulSoup import BeautifulSoup as bs
import requests
import csv
import sys
import time
import signal

base_url = 'https://news.zing.vn/tra-cuu-diem-thpt-2018.html'
#time interval in seconds
time_interval = 0.4

#number of retries when fail
max_retry = 10
#retry interval
retry_interval = 1

pref_start = 1
pref_end = 63
sbd_id_start = 0
sbd_id_end = 99999
last_fail_pref = 1
last_fail_sbd_id = 3349

# verbose each 10 students
verbose_range = 10

# if there no data in 100 consecutive students -> quit that pref
stop_threshold = 100

flush_freq = 50
ctrl_c_interupted = [False]

user_agents = [
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0)"
        ]

#sbd: string
def crawl(sbd, user_agent =  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36'):
    try:
        student = {}
        res = requests.get(base_url,
            params={'location': '0', 'q': sbd},
            allow_redirects=True,
            headers= {'User-Agent': user_agent}
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
subjects = {

        'lich-su': 0,
        'dia-li': 1,
        'khxh': 2,
        'gdcd': 3,
        'ngu-van': 4,
        'toan-hoc': 5,
        'tieng-anh': 6,
        'sinh-hoc': 7,
        'vat-li': 8,
        'khtn': 9,
        'hoa-hoc': 10,
        'tieng-trung': 11,
        'tieng-nhat': 12
        }

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
            print("new subject has been added", subjects)
        force_set(row, index + 2, score)
    csvwriter.writerow(row)
    if sbd_id % flush_freq == 0:
        csvfile.flush()

def crawl_and_write(pref, sbd_id):
    sbd = "%02d0%05d" % (pref, sbd_id)
    student = crawl(sbd, user_agent = user_agents[sbd_id % len(user_agents)])
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
                if ctrl_c_interupted[0]:
                    return
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
            if notfound_cnt >= stop_threshold:
                break
            time.sleep(time_interval)
        if cnt == 0:
            print("No student data in pref code %d" % pref)

def write_subjects():
    row = ['prefecture', 'student_id']
    for subject, index in subjects.iteritems():
        force_set(row, index + 2, subject)
    csvwriter.writerow(row)
def signal_handler(sign, frame):
    ctrl_c_interupted[0] = True
    print("you pressed Ctrl-C!")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

scan_all(pref_start, pref_end, sbd_id_start, sbd_id_end, last_fail_pref, last_fail_sbd_id)

write_subjects()
csvfile.flush()
