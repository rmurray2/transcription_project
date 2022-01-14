from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup

import joblib


'''


create a master dict with links to book scan pages


'''

def get_table(text):
	data = []
	soup = BeautifulSoup(text)

	table = soup.find('table', attrs={'class':'tListagem1'}) 

	table_body = table.find('tbody')

	rows = table_body.find_all('tr')

	for row in rows:
		cols = row.find_all('td')
		cols = [ele.text.strip() for ele in cols]
		data.append([ele for ele in cols if ele])
	return data
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome('/home/rm/Downloads/chromedriver', options=options)

driver.get('http://www.culturacores.azores.gov.pt/ig/registos/')




island_dd = driver.find_element_by_id("cplHolder_ctlRegistos_cboIlha")
island_select = Select(island_dd)



null_text = "Todos"

island_options = [i.text for i in island_select.options]
#island_options = ['Flores']
od = {}

for island in island_options:
    island_dd = driver.find_element_by_id("cplHolder_ctlRegistos_cboIlha")
    island_select = Select(island_dd)
        
    if island != 'Todos' and island != 'Todas':
        od[island] = {}
        print (island)
        island_select.select_by_visible_text(island)
        time.sleep(2)
        concelho_dd = driver.find_element_by_name("_ctl0:cplHolder:ctlRegistos:cboConcelho")
        concelho_select = Select(concelho_dd)
        concelho_options = [i.text for i in concelho_select.options]

        for concelho in concelho_options:

            if concelho != 'Todos' and concelho != 'Todas':
                od[island][concelho] = {}
                print ('\t', concelho)
                concelho_dd = driver.find_element_by_name("_ctl0:cplHolder:ctlRegistos:cboConcelho")
                concelho_select = Select(concelho_dd)
                concelho_select.select_by_visible_text(concelho)
                time.sleep(2)
                freguesia_dd = driver.find_element_by_name("_ctl0:cplHolder:ctlRegistos:cboFreguesia")
                freguesia_select = Select(freguesia_dd)
                freguesia_options = [i.text for i in freguesia_select.options]


                for freguesia in freguesia_options:

                    if freguesia != 'Todos' and freguesia != 'Todas':
                        od[island][concelho][freguesia] = {}
                        print ('\t\t', freguesia)
                        freguesia_dd = driver.find_element_by_name("_ctl0:cplHolder:ctlRegistos:cboFreguesia")
                        freguesia_select = Select(freguesia_dd)
                        freguesia_select.select_by_visible_text(freguesia)
                        time.sleep(2)
                        baptisms = driver.find_element_by_xpath("/html/body/form[@id='form1']/div[@class='contentor']/div[@id='cplHolder_ctlRegistos_upIGRegistos']/div[@class='pesquisa']/div[@class='container']/div[@class='formBox formBox700']/table[@id='cplHolder_ctlRegistos_radSerie']/tbody/tr/td[2]/input[@id='cplHolder_ctlRegistos_radSerie_1']")
                        baptisms.click()
                        search_button = driver.find_element_by_name("_ctl0:cplHolder:ctlRegistos:cmdSubmit")
                        search_button.click()
                        res = get_table(driver.page_source)

                        z = driver.find_elements_by_link_text("Ver")
                        for i,link in enumerate(z):
                            link_text = link.get_attribute('href')
                            index = i+1
                            period = res[index][-2]
                            od[island][concelho][freguesia][period] = link_text
#                            print (len(od[island][concelho][freguesia]))

                        multiple_pages_link = driver.find_elements_by_link_text("2")
                        print (multiple_pages_link, '******************')

                        if multiple_pages_link != []:
                            for index in range(2, 10):
                                next_page_link = driver.find_elements_by_link_text(str(index))
                                if next_page_link == []:
                                    break
                                else:
                                    print (index, '*******')
                                    next_page_link[0].click()
                                    time.sleep(2)

                                    res = get_table(driver.page_source)
                                    z = driver.find_elements_by_link_text("Ver")
                                    for i,link in enumerate(z):
                                        link_text = link.get_attribute('href')
                                        index = i+1
                                        period = res[index][-2]
                                        od[island][concelho][freguesia][period] = link_text
#                                        print (len(od[island][concelho][freguesia]))



#                        print (od)

                            


joblib.dump(od, 'island_dump')
						




		
