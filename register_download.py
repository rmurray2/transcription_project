from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import joblib
import os
import requests



od = joblib.load("island_dump")

root = '/run/media/rm/Samsung_T5/transcription_project/'
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')

driver = webdriver.Chrome('/home/rm/Downloads/chromedriver', options=options)

for island,i in od.items():
    if island != 'Flores': continue
    if not os.path.exists(root + island):
        os.mkdir(root + island)

    for concelho,j in od[island].items():
        print (concelho)
        if not os.path.exists(root + island + '/' + concelho):
            os.mkdir(root + island + '/' + concelho)

        for f, k in od[island][concelho].items():
            print (f)
            if not os.path.exists(root + island + '/' + concelho + '/' + f):
                os.mkdir( root + island + '/' + concelho + '/' + f)


            for period, z in od[island][concelho][f].items():
                print (period)
                if not os.path.exists(root + island + '/' + concelho + '/' + f + '/' + period):
                    os.mkdir(root + island + '/' + concelho + '/' + f + '/' + period)

                if not os.path.exists(root + island + '/' + concelho + '/' + f + '/' + period + '/original'):
                    os.mkdir(root + island + '/' + concelho + '/' + f + '/' + period + '/original')

                driver.get(z)
                #links to individual scan pages
                z = driver.find_elements_by_class_name("linkIndex")
                hrefs = {i.text:i.get_attribute('href') for i in z}
                for text, link in hrefs.items():
#                    driver.get(link)
#                    image = driver.find_element_by_id("pag")
#                    src = image.get_attribute("src")
#                    fn = src.split('/')[-1]
                    midsection = link.split('/')[4]
                    link = link.replace('item1', 'master')
                    link = '/'.join(link.split('/')[:-1])

                    src = link  + '/' + midsection + '_JPG/' + midsection + '_' + text + '.jpg'
                    print (src)


                    fn = text + '.jpg'
                    if os.path.exists(root + island + '/' + concelho + '/' + f + '/' +  period + '/original/' + fn):
                        continue
                    time.sleep(2)
                    img_data = requests.get(src).content
                    with open(root + island + '/' + concelho + '/' + f + '/' + period + '/original/' + fn, 'wb') as outfile:
                        outfile.write(img_data)









