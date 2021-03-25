from bs4 import BeautifulSoup
import requests
from pathlib import Path
import html2text
import pandas as pd

data_path = Path('data')

all_data = []

for path in data_path.glob('*'):
    with open(path, 'r') as f:
        data = f.read()
    soup = BeautifulSoup(data, 'html.parser')
    allul = soup.find_all('ul')
    print(" ==== ")
    print(" ==== ")
    print("READING "+str(path))
    print(" ==== ")
    print(" ==== ")
    for ul in allul:
        lis = ul.find_all(class_='lpt')
        if not lis:
            continue

        h = html2text.HTML2Text()
        print()
        print()
        tds = lis[0].find_all('td')
        title = h.handle(tds[0].text)
        authors = tds[1].text
        info = tds[2].text

        print()
        print(authors)
        print(info)
        pubinfo = ul.find_all('p', class_=None)
        doi = None
        for p in pubinfo:
            if "cyfrowy identyfikator" in p.text:
                doi = p.find('strong').text
        print(doi)
        journal = info.split(' — ')[0]
        page_and_date = info.split(' — ')[1]
        print(journal)
        print(page_and_date)

        points = None
        for a in ul.find_all('a'):
            if 'punktacja MNiSW, IF/LF' in a.text:
                print(a)
                punktacja_link = str(a).split('href="')[1]
                punktacja_link = punktacja_link.split('\" id=')[0]
                punktacja_link = punktacja_link.replace('amp;','')
                print(punktacja_link)
                punk_data = requests.get(punktacja_link)
                points = h.handle(punk_data.text)

        row = dict(
            authors=authors,
            title=title.replace("\n",""),
            journal=journal,
            date=page_and_date,
            doi=doi,
            point=points
        )
        all_data.append(row)

df = pd.DataFrame(all_data)
print(df)
df.to_excel('publikacje.xlsx', index=False)
with open('publikacje.txt','w') as f:
    for d in all_data:
        row = "Autorzy:{authors}\n" +\
        "tytuł publikacji:{title}\n" +\
        "Nazwa czasopisma:{journal}\n" +\
        "numer tomu, strona (rok):{date}\n" +\
        "numer doi:{doi}\n" +\
        "punktacja: {point}\n\n"
        f.write(row.format(**d))
