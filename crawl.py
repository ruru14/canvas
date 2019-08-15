from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import WebDriverWait
from util import info
import os
import util.logger as logger
import dbConnect.dbConnector as Db

dirname = os.path.dirname(__file__)

connect = info.getDbInfo()
user = info.getUserInfo()

excepts = set()
exempts = set()

re_text = '통신이 원활하지 않습니다. 다시 시도하시기 바랍니다.'

filename_except = os.path.join(dirname, 'util/except')
filename_exempt = os.path.join(dirname, 'util/exempt')

f = open(filename_except, mode='rt', encoding='utf-8')
lines = f.readlines()
for line in lines:
    excepts.add(line.replace('\n', ''))

f = open(filename_exempt, mode='rt', encoding='utf-8')
lines = f.readlines()
for line in lines:
    exempts.add(line.replace('\n', ''))

class Crawler:

    def __init__(self):
        _option = webdriver.ChromeOptions()
        _option.add_argument('headless')
        _option.add_argument('window-size=1920x1080')
        _option.add_argument('disable-gpu')
        self._driver = webdriver.Chrome('chromedriver', chrome_options=_option)
        self._sub_driver = webdriver.Chrome('chromedriver', chrome_options=_option)
        self._wait = WebDriverWait(self._driver, 10)

        self._db = Db.DbConnector(connect)

        # name
        # grade
        # contribution
        # level
        # class
        # job
        # experation
        # population
        # exepmtion

        self._member = list()

        self._info = list()

        self._subName = list()
        self._subCont = list()

        self._insertFlag = {
            'member' : False,
            'guildInfo' : False,
            'subMember' : False
        }

        self._driver.get('https://maplestory.nexon.com/Authentication/Login?t=2')  # Login Page URL
        self._driver.find_element_by_name('ID').send_keys(user['id'])
        self._driver.find_element_by_name('Password').send_keys(user['password'])
        self._driver.find_element_by_css_selector('#frmLoginMaple > div.login_btn_wrap > a > img').click()
        print("Login Success")

    def exceptMember(self, name):
        if name in excepts:
            return False
        else:
            return name

    def exemptMember(self, name):
        if name in exempts:
            return 1
        else:
            return 0

    def crwalDetail(self, element):
        try:
            name = element.find_element_by_tag_name('a').text
            if not self.exceptMember(name):
                return
            member_guild_info = element.find_element_by_class_name('gd_fr_info').text.split(' ')
            grade = member_guild_info[1]
            contribution = member_guild_info[4]
            self._sub_driver.get(element.find_element_by_tag_name('a').get_attribute('href'))

            temp = self._sub_driver.find_element_by_class_name('char_info').find_elements_by_tag_name('dl')
            level = temp[0].find_element_by_tag_name('dd').text.split('LV.')[1]
            member_class = temp[1].find_element_by_tag_name('dd').text.split('/')[0]
            job = temp[1].find_element_by_tag_name('dd').text.split('/')[1]


            t = self._sub_driver.find_elements_by_css_selector('#wrap > div.center_wrap > div.char_info_top > div.char_info > div.level_data > span')
            exp = t[0].text.split('경험치')[1].replace(',', '')
            pop = t[1].text.split('인기도')[1].replace(',', '')

            member = list()
            member.append(grade)
            member.append(name)
            member.append(level)
            member.append(member_class)
            member.append(job)
            member.append(exp)
            member.append(contribution)
            member.append(pop)
            member.append(self.exemptMember(name))
            self._member.append(member)

        except UnexpectedAlertPresentException as e:
            print(e)
            am = Alert(self._sub_driver)
            am_text = am.text
            am.dismiss()
            if am_text == re_text:
                self.crwalDetail(element)
                print('RE')
            else:
                logger.logging(e, am_text)
                print(am_text)
        return True

    def crawl(self):
        # -----------------Member Crawl---------------
        if not self._db.isAlreadyInserted('Member'):
            print("Crawl Start : Member")
            self._driver.get('https://maplestory.nexon.com/home/main')
            self._driver.get(
                self._driver.find_element_by_css_selector('#section02 > div > div.login_after > div.login_after_wrap > dl.login_after_id > dd.login_id > a').get_attribute(
                    'href'))
            self._driver.find_element_by_css_selector('#wrap > div.center_wrap > div.char_info_top > span.my_char_info_btn01 > a').click()
            self._driver.find_element_by_css_selector('#container > div.con_wrap > div.contents_wrap > div > div.tab_menu > ul > li:nth-child(2) > a').click()

            temp = self._driver.find_elements_by_css_selector('li > div.fr_name')
            temp = iter(temp)

            for n in temp:
                self.crwalDetail(n)

            self._insertFlag['member'] = True

            print('Crawl Success : Member')

        else:
            print('Current Data Is Already Updated : Member')

        # -----------GuildInfo Crawl---------------
        if not self._db.isAlreadyInserted('GuildInfo'):
            print("Crawl Start : GuildInfo")
            self._driver.get('https://maplestory.nexon.com/home/main')
            self._driver.get(
                self._driver.find_element_by_css_selector('#section02 > div > div.login_after > div.login_after_wrap > dl.login_after_id > dd.login_id > a').get_attribute(
                    'href'))
            self._driver.find_element_by_css_selector('#container > div.con_wrap > div.lnb_wrap > ul > li:nth-child(11) > a').click()

            member = self._driver.find_element_by_css_selector(
                '#container > div.con_wrap > div.contents_wrap > div > div.tab01_con_wrap > table:nth-child(2) > tbody > tr:nth-child(2) > td:nth-child(4) > span').text.strip()
            pop = self._driver.find_element_by_css_selector(
                '#container > div.con_wrap > div.contents_wrap > div > div.tab01_con_wrap > table:nth-child(2) > tbody > tr:nth-child(3) > td:nth-child(2) > span').text.strip().replace(
                ',', '')
            ranking = self._driver.find_element_by_css_selector(
                '#container > div.con_wrap > div.contents_wrap > div > div.tab01_con_wrap > table:nth-child(2) > tbody > tr:nth-child(4) > td:nth-child(2) > span').text.strip()

            self._info.append(pop)
            self._info.append(member)
            self._info.append(ranking)

            self._insertFlag['guildInfo'] = True

            print('Crawl Success : GuildInfo')
        else:
            print('Current Data Is Already Updated : GuildInfo')

        # ------------SubMember Crawl-------------------
        if not self._db.isAlreadyInserted('SubMember'):
            print("Crawl Start : SubMember")
            self._driver.get('https://maplestory.nexon.com/home/main')
            self._driver.get(
                self._driver.find_element_by_css_selector('#section02 > div > div.login_after > div.login_after_wrap > dl.login_after_id > dd.login_id > a').get_attribute(
                    'href'))
            self._driver.find_element_by_css_selector('body > div.my_cate > div > div:nth-child(2) > span').click()
            for i in self._driver.find_elements_by_css_selector('#mCSB_2_container > li'):
                if i.find_element_by_css_selector('a').get_attribute('title') == user['subname'] :
                    self._driver.execute_script('arguments[0].click()', i.find_element_by_css_selector('a'))
                    break
            self._driver.find_element_by_css_selector('#wrap > div.center_wrap > div.char_info_top > span.my_char_info_btn01 > a').click()
            self._driver.find_element_by_css_selector('#container > div.con_wrap > div.contents_wrap > div > div.tab_menu > ul > li:nth-child(2) > a').click()

            temp = self._driver.find_elements_by_css_selector('li > div.fr_name > span')
            temp = iter(temp)

            for n in temp:
                # name
                # contribution
                tmp = n.text.strip().split()
                if (tmp[0] == '직위'):
                    self._subCont.append(tmp[4])
                else:
                    if (tmp[0] != self.exceptMember(tmp[0])):
                        next(temp)
                        continue
                    self._subName.append(tmp[0])

            self._insertFlag['subMember'] = True

            print('Crawl Success : SubMember')
        else:
            print('Current Data Is Already Updated : SubMember')

        self.__insert__()

    def __insert__(self):
        if self._insertFlag['member']:
            self._db.insertUser(self._member)
            if self._db.isAlreadyInserted('Member'):
                self._db.selectLeaveMember('Member', False)
        if self._insertFlag['guildInfo']:
            self._db.insertGuildInfo(self._info)
        if self._insertFlag['subMember']:
            subUser = list(zip(self._subName, self._subCont))
            self._db.insertSubUser(subUser)
            if self._db.isAlreadyInserted('SubMember'):
                self._db.selectLeaveMember('SubMember', True)

    def test(self):
        print('test')

    def __del__(self):
        self._driver.close()


if __name__ == "__main__":
    cr = Crawler()
    # cr.test()
    cr.crawl()
    print("All Crawling Success")
    f.close()
    os.system("pause")
