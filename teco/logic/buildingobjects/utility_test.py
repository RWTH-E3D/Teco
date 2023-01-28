import pandas as pd
import json
import time

from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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


def get_indicator_values(link):
    table = pd.read_html(link)

    df = table[len(table) - 1]  # make this better?

    row = df.loc[df['Indicator'] == 'Global warming potential (GWP)']

    print(row.iloc[0, 0])

    json_dict = {}

    for stage in df.columns[2:]:
        json_dict.update({(str.lower(stage[stage.rfind(' ') + 1:].replace("-", "_")),
                           float((str(row.iloc[0].loc[stage])[:str(row.iloc[0].loc[stage]).find("$")]).lower()))})

    return row.iloc[0].loc['Unit'], json_dict


def TABULA_DE():
    df = pd.read_excel("C:/Users/tayeb/Documents/Teaser+,Teco/TABULA-Analyses_DE-Typology_ResultData.xlsx",
                       sheet_name=0)

    Code_Building = df['Code_Building'][556:1359]
    Code_BuiSysCombi = df['Code_BuiSysCombi'][556:1359]
    Description_SystemType = df['Description_SystemType'][556:1359]
    Year1_Building = df['Year1_Building'][556:1359]
    Year2_Building = df['Year2_Building'][556:1359]

    with open("utilities.json", 'w') as writer:
        writer.write(json.dumps([{Code_Building: {"building_age_group": [Year1_Building, Year2_Building],
                                                  "Code_BuiSysCombi": Code_BuiSysCombi,
                                                  "Description_SystemType": Description_SystemType
                                                  }}
                                 for
                                 Code_Building, Code_BuiSysCombi, Description_SystemType, Year1_Building, Year2_Building
                                 in
                                 zip(Code_Building, Code_BuiSysCombi, Description_SystemType, Year1_Building,
                                     Year2_Building)],
                                ensure_ascii=False))


""" load libraries ???"""


def get_utility_OEKOBAUDAT(utility, bereich=1):
    link = "https://www.oekobaudat.de/no_cache/en/database/search.html"
    driver = webdriver.Firefox()  # seconds
    driver.get(link)
    actions = ActionChains(driver)
    # time.sleep(3)
    wait = WebDriverWait(driver, 10)

    # click on category browser
    button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="c1552"]/s4lca-root-0/div/s4lca-process/div/p-table/div/div[1]/div[2]/p-togglebutton')))
    button.click()

    # click on 8. Building service engineering
    element = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//div[contains(@class, 'ui-treenode-content')]//*[text()[contains(., 'engineering')]]/../../..")))
    actions.move_to_element(element).click().perform()

    # open tree
    element = WebDriverWait(element, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'ui-tree-toggler')))
    actions.move_to_element(element).click().perform()

    # click on Heating
    element = WebDriverWait(element, 10).until(EC.presence_of_element_located(
        (By.XPATH, "//ul[contains(@class, 'ui-treenode-children')]//*[text()[contains(., 'Heating')]]")))
    # element = element.find_element(By.XPATH, '//*[@id="lang-en"]/div[3]/div/div[2]/div/div[2]/s4lca-categories/p-tree/div/div/ul/p-treenode[8]/li/ul/p-treenode[1]/li/div/span[1]')
    actions.move_to_element(element).click().perform()

    # use search bar to find utility object in OEKOBAUDAT
    element = element.find_element(By.XPATH,
                                   f"//div[contains(@id,'bereich{bereich}')]//input[contains(@data-testid,'column-name-input')]")
    element.send_keys(str(utility))

    # make sure the required utility is loaded
    try:
        elementwait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,
                                                                                      f"//div[contains(@id,'bereich{bereich}')]//tr/*//a[contains(text(),'{utility}')]")))
    finally:
        # get attribute link
        element = element.find_element(By.XPATH,
                                       f"//div[contains(@id,'bereich{bereich}')]//tr/*//a[contains(text(),'{utility}')]")
        try:
            utility_link = element.get_attribute('href')
        except NoSuchElementException:
            print("utility not found")
    # click to open page
    # element = element.find_element(By.XPATH, f"//div[contains(@id,'bereich{bereich}')]//tr/*//a[contains(text(),'Liquefied gas tank 2700')]")
    # element.click()

    # open Heating tree?
    time.sleep(1)
    driver.close()
    return utility_link


from teco.logic.buildingobjects.buildingsystems.utility import Utility
from teaser.logic.buildingobjects.building import Building
import teco.data.input.utility_input_json

# TABULA_DE()  # loads to utilities.json
df = pd.read_excel("C:/Users/tayeb/Documents/Teaser+,Teco/TABULA-Analyses_DE-Typology_ResultData.xlsx",
                   sheet_name=0)

Code_Building = df['Code_Building'][556:1359]
Code_BuiSysCombi = df['Code_BuiSysCombi'][556:1359]
Description_SysH = df['Description_SysH'][556:1359]
Description_SysW = df['Description_SysW'][556:1359]
Year1_Building = df['Year1_Building'][556:1359]
Year2_Building = df['Year2_Building'][556:1359]


dict_SysH = {'EPDM foam': 'poor insulation of pipes',  # /good insulation of pipes
             # 'Liquefied gas tank': '???',
             'Underfloor heating': 'heat source ground',  # not sure
             'Gas heat pump': 'air source heat pump',  # not sure
             # 'Woodchip boiler': '???',
             'Pellet boiler': 'woodpellets boiler',  # whats the difference?
             # 'Oil tank': '???',
             'Electric heat pump': 'electrical heatpump'
             # 'Chimney', 'Transfer station', 'Circulating pump'}
             }

dict_SysW = {'Elelectric continuous flow heaters': 'decentral electric: instantaneous water heaters',
             'solar collector': 'solar'
             }

json_dict = {}

for Code_Building, Code_BuiSysCombi, Description_SysH, Description_SysW, Year1_Building, Year2_Building in zip(
        Code_Building, Code_BuiSysCombi, Description_SysH, Description_SysW, Year1_Building, Year2_Building):

    json_dict.update({Code_Building: {"Building_age_group": [Year1_Building, Year2_Building],
                                      "Code_BuiSysCombi": Code_BuiSysCombi,
                                      "Description_SystemHeating": Description_SysH,
                                      "Description_SystemWaterHeating": Description_SysW,
                                      "Utilities": '',
                                      "lca_data": {},
                                      "Unit": ''
                                      }})

    print(Description_SysH)

    # check for gas/oil condensing boiler case
    if 'gas central heating' in Description_SysH:
        if 'condensing boiler' in Description_SysH:
            json_dict[Code_Building]["Utilities"] = 'Gas condensing boiler'
            link = get_utility_OEKOBAUDAT('Gas condensing boiler')
            json_dict[Code_Building]["Unit"], json_dict[Code_Building]["lca_data"] = get_indicator_values(link)

        elif 'low temperature' in Description_SysH:
            json_dict[Code_Building]["Utilities"] = 'Gas low temperature'
            link = get_utility_OEKOBAUDAT('Gas low temperature')
            json_dict[Code_Building]["Unit"], json_dict[Code_Building]["lca_data"] = get_indicator_values(link)

    if 'oil central heating' in Description_SysH:
        if 'condensing boiler' in Description_SysH:
            json_dict[Code_Building]["Utilities"] = 'Oil condensing boiler'
            link = get_utility_OEKOBAUDAT('Oil condensing boiler')
            json_dict[Code_Building]["Unit"], json_dict[Code_Building]["lca_data"] = get_indicator_values(link)
        elif 'low temperature' in Description_SysH:
            json_dict[Code_Building]["Utilities"] = 'Oil low temperature'
            link = get_utility_OEKOBAUDAT('Oil low temperature')
            json_dict[Code_Building]["Unit"], json_dict[Code_Building]["lca_data"] = get_indicator_values(link)

    for utility in dict_SysH:
        if dict_SysH[utility] in Description_SysH:
            json_dict[Code_Building]["Utilities"] = utility
            link = get_utility_OEKOBAUDAT(utility)
            json_dict[Code_Building]["Unit"], json_dict[Code_Building]["lca_data"] = get_indicator_values(link)

    print(Description_SysW)

    for utility in dict_SysW:
        if dict_SysW[utility] in Description_SysW:
            json_dict[Code_Building]["Utilities"] = utility
            link = get_utility_OEKOBAUDAT(utility)
            json_dict[Code_Building]["Unit"], json_dict[Code_Building]["lca_data"] = get_indicator_values(link)

with open("utilities.json", 'w') as writer:
    writer.write(json.dumps(json_dict, ensure_ascii=False))
# utility.add_utilities_to_json()
# divide archetypes from excel sheet according to building age class, then, for each building class, for each archetype, get utility objects
# build utility_input_json for this? based on buildingelement_input_json.py


# use code in utility.add_utilities_to_archetypes() to get gwp values

# store values in en15804lcadata class object


# next_button = driver.find_element(By.CSS_SELECTOR, 'p-treenode.ng-star-inserted:nth-child(9) > li:nth-child(1) > div:nth-child(1) > span:nth-child(3) > span:nth-child(1) > span:nth-child(1)')

# element = driver.find_element(By.CSS_SELECTOR, "p-treenode.ng-star-inserted:nth-child(8)>li:nth-child(1)>div:nth-child(1)>span:nth-child(3)>span:nth-child(1)>span:nth-child(1)")
# element_ = driver.find_element(By.XPATH, "/html/body/div[3]/div/div[2]/div/div[2]/s4lca-categories/p-tree/div/div/ul/p-treenode[8]/li/div/span[3]/span/span")
# print(element_.click())
# print(element.click())

# element = driver.find_element(By.LINK_TEXT, "8. Building service engineering")
# tree = driver.find_element(By.XPATH,
#                           '//*[@id="lang-en"]/div[3]/div/div[2]/div/div[2]/s4lca-categories/p-tree/div/div/ul')
# except:
#        print("error: ")

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
