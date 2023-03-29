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


def get_indicator_values(link, indicator='Global warming potential (GWP)'):
    table = pd.read_html(link)

    df = table[len(table) - 1]  # make this better?

    row = df.loc[df['Indicator'] == indicator]

    json_dict_vals = {}

    for stage in df.columns[2:]:
        json_dict_vals.update({(str.lower(stage[stage.rfind(' ') + 1:].replace("-", "_")),
                           float((str(row.iloc[0].loc[stage])[:str(row.iloc[0].loc[stage]).find("$")]).lower()))})

    return row.iloc[0].loc['Unit'], json_dict_vals


def get_all_indicators(link):
    table = pd.read_html(link)

    df = table[len(table) - 2]  # Indicators of life cycle

    json_all = {}

    for i in range(len(df)):

        json_dict_vals = {}
        row = df.loc[i:]
        if row.iloc[0].loc['Unit'] == 'm3':
            json_dict_vals.update({("unit", 'm^3')})
        else:
            json_dict_vals.update({("unit", row.iloc[0].loc['Unit'])})

        for stage in df.columns[3:]:
            json_dict_vals.update({(str.lower(stage[stage.rfind(' ') + 1:].replace("-", "_")),
                               float((str(row.iloc[0].loc[stage])[:str(row.iloc[0].loc[stage]).find("$")]).lower()))})

        name = row.iloc[0, 0]
        name = name[name.find('(') + 1:name.find(')')].lower()
        data = {name: json_dict_vals}

        json_all.update(data)

    df = table[len(table) - 1]  # Environmental Impact Indicators

    for i in range(len(df)):

        json_dict_vals = {}
        row = df.loc[i:]

        json_dict_vals.update({("unit", row.iloc[0].loc['Unit'])})

        for stage in df.columns[2:]:
            json_dict_vals.update({(str.lower(stage[stage.rfind(' ') + 1:].replace("-", "_")),
                               float((str(row.iloc[0].loc[stage])[:str(row.iloc[0].loc[stage]).find("$")]).lower()))})

        name = row.iloc[0, 0]
        name = name[name.find('(') + 1:name.find(')')].lower()
        data = {name: json_dict_vals}

        json_all.update(data)

    return json_all


def get_utility_OEKOBAUDAT(driver, utility, bereich=1):

    # use search bar to find utility object in OEKOBAUDAT
    searchbox = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.XPATH, f"//div[contains(@id,'bereich{bereich}')]//input[contains(@data-testid,'column-name-input')]")))
    #element = driver.find_element(By.XPATH, f"//div[contains(@id,'bereich{bereich}')]//input[contains(@data-testid,'column-name-input')]")
    searchbox.send_keys(str(utility))

    # make sure the required utility is loaded
    try:
        elementwait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,
                                                                                      f"//div[contains(@id,'bereich{bereich}')]//tr/*//a[contains(text(),'{utility}')]")))
    finally:
        # get attribute link
        element = searchbox.find_element(By.XPATH,
                                       f"//div[contains(@id,'bereich{bereich}')]//tr/*//a[contains(text(),'{utility}')]")
        try:
            utility_link = element.get_attribute('href')
        except NoSuchElementException:
            print("utility not found")
            utility_link = None
            pass

    searchbox.clear()

    return utility_link


# TABULA_DE()  # loads to utilities_old.json
df = pd.read_excel("C:/Users/tayeb/Documents/Teaser+,Teco/TABULA-Analyses_DE-Typology_ResultData.xlsx",
                   sheet_name=0)

a = 556
b = 1359
Code_BuildingVariant = df['Code_BuildingVariant'][a:b]
Code_BuiSysCombi = df['Code_BuiSysCombi'][a:b]
Description_SysH = df['Description_SysH'][a:b]
Description_SysW = df['Description_SysW'][a:b]
Year1_Building = df['Year1_Building'][a:b]
Year2_Building = df['Year2_Building'][a:b]

dict_SysH = {'EPDM foam': 'poor insulation of pipes',  # /good insulation of pipes
             # 'Liquefied gas tank': '???',
             'Underfloor heating system copper (100mm distance)': 'heat source ground',
             # not sure if its ths same thing (took the underfloor heating with the biggest gwp)
             'Gas heat pump (air)': 'air source heat pump',  # not sure
             # 'Woodchip boiler': '???',
             'Pellet boiler': 'woodpellets boiler',  # whats the difference between woodchip and pellet?
             # 'Oil tank': '???',
             'Electric heat pump (brine-water, geothermal probe)': 'electrical heatpump, heat source ground', # geothermal probe has bigger gwp than collector
             'Electric heat pump (water-water)': 'electrical heatpump, heat source water',
             'Electric heat pump (air-water)': 'electrical heatpump, heat source external air',
             # 'Chimney',
             # 'Circulating pump'}
             }

dict_SysW = {'Electric continuous flow heater (21 kW)': 'decentral electric: instantaneous water heaters',
             # 'District heating transfer station': 'district heating, transfer station'  (not in DE Tabula)
             # 'solar collector': 'solar'
             }

json_dict = {}

capacities1 = {'SFH': ' < 20 kW',
               'TH': ' < 20 kW',
               'MFH': ' 20-120 kW',
               'AB': ' 20-120 kW'  # or '120-400 kW'
               }

# Electric heat pump (brine-water)/(water-water)
capacities2 = {'SFH': ' 10 kW',
               'TH': ' 20 kW',
               'MFH': ' 20 kW',
               'AB': ' 70 kW'
               }

# Electric heat pump (air-water)
capacities3 = {'SFH': ' 7 kW',
               'TH': ' 10 kW',
               'MFH': ' 10 kW',
               'AB': ' 14 kW'
               }

driver = webdriver.Firefox()
driver.get("https://www.oekobaudat.de/no_cache/en/database/search.html")

bereich = 1

# use classification bar to filter down to heating objects in OEKOBAUDAT
classification_box = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
    (By.XPATH, f"//div[contains(@id,'bereich{bereich}')]//input[contains(@data-testid,'column-classification-input')]")))

classification_box.send_keys("Heizung")


for Code_BuildingVariant, Code_BuiSysCombi, Description_SysH, Description_SysW, Year1_Building, Year2_Building in zip(
        Code_BuildingVariant, Code_BuiSysCombi, Description_SysH, Description_SysW, Year1_Building, Year2_Building):

    try:
        # make sure no two archetypes have the same name:
        if Code_BuildingVariant == 0:
            break
        if Code_BuildingVariant in json_dict:
            i = 0
            while Code_BuildingVariant + "." + str(i) in json_dict:
                i += 1
            Code_BuildingVariant += "." + str(i)

        json_dict[Code_BuildingVariant] = {"Building_age_group": [Year1_Building, Year2_Building],
                                           "Code_BuiSysCombi": Code_BuiSysCombi,
                                           "Description_SystemHeating": Description_SysH,
                                           "Description_SystemWaterHeating": Description_SysW,
                                           "Utilities": {}
                                           }

        # building type: SFH, MFH, TH, AB
        Building_type = Code_BuildingVariant[
                        Code_BuildingVariant.find('.', 4) + 1: Code_BuildingVariant.find('.', Code_BuildingVariant.find('.', 4) + 1)]

        # check for gas/oil condensing boiler/low temperature cases:
        if 'gas central heating' in Description_SysH:
            if 'condensing boiler' in Description_SysH:

                link = get_utility_OEKOBAUDAT(driver, 'Gas condensing boiler' + capacities1[Building_type])

                json_dict[Code_BuildingVariant]["Utilities"]['Gas condensing boiler' + capacities1[Building_type]] = (get_all_indicators(link))

                #json_dict[Code_BuildingVariant]["Utilities"].append({"name": 'Gas condensing boiler', "capacity": capacities1[Building_type], "lca_data":[{"name": "gwp", "data": gwp_data, "gwp Unit": unit_gwp}]})

            elif 'low temperature' in Description_SysH:

                link = get_utility_OEKOBAUDAT(driver, 'Gas low temperature boiler' + capacities1[Building_type])

                json_dict[Code_BuildingVariant]["Utilities"]['Gas low temperature boiler' + capacities1[Building_type]] = (get_all_indicators(link))

        if 'oil central heating' in Description_SysH:
            if 'condensing boiler' in Description_SysH:

                link = get_utility_OEKOBAUDAT(driver, 'Oil condensing boiler' + capacities1[Building_type])

                json_dict[Code_BuildingVariant]["Utilities"]['Oil condensing boiler' + capacities1[Building_type]] = (get_all_indicators(link))

            elif 'low temperature' in Description_SysH:

                link = get_utility_OEKOBAUDAT(driver, 'Oil low temperature boiler' + capacities1[Building_type])

                json_dict[Code_BuildingVariant]["Utilities"]['Oil low temperature boiler' + capacities1[Building_type]] = (get_all_indicators(link))

        # search for the rest of the utilities:
        for utility in dict_SysH:
            if dict_SysH[utility] in Description_SysH:
                capacity = ''
                if utility == 'Pellet boiler':
                     capacity = capacities1[Building_type]

                if 'Electric heat pump' in utility:
                    if '(air-water)' in utility:
                        capacity = capacities3[Building_type]
                    else:
                        capacity = capacities2[Building_type]

                try:
                    link = get_utility_OEKOBAUDAT(driver, utility)

                    json_dict[Code_BuildingVariant]["Utilities"][utility + capacity] = (get_all_indicators(link))

                except Exception as e:

                    print(f'lca data for {utility} not found: ' + str(e))

                pass

        """
        for utility in dict_SysW:
            if dict_SysW[utility] in Description_SysW:
                link = get_utility_OEKOBAUDAT(driver, utility)
                json_dict[Code_BuildingVariant]["Utilities"] = (get_all_indicators(link))
                
                json_dict[Code_BuildingVariant]["Utilities"]["name"] = utility
        """
    except Exception as e:
        print("ERROR: ", e, " in:")
        print(Code_BuildingVariant)
        pass

with open("../../data/input/inputdata/utilities.json", 'w') as writer:
    writer.write(json.dumps(json_dict, ensure_ascii=False))

time.sleep(1)
driver.close()