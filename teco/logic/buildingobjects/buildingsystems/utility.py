import pandas as pd
from sympy.codegen.cnodes import static
from teaser.logic.archetypebuildings.tabula.de.singlefamilyhouse import SingleFamilyHouse
from teaser.logic.archetypebuildings.tabula.de.apartmentblock import ApartmentBlock
from teaser.logic.archetypebuildings.tabula.de.multifamilyhouse import MultiFamilyHouse
from teaser.logic.archetypebuildings.tabula.de.terracedhouse import TerracedHouse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import time


class Utility(object):
    """Utility Class



        Parameters
        ----------

        parent: Building()
            The parent class of this object, the Building the Utility belongs to.
            Allows for better control of hierarchical structures.
            (default: None)

        Attributes
        ----------
        """

    def __init__(self, parent=None):
        """Constructor for Utility
        """

        self.parent = parent

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, value):
        from teaser.logic.buildingobjects.building import Building
        import inspect

        if inspect.isclass(Building):
            self.__parent = value

    def get_utility_link(self, bereich, utility):
        """

        Parameters
        ----------
        bereich: integer

        utility: string

        Returns
        -------

        """

        link = "https://www.oekobaudat.de/no_cache/en/database/search.html"
        driver = webdriver.Firefox()

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
            (By.XPATH,
             "//div[contains(@class, 'ui-treenode-content')]//*[text()[contains(., 'engineering')]]/../../..")))
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
        elementwait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,
                                       f"//div[contains(@id,'bereich{bereich}')]//tr/*//a[contains(text(),'Liquefied gas tank 2700')]")))

        # get attribute link
        element = element.find_element(By.XPATH,
                                       f"//div[contains(@id,'bereich{bereich}')]//tr/*//a[contains(text(),'Liquefied gas tank 2700')]")
        utility_link = element.get_attribute('href')

        # click to open page
        # element = element.find_element(By.XPATH, f"//div[contains(@id,'bereich{bereich}')]//tr/*//a[contains(text(),'Liquefied gas tank 2700')]")
        # element.click()

        # open Heating tree?
        time.sleep(10)
        driver.close()

        return utility_link


    def add_utilities_to_archetypes(self):

        # building needs to be german TABULA archetype?

        # for each YoC Class, for each archetype?
        # look in TABULA Webtool, on the right details about buildings, search those in Ökobaudat and get gwp from there

        #if self.parent.year_of_construction < 1860:
        #    if type(self) is SingleFamilyHouse:
        #        self.parent.add_lca_data_template("7d027677-b2e3-40dd-a4b1-91bd8f7383d5", 1)

        #        self.parent.utilities += self.parent.lca_data

        utility = "gas tank 2700 l"
        link = self.get_utility_link(1, utility)

        table = pd.read_html(link)

        df = table[len(table) - 1]  # make this better?

        row = df.loc[df['Indicator'] == 'Global warming potential (GWP)']

        print(row.iloc[0, 0])

        unit = row.iloc[0].loc['Unit']

        for stage in df.columns[2:]:
            print(stage)
            print(str(row.iloc[0].loc[stage])[:str(row.iloc[0].loc[stage]).find("$")])

        # save in en15804lcadata class object

        return
