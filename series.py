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
    table_finds = soup.find('table', id='search_results').find_all('tr', re.compile(r'change even|change odd'))
    
    pager_list = soup.find('div', id='pager')
    links_pages = pager_list.find_all('a')
    links_pages.pop()

    id_content = []
    name_content = []
    #ahora una forma de unir esas dos cosas
    for content in table_finds:
        if len(content.find("strong").next_sibling)==0:
            id_content.append(re.sub(r'\D','',content.get('id')))
            name_content.append(content.find("strong").get_text().replace('\n \t\t\t',' '))
    for link in links_pages:
        response_search = requests.get(f'https://www.opensubtitles.org{link.get('href')}')
        if response_search.status_code != 200 :
            exit(1)
        soup = BeautifulSoup(response_search.text, 'html.parser')
        table_finds = soup.find('table', id='search_results').find_all('tr', re.compile(r'change even|change odd'))
        for content in table_finds:
            if len(content.find("strong").next_sibling)==0:
                id_content.append(re.sub(r'\D','',content.get('id')))
                name_content.append(content.find("strong").get_text().replace('\n \t\t\t',' '))
    return name_content, id_content

def extract_episodes( id ):
    url_select = 'https://www.opensubtitles.org/es/ssearch/sublanguageid-spa,spl/idmovie-'+id
    response_select = requests.get(url_select)
    if response_select.status_code!=200:
        print('exit')
        exit(1)
    soup_select = BeautifulSoup(response_select.text, 'html.parser')
    table_finds = soup_select.find('table', id='search_results')
    seasons_name = table_finds.find_all(id=re.compile(r'season-\d+'))
    info_data = table_finds.find_all('tr')
    info_data.pop(0)
    season = []
    new_season = []
    for info in info_data:
        if info.find(id=re.compile(r'season-\d+')):
            season.append(new_season)
            new_season = []
        else:
            new_season.append([info.find('a').get('href'), info.find('a').get_text(), info.find('span').get_text()])
            #[link, nombre, nro_episodio]
    season.pop(0)
    return season

def extract_subs( link ):
    url_sub = 'https://www.opensubtitles.org' + link
    response_sub = requests.get(url_sub)
    if response_sub.status_code!=200:
        exit(1)
    soup_sub = BeautifulSoup(response_sub.text, 'html.parser')
    subs_lists = soup_sub.find('tbody').find_all('tr', class_=re.compile(r'change even expandable|change odd expandable'))
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

def prueba_1():
    #cabe recalcar que es sin verificar errores.
    #---------proceso de seleccion de pelicula-serie------------#
    if len(sys.argv)==1:
        print('Introduce el path donde quieres guardar la descarga')
        exit(1)
    name_movie = input('enter the name of the movie-series: ').replace(' ', '+')
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

def prueba_2():
    name = input('nombre serie: ').replace(' ','+')
    names, ids = extract_ids(name)
    for name in enumerate(names):
        print(f'{name[0]}: {name[1]}')
    selected_id = int(input('elije la serie: '))
    #--------proceso de obtencion de los links/subs de todos-------------#
    seasons = extract_episodes(ids[selected_id])
    option = int( input('1) Descargar todas las seasons\n2) Descargar una season\n3) Descargar un capitulo\nSelecciona: ') )
    if option==1:
        print('se descargara todas las seasons')
    else:
        for i in range(len(seasons)):
            print(f'season nro {i+1}')
        nro_season = int(input('Seleccion la season: '))
        if option==2:
            print('se descarga la season entera')
        else:
            print(f'season nro {nro_season}')
            for chapter in seasons[nro_season-1]:
                print(f'capitulo nro. {chapter[2]}: {chapter[1]}')
            selected_episode = int( input('enter the select episode: ') )
            info_subs = extract_subs(seasons[nro_season][selected_episode-1][0])
            max_lengt = max(len(row[0]) for row in info_subs)
            for number,sub in enumerate(info_subs):
                print(f'{number}) {sub[0].ljust(max_lengt)} | {sub[1]} | {sub[2]}')

if __name__=='__main__':

    #va funciona de medio maravilla, solo que la prueba_1 ya no funcionara para nada
    #prueba_1()
    prueba_2()







