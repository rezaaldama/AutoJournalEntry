#-------------------------------------------------------------------------------
# Name:        AutoJournal
# Purpose:     Automate Kasbon/GL Journal (Odoo)
#
# Author:      rezaaldama
#
# Created:     04/06/2020
# Copyright:   <None>
# Licence:     <None>
#-------------------------------------------------------------------------------

from helium import write
from helium import wait_until
from helium import press
from helium import Text
from helium import Button
from helium import click as h_click
from helium import start_chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep

#-------------------------------------------------------------------------------

TAX = True

REIMBURSE = 10
REIMBURSE_PAYABLE = 11
GROSSUP = 12
BPJS = 13
LABOUR = 14
SALARY = 15
OTHERS = 16

def RE(kasbon, TAX=False, mode=REIMBURSE):
    """ To Automate Reimburse Kasbon """

    project, partner, company = write_kasbon(kasbon, mode)
    edit_kasbon(mode)
    submit_kasbon()
    balance_kasbon(mode, project = project)
    print_kasbon(mode, partner, project, company, TAX)

def REP(kasbon, TAX=False): RE(kasbon, TAX, mode=REIMBURSE_PAYABLE)

def ARE(mode=None):
    """ To Automate Reimburse Kasbons """

    update_kasbon()
    update_entries()

    for kasbon in kasbons:
        RE(kasbon, mode=mode)

def AGJ(): ARE(mode=GROSSUP)
def ABJ(): ARE(mode=BPJS)
def ALJ(): ARE(mode=LABOUR)
def ASJ(): ARE(mode=SALARY)
def AOJ(): ARE(mode=OTHERS)

#-------------------------------------------------------------------------------

CASHOUT = 21
CASHOUT_PAYABLE = 22

def CO(kasbon, TAX=False, mode=CASHOUT):
    """ To Automate Cash Out Kasbon """

    project, partner, company = write_kasbon(kasbon, mode)
    submit_kasbon()
    pay_kasbon(mode, project, company, TAX)
    print_kasbon(mode, partner, project, company, TAX)

def COP(kasbon, TAX=False): CO(kasbon, TAX, mode=CASHOUT_PAYABLE)

#-------------------------------------------------------------------------------

BALANCE = 30
BALANCE_RECEIVABLE = 31
BALANCE_PAYABLE = 32

def RPB(kasbon, mode=BALANCE):
    """ To Automate Responsibility Kasbon """

    project, partner, company = write_kasbon(kasbon, mode)
    balance_kasbon(mode)
    print_kasbon(mode, partner, project, company)

def RPR(kasbon): RPB(kasbon, BALANCE_RECEIVABLE)
def RPP(kasbon): RPB(kasbon, BALANCE_PAYABLE)

#-------------------------------------------------------------------------------

BUTTON = ["Edit", "Import", "Report Balancing", "Post Balance", "Reverse Entry",
          "Post", "Cancel Entry", "Entries", "Discard", "Journal Entries"]

def wait(string=None):

    if string in BUTTON:

        if (string == "Post" or
            string == "Cancel Entry" or
            string == 'Import' or
            string == 'Entries' or
            string == 'Discard' or
            string == 'Journal Entries' or
            string == 'Add an Item'):

            sleep(1)

            WebDriverWait(driver,999).until(EC.presence_of_element_located(
                (By.XPATH, "//body[@class='o_web_client']")))

        wait_until(Button(string).exists,999)

    else:
        wait_until(Text(string).exists,999)

def click(string):

    try:
        driver.find_element_by_xpath("//*[text()='" + string + "']").click()

    except:
        try:
            driver.find_element_by_partial_link_text(string).click()
        except:
            try:
                driver.find_element_by_class_name(string).click()
            except:
                h_click(string)

#-------------------------------------------------------------------------------

ACCOUNT = 1
PARTNER = 2
LABEL = 3
PROJECT = 4
NOMINAL = 5

DIFF_ACCOUNT = 6

def entry(mode, string=None, t=0):

    if not string:

        if mode == DATE:
            xpath = "//div[@name='date']//input"

        elif mode == BANK:
            xpath = """//div[contains(@class,'o_required_modifier')]
                        [contains(@name,'journal_id')]//input"""

        else:
            xpath = "//input[@class='o_searchview_input']"

        string = mode

    else:

        if mode == DIFF_ACCOUNT:
            try:
                xpath = """//div[contains(@class,'o_required_modifier')]
                        [contains(@name,'expense_account_id')]//input"""
            except:
                xpath = """//div[contains(@class,'o_required_modifier')]
                        [contains(@name,'diff_account_id')]//input"""

        elif mode == ACCOUNT:
            xpath = "//tr[@class='o_data_row o_selected_row']/td[1]//input"

        elif mode == PARTNER:
            xpath = "//tr[@class='o_data_row o_selected_row']/td[2]//input"

        elif mode == LABEL:
            xpath = "//tr[@class='o_data_row o_selected_row']/td[3]//input"

        elif mode == PROJECT:
            xpath = "//tr[@class='o_data_row o_selected_row']/td[5]//input"

        elif mode == NOMINAL:
            xpath = "//tr[@class='o_data_row o_selected_row']/td[9]//input"

    xpath = driver.find_element_by_xpath(xpath)

    xpath.click()
    xpath.send_keys(Keys.CONTROL + 'a')
    xpath.send_keys(string)
    sleep(0.5+t)

    if t > 0:
        xpath.send_keys(Keys.ENTER)
        sleep(0.5)

kasbons = []
def update_kasbon():
    with open("kasbons.txt") as f:
        for line in f:
            line_split = line.split("\n")
            kasbons.append(line_split[0])

entries = {}
def update_entries(
    mode=None, partner=None, label=None, project=None, nominal=None):

    if mode == BALANCE_RECEIVABLE:
        entries[len(entries)] = ['1150-999', partner, label, project, nominal]

    elif mode == BALANCE_PAYABLE:
        entries[len(entries)] = ['2170-009', partner, label, project, -nominal]

    elif not mode:
        with open("journal_entries.txt") as f:
            for line in f:
                line_split = line.split("\t")
                line_split = [i.strip() for i in line_split]
                entries[line_split[0]] = line_split[1:-1]

def auto_entries(project=None, mode=False, entries=entries):
    """ To Automate Entry Process """

    if (not mode):

        for n in range(len(entries[project])):

            try:

                if (((entries[project][n] != '0')
                    and n != (len(entries[project])-1))
                    and (project != 'account' and
                        project != 'description' and
                        project != 'partner')):

                    click('Add an item')
                    wait('Discard')

                    entry(ACCOUNT, entries['account'][n], t=1+t)

                    if (entries['partner'][n] != '0'):
                        entry(PARTNER, entries['partner'][n], t=1+t)

                    entry(LABEL, entries['description'][n])

                    entry(PROJECT, project, t=1+t)

                    if (int(entries[project][n]) < 0):
                        entry(NOMINAL, str(entries[project][n])[1:])
                        press(Keys.TAB)
                        write('0')
                    elif (int(entries[project][n]) > 0):
                        entry(NOMINAL, '0')
                        press(Keys.TAB)
                        write(entries[project][n])

            except:
                break

    else:

        for n in entries:

            click('Add an item')
            wait('Discard')

            entry(ACCOUNT, entries[n][0], t=1+t)

            entry(PARTNER, entries[n][1], t=1+t)

            entry(LABEL, entries[n][2])

            entry(PROJECT, entries[n][3], t=1+t)

            if (int(entries[n][4]) < 0):
                entry(NOMINAL, str(entries[n][4])[1:])
                press(Keys.TAB)
                write('0')
            elif (int(entries[n][4]) > 0):
                entry(NOMINAL,'0')
                press(Keys.TAB)
                write(entries[n][4])

        entries.clear()
        click('Post')
        wait('Cancel Entry')

        try:
            click('Save')

        except:
            wait('Edit')

        click('Print')
        click('Journal Entries')

def AGL(mode=None):

    if (not entries):
        update_entries()

    if (not mode):
        auto_entries(mode=True)
    else:
        for project in entries:
            auto_entries(project)

def AGS(): AGL(mode=SALARY)

#-------------------------------------------------------------------------------

def write_kasbon(kasbon, mode):

    if (mode == BALANCE_RECEIVABLE or
        mode == BALANCE_PAYABLE or
        mode == BALANCE):
        driver.find_element_by_xpath("//a[@data-menu='186']/span").click()
    else:
        driver.find_element_by_xpath("//a[@data-menu='185']/span").click()

    wait('Import')

    entry(kasbon, t=0.5+t)

    temp = str(kasbon)
    try:
        kasbon = driver.find_element_by_xpath("//tr[@class='o_data_row']/td[2]")
        if len(temp) != 15:
            if (((kasbon.text[1:5] == temp) or (kasbon.text[:5] == temp)) and
                (kasbon.text[-2:] == '21' or kasbon.text[-2:] == '20')):
                kasbon.click()
            else:
                print("Warning: Check kasbon's number!")
        else:
            kasbon.click()
    except:
        pass

    wait('Edit')

    project = driver.find_element_by_name('project_id').text
    partner = driver.find_element_by_name('employee_id').text
    company = driver.find_element_by_css_selector(".o_switch_company_menu").text

    return project[1:8], partner, company

def edit_kasbon(mode):

    click('Edit')

    if (mode == SALARY or mode == GROSSUP):
        entry(DATE)

    click('Reimburse')
    click('Save')

def submit_kasbon():

    click('Submit')
    wait('Kasbon Progress')
    entry(DATE)
    click('OK')

def pay_kasbon(mode, project, company, TAX):

    wait('Pay and Post')

    if (TAX):
        click('Edit')
        wait('Edit')

    click('Pay and Post')
    wait('Kasbon Progress')
    entry(DATE)
    entry(BANK, t=0.5+t)
    if (company == 'PT SUA Sby'):
        if (project[0] == 'K'):
            entry(DIFF_ACCOUNT, '1181-003', t=0.5+t)
        elif (project[0] == 'B'):
            entry(DIFF_ACCOUNT, '1181-002', t=0.5+t)
    elif (project[0] != 'K'):
        entry(DIFF_ACCOUNT, '1181-001', t=0.5+t)
    click('OK')

def balance_kasbon(mode, project=None):

    wait('Report Balancing')
    click('Edit')

    for n in range(len(driver.find_elements_by_name('to_pay'))):

        if ((mode == GROSSUP or mode == LABOUR)
            and (project[0] != 'K')):
            driver.find_elements_by_css_selector("td:nth-child(4)")[n].click()
            sleep(1+t)
            write('6100-010')
            sleep(1+t)
            press(Keys.ENTER)

        driver.find_elements_by_css_selector("td:nth-child(9)")[n].click()
        sleep(1+t)
        write(driver.find_elements_by_name('to_pay')[n].text)

    if (mode != BALANCE_RECEIVABLE and
        mode != BALANCE_PAYABLE and
        mode != BALANCE):
        click('Save')
    wait('Edit')

    click('Report Balancing')
    wait('Kasbon Progress')
    entry(DATE)
    click('OK')

    wait('Post Balance')
    click('Post Balance')
    wait('Kasbon Progress')
    entry(DATE)
    entry(BANK, t=0.5+t)
    if (mode == BALANCE_RECEIVABLE):
        entry(DIFF_ACCOUNT,'1150-999', t=0.5+t)
    elif (mode == BALANCE_PAYABLE):
        entry(DIFF_ACCOUNT,'2170-009', t=0.5+t)
    elif (mode == BALANCE):
        entry(DIFF_ACCOUNT,'1112-101', t=0.5+t)
    click('OK')

def print_kasbon(mode, partner, project, company, TAX=False):

    wait('Entries')

    try:
        if (mode == CASHOUT_PAYABLE or
            mode == REIMBURSE_PAYABLE or
            mode == BALANCE_RECEIVABLE or
            mode == BALANCE_PAYABLE):

            if mode == CASHOUT_PAYABLE:
                nominal = driver.find_element_by_name('pay_total').text
            elif mode == REIMBURSE_PAYABLE:
                nominal = driver.find_element_by_name('realize_total').text
            else:
                nominal = driver.find_element_by_name('difference').text
            nominal = abs(int(nominal[:-3].replace(',','')))

        click('Entries')
        wait('Journal Entry')
        click(DATE)
        wait('Accounting Documents')
        click(JOURNAL)
        wait('Reference')

    except:
        wait('Reverse Entry')

    label = driver.find_element_by_name('ref').text

    if (mode == BALANCE_RECEIVABLE or mode == BALANCE_PAYABLE):
        if (company == 'PT SUA Jkt'):
            update_entries(mode, partner, label, project, nominal)
        else:
            pass

    elif (mode != REIMBURSE or entries):

        if ((mode == LABOUR or mode == SALARY) and
            (not (project in entries))):
            pass

        else:

            click('Edit')
            click('Cancel Entry')
            wait('Post')
            wait('Add an Item')

            try:
                if (JOURNAL == 'BOK'):
                    if (company == 'PT SUA Jkt'):
                        click('01-1112-113')
                    elif (company == 'PT SUA Sby'):
                        click('02-1112-113')

                elif (JOURNAL == 'BCK'):
                    if (company == 'PT SUA Jkt'):
                        click('01-1112-101')
                    elif (company == 'PT SUA Sby'):
                        click('02-1112-101')

                if (mode == CASHOUT):
                    entry(PROJECT, project, t=1+t)

                elif (mode == REIMBURSE_PAYABLE or mode == CASHOUT_PAYABLE):
                    entry(ACCOUNT, '2170-009', t=1+t)
                    if (mode == CASHOUT_PAYABLE):
                        entry(PROJECT, project, t=1+t)
                    update_entries(BALANCE_PAYABLE, partner, label, project, nominal)

                elif (mode == GROSSUP):
                    entry(ACCOUNT, '2133-001', t=1+t)

                elif (mode == BPJS):
                    entry(ACCOUNT, '2170-009', t=1+t)
                    entry(PARTNER, 'GUNAKARYANA', t=1+t)
                    entry(LABEL, DESC)
                    entry(PROJECT ,'HO-21-0', t=1+t)

                elif (mode == LABOUR or mode == SALARY):
                    entry(NOMINAL, '0')
                    press(Keys.TAB)
                    write(entries[project][-1])
                    auto_entries(project)

                elif (mode == OTHERS):
                    entry(LABEL, DESC)
                    entry(PROJECT ,'HO-21-0', t=1+t)

                if (mode == BPJS or mode == OTHERS):
                    if (project[1:9] == 'HO-21-00'):
                        AGL()
                    wait('Cancel Entry')

                elif ((mode == CASHOUT or mode == REIMBURSE or mode == BALANCE)
                    and (entries)) or TAX:
                    return

                else:
                    click('Post')
                    wait('Cancel Entry')
                    click('Save')

            except:
                wait('Edit')

    if ((mode != GROSSUP and mode != LABOUR) or company == 'PT SUA Sby'):
            click('Print')
            click('Journal Entries')
            print(entries)

    print('Current journal date: '+ DATE)
    wait('Post')
