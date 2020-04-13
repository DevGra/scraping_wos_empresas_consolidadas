#!/usr/bin/env python
# coding: utf-8
import requests
import pandas as pd
from selenium import webdriver
from time import sleep
import re
from login import login
from functools import partial

url_login = "http://login.webofknowledge.com/error/Error?Error=IPError&PathInfo=%2F&RouterURL=http%3A%2F%2Fwww.webofknowledge.com%2F&Domain=.webofknowledge.com&Src=IP&Alias=WOK5"

# path usado no anaconda jupyter notebook
# driver_path = 'C:/Users/GRAZIANI/anaconda3/pkgs/selenium-3.141.0-py37he774522_0/Lib/site-packages/selenium/webdriver/chrome/chromedriver.exe'

driver_path = 'chromedriver.exe'

browser = webdriver.Chrome(driver_path)
browser.get(url_login)
sleep(2)

#seu nome e email aqui
dados = login()
email = dados[0]
senha = dados[1]

formulario = browser.find_element_by_tag_name("form")
email_input = formulario.find_element_by_name("username")
email_input.send_keys(email)
sleep(2)
pass_input = formulario.find_element_by_name("password")
pass_input.send_keys(senha)
sleep(2)
formulario.find_element_by_tag_name("a").click()

sleep(2)
string_busca = "WC=COMPUTER SCIENCE, ARTIFICIAL INTELLIGENCE AND CU=BRAZIL AND PY=(2017-2019)"
sleep(2)

div_box = browser.find_element_by_class_name("searchtype-nav")
advanced_search = div_box.find_elements_by_tag_name("a")[-1]
advanced_search.click()

div_box = browser.find_element_by_class_name("AdvSearchBox")
txt_area = div_box.find_element_by_tag_name("textarea")
sleep(2)
txt_area.send_keys(string_busca)

sleep(1)
btn_pesquisar = div_box.find_element_by_id("search-button")
btn_pesquisar.click()
sleep(2)

div_1 = browser.find_element_by_id("set_1_div")
text_itens = div_1.find_element_by_tag_name("a").text
text_qtd_itens = text_itens.replace(".", "")
qtd_itens = int(text_qtd_itens)
sleep(2)
div_1.find_element_by_tag_name("a").click()

div_search_results_content = browser.find_element_by_class_name("search-results-content")
tag_a = div_search_results_content.find_element_by_tag_name("a")
sleep(1)
tag_a.click()

# --- declaração das variáveis
lista_dados = []
names = ''
project = ''
inform_autors = ''
consolidado = ''
i = 1

while i <= qtd_itens:
    print(f"pagina --> {i}")
    sleep(2)
    info_names = browser.find_elements_by_xpath("//*[@id = 'records_form']/div/div/div/div[1]/div/div[2]")
    texto = info_names[0].text
    txt = texto.replace("Por:", "").replace("[", "").replace("]", "").replace("1", "").replace("2", "").replace("3",
                                                                                                                "").replace(
        "\nExibir ResearcherID e ORCID do Web of Science", "")
    name = txt.strip().replace(" ", "")
    names = name

    sleep(1)
    info_dados = browser.find_elements_by_xpath("//*[@id='records_form']/div/div/div/div[1]/div/div[3]")[0].text
    lista_info = info_dados.split("\n")
    proj = lista_info[0]
    project = proj

    try:
        # import pdb;pdb.set_trace()
        # vol_list = list(filter(lambda x: busca_dados(f=x, dado="Volume"), lista_info))
        buscar = 'Volume'
        vol_list = list(filter(lambda x: x.startswith(buscar), lista_info))
        vol_split = [i.split(':', 2)[1] for i in vol_list]
        vol = re.findall(r'\b\d+\b', vol_split[0])
        vol = vol[0]

    except Exception as e:
        print("Não há informações sobre o volume...", e)
        vol = 'na'
    volume = vol
    sleep(2)
    # import pdb;pdb.set_trace()
    # print('numero do artigo')
    try:
        buscar = "Número do artigo"
        # art_list = list(filter(lambda x: busca_dados(f=x, dado="Número do artigo"), lista_info))
        art_list = list(filter(lambda x: x.startswith(buscar), lista_info))
        art_split = [i.split(':', 2)[1] for i in art_list]
        n_art = re.findall(r'\b\d+\b', art_split[0])
        n_art = n_art[0]

    except Exception as e:
        print("Não há informações sobre o artigo...", e)
        n_art = 'na'
    n_artigo = n_art
    sleep(2)
    # import pdb;pdb.set_trace()
    # print('DOI')
    try:
        buscar = "DOI"
        # doi_list = list(filter(lambda x: busca_dados(f=x, dado="DOI"), lista_info))
        doi_list = list(filter(lambda x: x.startswith(buscar), lista_info))
        doi_split = [i.split(':', 2)[1] for i in doi_list]
        doi_proj = doi_split[0].strip()

    except Exception as e:
        print("Não há informações sobre o DOI...", e)
        doi_proj = 'na'
    doi = doi_proj
    sleep(2)
    # import pdb;pdb.set_trace()
    # print('publicado')
    try:
        buscar = "Publicado"
        # public_list = list(filter(lambda x: busca_dados(f=x, dado="Número do artigo"), lista_info))
        public_list = list(filter(lambda x: x.startswith(buscar), lista_info))
        public_split = [i.split(':', 2)[1] for i in public_list]
        public = public_split[0]

    except Exception as e:
        print("Não há informações sobre a publicação...", e)
        public = 'na'
    publication = public

    info_autors = browser.find_elements_by_xpath("//*[@id = 'records_form']/div/div/div/div[1]/div/div[6]")
    # import pdb;pdb.set_trace()
    txt_autor = ''
    for info_autor in info_autors:
        # import pdb;pdb.set_trace()
        txt_autor = info_autor.text
        try:
            adress1 = txt_autor.split(":")[1].replace("\n", " ").replace("Endereços", "").strip()
            adress2 = txt_autor.split(":")[2].replace("[", "").replace("]", "").replace("\n", "").replace(
                "Endereços de e-mail", "").strip()
            txt_autor = adress1 + adress2
        except Exception as e:
            print("Não há informações sobre autores...", e)
            txt_autor = 'na'

    inform_autors = txt_autor

    list_consolid = []
    itr = 1
    try:
        tbl_endereco = browser.find_elements_by_class_name('FR_table_noborders')
        # import pdb;pdb.set_trace()
        qdt_endereco = len(tbl_endereco)

    except Exception as e:
        print("Não há informações sobre consolidação...", e)
        consolid = 'na'
        list_consolid.append(consolid)
    t = 1

    for tb in tbl_endereco:

        id_reprint = "//*[@id=" + "'" + "show_reprint_pref_org_exp_link_" + str(itr) + "'" + "]/a"
        id_txt_reprint = "//*[@id=" + "'" + "reprint_pref_org_exp_link_" + str(itr) + "'" + "]/preferred_org"
        # print(f't -->{t}')
        # print(f'len tbl_endereco -->{len(tbl_endereco)}')
        # import pdb;pdb.set_trace()

        if t < len(tbl_endereco):
            # print("Reprint")
            # print(id_reprint)
            # print(id_txt_reprint)

            try:
                # import pdb;pdb.set_trace()
                # sleep(2)
                tb.find_element_by_xpath(id_reprint).click()
                sleep(2)
                tx_consolid = browser.find_element_by_xpath(id_txt_reprint).text
                list_consolid.append(tx_consolid)
            except Exception as e:
                print("Não há informação endereço reprint", e)
                consolid = 'na'
                sleep(2)
                list_consolid.append(consolid)

            # print("Lista consolidada reprint")
            # print(list_consolid)

        else:
            ite = 1
            trs = tb.find_elements_by_tag_name('tr')
            qtd_tr = len(trs)

            for tr in trs:
                id_a_tag = "//*[@id=" + "'" + "show_research_pref_org_exp_link_" + str(ite) + "'" + "]/a"
                id_txt_consolid = "//*[@id=" + "'" + "research_pref_org_exp_link_" + str(ite) + "'" + "]/preferred_org"

                if ite <= qtd_tr:
                    try:
                        sleep(1)
                        tr.find_element_by_xpath(id_a_tag).click()
                        sleep(1)
                        # import pdb;pdb.set_trace()
                        txt_consolid = tr.find_element_by_xpath(id_txt_consolid).text
                        # import pdb;pdb.set_trace()
                        sleep(1)
                        list_consolid.append(txt_consolid)
                    except Exception as e:
                        print("Não há informação de consolidado..", e)
                        consolid = 'na'
                        sleep(1)
                        list_consolid.append(consolid)

                    ite += 1
                print(list_consolid)

        t += 1
        itr += 1

    consolid = ",".join(list_consolid)
    consolidado = consolid

    dict_temp = {"Pagina": i, "Nomes": names, "Projeto": project, "Volume": volume, "Nº Artigo": n_artigo, "DOI": doi,
                 "Publicação": publication, "Informação dos autores": inform_autors, "Consolidado": consolidado}
    lista_dados.append(dict_temp)

    print(lista_dados[-1]['Consolidado'])
    print(f"fim da pagina _> {i}")

    try:
        form_pgnation = browser.find_element_by_id("paginationForm")
        link_prox = form_pgnation.find_element_by_xpath("//*[@id = 'paginationForm']/span/a[2]")
        sleep(2)
        link_prox.click()
    except Exception as e:
        print("Algo de errado com o link...", e)

    if (qtd_itens == i):
        print("Terminou...")
    i += 1

sleep(3)
browser.find_element_by_xpath("/html/body/div[1]/div[22]/ul[2]/li[1]/a").click()
# a_title = browser.find_elements_by_css_selector('li.nav-item')[1].click()
sleep(1)
browser.find_element_by_xpath("/html/body/div[1]/div[22]/ul[2]/li[1]/ul/li[2]/a").click()
browser.quit()

lista = lista_dados
df_scrap = pd.DataFrame.from_dict(lista, orient='columns')
df_scrap.to_excel("dados_scrap_organizacao2.xlsx", encoding='utf-8')

# --------------- arquivos para teste deste codigo -----------------------------------

items = ['EXPERT SYSTEMS WITH APPLICATIONS', 'Volume: 138', 'Número do artigo: UNSP 112812',
         'DOI: 10.1016/j.eswa.2019.07.029', 'Publicado:DEC 30 2019', 'Tipo de documento:Article',
         'Visualizar impacto do periódico']
prefix = 'Volume'

vol_list = list(filter(lambda x: x.startswith(prefix), items))
print(vol_list)
vol_split = [i.split(':', 2)[1] for i in vol_list]
vol = re.findall(r'\b\d+\b', vol_split[0])
print(vol[0])
