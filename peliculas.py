import sys
import requests
import re
from bs4 import BeautifulSoup

def extract_movies_ids(movie_name):
    url_search = 'https://www.opensubtitles.org/es/search2/moviename-'+movie_name+'/sublanguageid-spa,spl'
    response_search = requests.get(url_search)
    if response_search.status_code != 200 :
        exit(1)
    soup = BeautifulSoup(response_search.text, 'html.parser')
    table_finds = soup.find('table', id='search_results')

    pattern = re.compile(r'change even|change odd')
    table_content = table_finds.find_all('tr', class_=pattern)
    data = []
    for content in table_content:
        name = content.find("strong").get_text().replace('\n \t\t\t',' ')
        id = re.sub(r'\D','',content.get('id'))
        new_data = [name, id]
        data.append(new_data)
    return data
def extract_movies_subs(id_movie):
    url = 'https://www.opensubtitles.org/es/search/sublanguageid-spa,spl/idmovie-'+id_movie
    response_search = requests.get(url)
    if response_search.status_code != 200:
        exit(1)
    soup = BeautifulSoup(response_search.text, 'html.parser')
    table_data = soup.find('table', id='search_results')
    pattern = re.compile(r'change even|change odd')
    table_subs = table_data.find_all('tr', class_=pattern)
    info_subs = []

    # nombre - fecha_subido - nro_downloads - autor #
    for sub in table_subs:
        #name_sub = f"{re.sub(r'\s+', '', sub.find('br').next_sibling.strip())}"
        name_sub = sub.find('br').next_sibling
        time = re.sub(r'\s+', '', sub.find('time').get_text())
        link = re.sub(r'\s+', '', sub.find('a').get('href'))
        new_sub = [name_sub, time, link]
        info_subs.append(new_sub)
    return info_subs

def download_file(url_sub, path_save):
    url_download = 'https://www.opensubtitles.org' + url_sub
    response_download = requests.get(url_download)
    soup_download = BeautifulSoup(response_download.text, 'html.parser')

    link_download = 'https://www.opensubtitles.org' + soup_download.find('a', id='bt-dwl-bt').get('href')
    download_file = requests.get(link_download, stream=True)
    file_name = path_save +soup_download.find('a', id='bt-dwl-bt').get('data-product-file-name')
    if download_file.status_code != 200:
        exit(1)
    with open(file_name, 'wb') as file:
        for chunk in download_file.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
    print(f'archivo descargado: {file_name}')

if __name__=='__main__':
    if len(sys.argv)==1:
        print('Introduce el path donde vas a guardar')
        exit(1)
    movie_name = input('Introduce el nombre de la pelicula: ')

    data_peli = extract_movies_ids(movie_name)
    for number, data in enumerate(data_peli):
        print(f'{number}: {data[0]}')

    select_id = int(input('Selecciona la pelicula: '))
    data_subs = extract_movies_subs(data_peli[select_id][1])
    for number, data in enumerate(data_subs):
        print(f'{number}) {data[0]}, {data[1]}')

    select_sub = int(input('Selecciona el subtitulo: '))
    download_file(data_subs[select_sub][2], sys.argv[1])