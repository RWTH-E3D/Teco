import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# link = "https://www.oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?uuid=dcd5e23a-9bec-40b6-b07c-1642fe696a2e&version=20.19.120"
# link = "https://webtool.building-typology.eu/data/matrix/building/de/p/0/o/0/l/10/dc/1234567890123"
# link = "https://oekobaudat.de/OEKOBAU.DAT/resource/datastocks/cd2bda71-760b-4fcc-8a0b-3877c10000a8/processes/b7cacb37-7945-4518-be5a-bf7df7edf5c2?format=html&lang=en&version=20.19.120"
from selenium.webdriver import ActionChains
from sympy import false, true

# stages = ["A1-A3", "A1", "A2", "A3", "A4", "A5", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "C1", "C2", "C3", "C4", "D"]
"""
df = pd.read_csv("C:\\Users\\tayeb\\Documents\\OEKOBAUDAT.csv", delimiter=';', encoding='latin-1')
print(df['URL'])
for link in df.loc['URL']:
    table = pd.read_html(link)
    df = table[len(table)-1] # make this better?

    row = df.loc[df['Indicator'] == 'Global warming potential (GWP)']
    print(row.iloc[0, 0])
    unit = row.iloc[0].loc['Unit']
    clean_row = row.iloc[0].str.slice(stop=5)
    print(clean_row) # change to stopping at dollar sign?
    for stage in df.columns[2:]:
        print(stage)
        print(clean_row.loc[stage])
"""


def TABULA_DE(self):
    df = pd.read_excel("C:/Users/tayeb/Documents/Teaser+,Teco/TABULA-Analyses_DE-Typology_ResultData.xlsx",
                       sheet_name=0)
    # print(df.loc[554:1357,:])

    Code_BuiSysCombi = df['Code_BuiSysCombi'][556:1359]
    Description_National_SysH = df['Description_National_SysH'][556:1359]
    Description_National_SysW = df['Description_National_SysW'][556:1359]
    Description_National_SystemType = df['Description_National_SystemType'][556:1359]
    Description_National_System_AssignedMeasure = df['Description_National_System_AssignedMeasure'][556:1359]

    pd.DataFrame(
        [Code_BuiSysCombi, Description_National_SysH, Description_National_SysW, Description_National_SystemType,
         Description_National_System_AssignedMeasure]).to_excel("sheet.xlsx")


""" load libraries ???"""

link = "http://www.oekobaudat.de/no_cache/en/database/search.html"
# soup = BeautifulSoup(requests.get(link).text, "html.parser")
# OEKOBAUDAT = pd.read_html(link)
# print(OEKOBAUDAT.columns)


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException

driver = webdriver.Firefox()  # seconds
driver.get(link)

elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "ui-table-tbody")))

print(driver.title)
# print(driver.page_source)
button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="c1552"]/s4lca-root-0/div/s4lca-process/div/p-table/div/div[1]/div[2]/p-togglebutton')))
print(button.click())


actions = ActionChains(driver)

element = driver.find_element(By.XPATH, '/html/body/div[3]/div/div[2]/div/div[2]/s4lca-categories/p-tree/div/div/ul/p-treenode[8]/li/div/span')
actions.move_to_element(element).click().perform()

#if element.find_element(By.TAG_NAME, 'aria-expanded'):
element = element.find_element(By.XPATH, '//*[@id="lang-en"]/div[3]/div/div[2]/div/div[2]/s4lca-categories/p-tree/div/div/ul/p-treenode[8]/li/ul/p-treenode[1]/li/div')
actions.move_to_element(element).click().perform()


#next_button = driver.find_element(By.CSS_SELECTOR, 'p-treenode.ng-star-inserted:nth-child(9) > li:nth-child(1) > div:nth-child(1) > span:nth-child(3) > span:nth-child(1) > span:nth-child(1)')

#element = driver.find_element(By.CSS_SELECTOR, "p-treenode.ng-star-inserted:nth-child(8)>li:nth-child(1)>div:nth-child(1)>span:nth-child(3)>span:nth-child(1)>span:nth-child(1)")
#element_ = driver.find_element(By.XPATH, "/html/body/div[3]/div/div[2]/div/div[2]/s4lca-categories/p-tree/div/div/ul/p-treenode[8]/li/div/span[3]/span/span")
#print(element_.click())
#print(element.click())

#element = driver.find_element(By.LINK_TEXT, "8. Building service engineering")
# tree = driver.find_element(By.XPATH,
#                           '//*[@id="lang-en"]/div[3]/div/div[2]/div/div[2]/s4lca-categories/p-tree/div/div/ul')
# except:
#        print("error: ")
time.sleep(10)
driver.close()
'''
    time.sleep(1)
    Error = true
    i = 0
    tree_child = tree
    while i < 6 and Error:
        try:
            tree_child = tree_child.find_element(By.XPATH, './child::*')
            print(tree_child.click())
        except ElementNotInteractableException:
            print("ElementNotInteractableException")
            i = i + 1
            time.sleep(2)
    print(i)
    time.sleep(10)
    driver.close()
    # !!!!!!!!try manually clicking on tree_node elements, otherwise try changing the value of the variable expand or wtv its called
'''
# print([ for stage in row[2:] in row.iloc[0]])
# idea: take directly first row, then check if its GWP, then only if its not, call a for loop

# html manipulation with for loops and if statements (badddd)
"""
r = requests.get(link)

soup = BeautifulSoup(r.text, 'html.parser')
forms = soup.find_all("form")

for form in forms:
    if "lcia" in form['id']:
        elements = form.tbody.find_all("a")
        for element in elements:
            indicator_values = []
            if element.text.find("GWP") != -1:
                trs = list(element.parent.parent.next_siblings)
                for _ in range(len(trs)-1):
                    try:
                        indicator_values.append(trs[_+1].span.text)
                    except AttributeError as err:
                        print("span doesnt exist! ", err)
                print(indicator_values)
            else:
                print("GWP not found!")

            stage_titles = []
            for stage_title in form.find_all("th", {"role": "columnheader"}):
                # stage_titles.append(stage_title.text.translate(str.maketrans({chr(10): ' ', chr(9): ''})))
                stage_titles.append(stage_title.text)

                i = 0
                # go through possible stages (in parallel while saving the stages given)
                for stage in stages:
                    if stage in stage_title.text:
                        if stage == "A1-A3":    # in the case  of A1-A3
                            stage.replace('-', '_')
                        # getattr(self.parent.lca_data.gwp,lower(stages[i]))
                        print("self.parent.lca_data.gwp.", str.lower(stages[i]))

            # unit
            indicator_unit = stage_titles[1]

            # titles
            stage_titles = stage_titles[2:]

            print(stage_titles)

            break
        break
"""

"""
# print("output: ", html_to_json.convert(output))
res = output.find("lciaindicatorsform")
print("res4: ", output[res-35:])
res = output.find("GWP")
gwp_text = output[res:]
print("res: ", res)
res2 = output[res+7:].find("</form>")
print("res2: ", res2)
res3 = output[res2+7:].find("</form>")
print("res3: ", res3)
print(output)
print("res4: ", output[res2:res3])
p = 0
for i in range(4):
    p = gwp_text.find("\n")
    gwp_text = gwp_text[p+1:]
p2 = gwp_text[p:].find("\n")
print(re.findall('span title=".*?"', gwp_text[p:p2]))
disposal = ["A1", "A2", "A3", "A1_A3", "A4", "A5", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "C1", "C2", "C3", "C4", "D"]

res2 = gwp_text.find("span title=")
# print("\n \n res2 : ", res2)
print(gwp_text[res2:])
res3 = gwp_text[res:].find("kg CO2")
print("\n \n res3 : ", res3)
print(gwp_text[res3:])
"""
