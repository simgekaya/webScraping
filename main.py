import requests
from bs4 import BeautifulSoup
import csv
import os
import uuid

url = 'http://www.tk.org.tr/index.php/tk/issue/archive'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

h4s = soup.find_all('h4')

links = []
for h4 in h4s:
    link_tags = h4.find_all('a')
    for link in link_tags:
        link_ciltsayi = link.text.strip()
        link_url = link.get('href')
        link_response = requests.get(link_url)
        link_soup = BeautifulSoup(link_response.content, 'html.parser')
        link_makale = [td.text.strip() for td in link_soup.find_all('td', {'class': 'tocTitle'})]
        link_yazar = [td.text.strip() for td in link_soup.find_all('td', {'class': 'tocAuthors'})]
        link_sayfa = [td.text.strip() for td in link_soup.find_all('td', {'class': 'tocPages'})]
        link_detay = [link.get('href') for link in link_soup.find_all('a', {'class': 'file'})]
        links.append({'CiltSayi': link_ciltsayi, 'Makale': link_makale, 'Yazar':link_yazar, 'Sayfa':link_sayfa, 'Icindekiler':link_url, 'MakaleDetay':link_detay})

with open('turkkutuphaneciligi.csv', mode='w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['CiltSayi', 'Makale', 'Yazar', 'Sayfa', 'Icindekiler', 'MakaleDetay'])
    for link in links:
        for i in range(len(link['Makale'])):
            if i < len(link['Yazar']) and i < len(link['Sayfa']) and i < len(link['MakaleDetay']):
                writer.writerow([link['CiltSayi'], link['Makale'][i], link['Yazar'][i], link['Sayfa'][i], link['Icindekiler'], link['MakaleDetay'][i]])


with open('turkkutuphaneciligi.csv', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    rows = []
    for row in reader:
        if 'view' in row['MakaleDetay']:
            row['MakaleDetay'] = row['MakaleDetay'].replace('view', 'download')
        rows.append(row)

with open('turkkutuphaneciligi_guncel.csv', mode='w', encoding='utf-8', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=['CiltSayi', 'Makale', 'Yazar', 'Sayfa', 'Icindekiler', 'MakaleDetay'])
    writer.writeheader()
    writer.writerows(rows)

dosya_konumu = '/Users/Simge/Desktop/mantis'

with open('turkkutuphaneciligi_guncel.csv', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        download_url = row['MakaleDetay']
        filename = row['MakaleDetay'].split('/')[-1]
        response = requests.get(download_url, stream=True)

        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
            print(f"{filename} downloaded.")

        # Rename the downloaded file with a random UUID
        yeni_isim = str(uuid.uuid4()) + '.pdf'
        eski_yol = os.path.join(dosya_konumu, filename)
        yeni_yol = os.path.join(dosya_konumu, yeni_isim)
        os.rename(eski_yol, yeni_yol)

