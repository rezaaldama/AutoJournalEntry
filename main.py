#-------------------------------------------------------------------------------
# Name:        AutoJournal
# Purpose:     Automate Journal (Odoo)
#
# Author:      reza_aldama
#
# Created:     04/06/2020
# Copyright:   (c) Reza Adita Aldama 2020
# Licence:     <None>
#-------------------------------------------------------------------------------

from helium import write
from helium import wait_until
from helium import press
from helium import Text
from helium import Button
from helium import click as helium_click
from helium import start_chrome

from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from time import sleep


def RE(kasbon, mode='re_direct'):
    """ To Automate Reimburse Kasbon """
    project, partner, company = write_kasbon(kasbon, mode)
    edit_kasbon('reimburse')
    edit_kasbon('date')
    submit_kasbon()
    balance_kasbon(mode, project=project)
    print_kasbon(mode, partner, project, company)
def REP(kasbon):
    RE(kasbon, mode='re_indirect')

def ARE(mode=None):
    """ To Automate Reimburse Kasbons """
    update_kasbon()
    update_entries()
    for kasbon in kasbons:
        RE(kasbon, mode)
def AGJ():
    ARE(mode='grossup')
def ABJ():
    ARE(mode='bpjsk')
def ALJ():
    ARE(mode='labour')
def ASJ():
    ARE(mode='salary')
def AMJ():
    ARE(mode='modified')

def CO(kasbon, tax=False, mode='co_direct'):
    """ To Automate Cash Out Kasbon """
    project, partner, company = write_kasbon(kasbon, mode)
    submit_kasbon()
    pay_kasbon(mode, tax, project, company)
    print_kasbon(mode, partner, project, company)
def COP(kasbon, tax=False):
    CO(kasbon, tax, mode='co_indirect')
TAX=True

def RP(kasbon, status, mode='responsibility'):
    """ To Automate Responsibility Kasbon """
    project, partner, company = write_kasbon(kasbon, mode)
    balance_kasbon(mode, status=status)
    print_kasbon(mode, partner, project, company, status)
def RPR(kasbon):
    RP(kasbon, status='receivable')
def RPP(kasbon):
    RP(kasbon, status='payable')
def RPB(kasbon):
    RP(kasbon, status='bank')


def entry(string, xpath=None, t=0):

    if (not xpath):

        if (string == date):
            xpath = "//div[@name='date']"

        elif (string == bank):

            xpath = """//div[contains(@class,'o_required_modifier')]
                        [contains(@name,'journal_id')]"""

        else:
            if (string[:4] == '1181'):
                xpath = """//div[contains(@class,'o_required_modifier')]
                        [contains(@name,'expense_account_id')]"""
            else:
                xpath = """//div[contains(@class,'o_required_modifier')]
                        [contains(@name,'diff_account_id')]"""

    else:

        temp = xpath

        if (string == 'account'):
            xpath = "//tr[@class='o_data_row o_selected_row']/td[1]"

        elif (string == 'partner'):
            xpath = "//tr[@class='o_data_row o_selected_row']/td[2]"

        elif (string == 'label'):
            xpath = "//tr[@class='o_data_row o_selected_row']/td[3]"

        elif (string == 'project'):
            xpath = "//tr[@class='o_data_row o_selected_row']/td[5]"

        elif (string == 'nominal'):
            xpath = "//tr[@class='o_data_row o_selected_row']/td[9]"

        string = temp

    xpath = driver.find_element_by_xpath(xpath + '//input')

    xpath.click()
    xpath.send_keys(Keys.CONTROL + 'a')
    xpath.send_keys(string)
    sleep(0.5+t)
    if (t > 0):
        press(Keys.ENTER)
        sleep(0.5)

def click(string, t=0):

    try:
        driver.find_element_by_xpath("//*[text()='" + string + "']").click()

    except:
        try:
            driver.find_element_by_partial_link_text(string).click()
        except:
            try:
                driver.find_element_by_class_name(string).click()
            except:
                helium_click(string)

    sleep(0.35+t)

def wait(string, mode=False):

    if mode:
        wait_until(Button(string).exists,999)
    else:
        wait_until(Text(string).exists,999)

    sleep(0.35+t)
button = True


kasbons = []
def update_kasbon():
    with open("kasbons.txt") as f:
        for line in f:
            line_split = line.split("\n")
            kasbons.append(line_split[0])

entries = {}
def update_entries(
    status=None, partner=None, label=None, project=None, nominal=None):

    if status == 'receivable':
        entries[len(entries)] = ['1150-999', partner, label, project, nominal]
    elif status == 'payable':
        entries[len(entries)] = ['2170-009', partner, label, project, -nominal]

    elif not status:
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

                    click('Add an item', t=1+t)

                    entry('account', entries['account'][n], t=0.65)

                    if (entries['partner'][n] != '0'):
                        entry('partner', entries['partner'][n], t=0.65)

                    entry('label', entries['description'][n])

                    entry('project', project, t=0.65)

                    if (int(entries[project][n]) < 0):
                        entry('nominal', str(entries[project][n])[1:])
                        press(Keys.TAB)
                        write('0')
                    elif (int(entries[project][n]) > 0):
                        entry('nominal', '0')
                        press(Keys.TAB)
                        write(entries[project][n])

            except:
                break

    else:

        for n in entries:

            click('Add an item', t=1+t)

            entry('account', entries[n][0], t=0.65)

            entry('partner', entries[n][1], t=0.65)

            entry('label', entries[n][2])

            entry('project', entries[n][3], t=0.65)

            if (int(entries[n][4]) < 0):
                entry('nominal', str(entries[n][4])[1:])
                press(Keys.TAB)
                write('0')
            elif (int(entries[n][4]) > 0):
                entry('nominal','0')
                press(Keys.TAB)
                write(entries[n][4])

        entries.clear()
        click('Post', t=1.5+t)
        try:
            click('Save')
        except:
            wait('Edit', button)
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

def AGS():
    AGL(mode='salary')


def write_kasbon(kasbon, mode):

    if (mode != 'responsibility'):
        driver.find_element_by_xpath("//a[@data-menu='185']/span").click()
    else:
        driver.find_element_by_xpath("//a[@data-menu='186']/span").click()
    wait('Import', button)

    driver.find_element_by_class_name("o_searchview_input").click()
    sleep(0.25+t)
    write(kasbon)
    sleep(0.5+t)
    press(Keys.ENTER)
    sleep(1+t)

    kasbon = driver.find_element_by_xpath("//tr[@class='o_data_row']/td[2]")
    if (kasbon.text[-2:] == '20') or  (kasbon.text[-2:] == '21'):
        kasbon.click()

    wait('Edit', button)

    project = driver.find_element_by_name('project_id').text
    partner = driver.find_element_by_name('employee_id').text
    company = driver.find_element_by_css_selector(".o_switch_company_menu").text

    return project[1:8], partner, company

def edit_kasbon(mode):

    click('Edit')
    if (mode == 'reimburse'):
        click('Reimburse')
    elif (mode == 'date'):
        entry(date)
    click('Save')

def submit_kasbon():

    click('Submit')
    wait('Kasbon Progress')
    entry(date)
    click('OK')

def pay_kasbon(mode, tax, project, company):

    wait('Pay and Post', button)
    if (tax):
        click('Edit')
        wait('Edit', button)
    click('Pay and Post')
    wait('Kasbon Progress')

    entry(date)
    entry(bank, t = 0.75+t)
    if (company == 'PT SUA Sby'):
        if (project[0] == 'K'):
            entry('1181-003', t = 0.75+t)
        elif (project[0] == 'B'):
            entry('1181-002', t = 0.75+t)
    elif (project[0] != 'K'):
        entry('1181-001', t = 0.75+t)
    click('OK')

def balance_kasbon(mode, project=None, status=None):

    wait('Report Balancing', button)
    click('Edit')
    for n in range(len(driver.find_elements_by_name('to_pay'))):

        if ((mode == 'grossup') or (mode == 'labour')) and (project[0] != 'K'):
            driver.find_elements_by_css_selector("td:nth-child(4)")[n].click()
            sleep(0.75+t)
            write('6100-010')
            sleep(0.75)
            press(Keys.ENTER)
            sleep(0.75)

        elif (mode == 'modified'):
            driver.find_elements_by_css_selector("td:nth-child(4)")[n].click()
            sleep(0.75+t)
            write('2170-009')
            sleep(0.75)
            press(Keys.ENTER)
            sleep(0.75)

        driver.find_elements_by_css_selector("td:nth-child(9)")[n].click()
        sleep(0.75+t)
        write(driver.find_elements_by_name('to_pay')[n].text)
        sleep(0.25)

    if (mode != 'responsibility'):
        click('Save')

    wait('Edit', button)

    click('Report Balancing')
    wait('Kasbon Progress')
    entry(date)
    click('OK')

    wait('Post Balance', button)
    click('Post Balance')
    wait('Kasbon Progress')
    entry(date)
    entry(bank, t = 0.75+t)
    if (mode == 'responsibility'):
        if (status == 'receivable'):
            entry('1150-999', t = 0.75+t)
        elif (status == 'payable'):
            entry('2170-009', t = 0.75+t)
        elif (status == 'bank'):
            try:
                entry('1112-101', t = 0.75+t)
            except:
                pass
    click('OK')

def print_kasbon(mode, partner, project, company, status=None):

    WebDriverWait(driver,999).until(EC.presence_of_element_located(
        (By.XPATH, "//body[@class='o_web_client']")))

    try:

        if (mode == 'co_indirect' or
            mode == 're_indirect' or
            mode == 'responsibility'):

            if (mode == 'co_indirect'):
                nominal = driver.find_element_by_name('pay_total').text
            elif (mode == 're_indirect'):
                nominal = driver.find_element_by_name('realize_total').text
            elif (mode == 'responsibility'):
                nominal = driver.find_element_by_name('difference').text
            nominal = abs(int(nominal[:-3].replace(',','')))

        sleep(0.5)

        click('Entries')
        wait('Journal Entry')
        click(date)
        wait('Accounting Documents')
        click(journal)
        wait('Reference')

    except:
        wait('Reverse Entry', button)

    label = driver.find_element_by_name('ref').text

    if (mode == 'responsibility'):

        if (status != 'bank') and company == 'PT SUA Jkt':
            update_entries(status, partner, label, project, nominal)
        else:
            pass

    elif ((mode != 're_direct') or (entries)):

        if ((mode == 'labour' or mode == 'salary') and
            (not (project in entries))):
            pass

        else:

            try:
                click('Edit')
                click('Cancel Entry', 1.5+t*2)
            except:
                wait('Post', button)
                sleep(1)

            if (journal == 'BOK'):
                bank = 'BANK PERMATA SYARIAH'
                if (company == 'PT SUA Jkt'):
                    click('01-1112-113')
                elif (company == 'PT SUA Sby'):
                    click('02-1112-113')
            elif (journal == 'BCK'):
                bank = 'BANK BCA (JKT)'
                if (company == 'PT SUA Jkt'):
                    click('01-1112-101')
                elif (company == 'PT SUA Sby'):
                    click('02-1112-101')

            if (mode == 'co_direct'):
                entry('project', project, t=0.65)
            elif (mode == 're_indirect' or mode == 'co_indirect'):
                entry('account', '2170-009', t=0.65)
                if (mode == 'co_indirect'):
                    entry('project', project, t=0.65)
                update_entries('payable', partner, label, project, nominal)
            elif (mode == 'grossup'):
                entry('account', '2133-001', t=0.65)
            elif (mode == 'bpjsk'):
                entry('account', '1121-001', t=0.65)
                entry('partner', partner, t=0.35)
                entry('label', label)
                entry('project', project, t=0.65)
            elif (mode == 'labour' or mode == 'salary'):
                entry('nominal', '0')
                press(Keys.TAB)
                write(entries[project][-1])
                auto_entries(project)
            elif (mode == 'modified'):
                entry('label', label)

            if (mode == 'bpjsk' or mode == 'modified'):
                wait('Cancel Entry', button)
                sleep(1)
            elif ((mode == 'co_direct' or mode == 're_direct') and
                (entries)):
                return
            else:
                click('Post', 1.5)
                wait('Cancel Entry', button)
                sleep(0.5)
                try:
                    click('Save')
                except:
                    wait('Edit', button)

    if (mode != 'grossup' and mode != 'labour') or (company == 'PT SUA Sby'):
            click('Print', 0.25)
            click('Journal Entries')
            print(entries)

    print('Current journal date: '+ date)

    WebDriverWait(driver,999).until(EC.presence_of_element_located(
        (By.XPATH, "//body[@class='o_web_client']")))
    sleep(1+t)
