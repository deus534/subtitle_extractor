import sys
from http.client import responses

import requests
import re
from bs4 import BeautifulSoup


#id = search_results
#class = change even
#class = bnome

def extract_ids( movie_name ):
    url_search = 'https://www.opensubtitles.org/es/search2/moviename-'+movie_name+'/sublanguageid-spa,spl'
    response_search = requests.get(url_search)
    if response_search.status_code != 200 :
        exit(1)
    soup = BeautifulSoup(response_search.text, 'html.parser')
    table_finds = soup.find('table', id='search_results')

    table_content = table_finds.find_all('tr', class_='change even')
    id_content = []
    name_content = []
    indice = 1
    for content in table_content:
        name_content.append(content.find("strong").get_text().replace('\n \t\t\t',' '))
        id_content.append(re.sub(r'\D','',content.get('id')))
        indice+=1
    return name_content, id_content
def extract_episodes( id ):
    url_select = 'https://www.opensubtitles.org/es/ssearch/sublanguageid-spa,spl/idmovie-'+id
    response_select = requests.get(url_select)
    if response_select.status_code!=200:
        print('exit')
        exit(1)
    soup_select = BeautifulSoup(response_select.text, 'html.parser')
    table_finds = soup_select.find('tbody')
    #table_finds = soup_select.find('table', id='search_results')
    pattern = re.compile(r'change even|change odd')
    seasons_name = table_finds.find_all(id=re.compile(r'season-\d+'))
    episodes = table_finds.find_all('tr', class_=pattern)
    links = []
    name_episodes = []
    for episode in episodes:
        #print(episode)
        links.append(episode.find('a').get('href'))
        name_episodes.append(episode.find('a').get_text())
    return name_episodes, links
def extract_subs( link ):
    url_sub = 'https://www.opensubtitles.org' + link
    response_sub = requests.get(url_sub)
    if response_sub.status_code!=200:
        exit(1)
    soup_sub = BeautifulSoup(response_sub.text, 'html.parser')

    pattern = re.compile(r'change even expandable|change odd expandable')
    table_select = soup_sub.find('tbody')
    subs_lists = table_select.find_all('tr', class_=pattern)

    info_subs = []

    #nombre - fecha_subido - nro_downloads - autor #
    for sub in subs_lists:
        #name_sub = f"{re.sub(r'\s+','',sub.find('strong').get_text())} - ({sub.find('br').next_sibling.strip()})"
        name_sub = f"{re.sub(r'\s+','',sub.find('br').next_sibling.strip())}"
        time = re.sub(r'\s+','',sub.find('time').get_text())
        link = re.sub(r'\s+','',sub.find('a').get('href'))
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
    #cabe recalcar que es sin verificar errores.
    #---------proceso de seleccion de pelicula-serie------------#
    if len(sys.argv)==1:
        print('Introduce el path donde quieres guardar la descarga')
        exit(1)
    print('Example movie-series name format: rick+and+morty')
    name_movie = input('enter the name of the movie-series: ')
    names, ids = extract_ids(name_movie)
    for name in enumerate(names):
        print(f'{name[0]}: {name[1]}')
    selected_id = int( input('enter the select movie-serie: ') )

    #---------------------------------------------------------------------#
    option = int(input('1) Season\n2)episodes\nDowloand Season or episode'))

    #--------proceso de obtencion de los links/subs de todos-------------#
    episodes, links = extract_episodes(ids[selected_id])
    for number, episode in enumerate(episodes):
        print(f'{number}: {episode}')
    selected_episode = int( input('enter the select episode: ') )

    #---------------------------------------------------------------------#
    info_subs = extract_subs(links[selected_episode])
    max_lengt = max(len(row[0]) for row in info_subs)
    for number,sub in enumerate(info_subs):
        print(f'{number}) {sub[0].ljust(max_lengt)} | {sub[1]} | {sub[2]}')
    selected_sub = int( input('enter the select sub: ') )

    # ---------------------------------------------------------------------#
    download_file(info_subs[selected_sub][2], sys.argv[1])

    #programa funcional donde tenes que romperte los huevos.. jajja
    #names, ids = extract_ids(sys.argv[1])
    #episodes, links = extract_episodes(ids[0])
    #info_subs = extract_subs(links[0])
    #download_file(info_subs[0][2])
