# thpt
THPT 2018

Crawl CSDL thi THPC quốc gia năm 2018 từ Zing.vn

# Requirement

- Python 2
- `pip install requests BeautifulSoup`

# How to run

- Run `python crawl.py`
- Output is written in `out.csv`
- Check more configuration in `crawl.py`
- Press `Ctrl-C` once (do NOT press twice or more) to terminate job. Crawled data is not lost and saved in `out.csv`

# Student ID structure

- Cụm thi: 1 -> 63
- SBD tại cụm thi: 1 -> 99999
- Ví dụ thí sinh cụm thi Hà Nội (mã cụm thi 1), STT trong cụm thi: 1412 sẽ mang sbd: `01001412`
