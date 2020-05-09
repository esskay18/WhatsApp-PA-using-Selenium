import time
import re
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
#import redditScrapper as red
import databaseHelper as db
import datetime as dt
import traceback

target = '"HCI Project Testing"'  # Group/person's name
x_arg = '//span[contains(@title,' + target + ')]'
std_pat = re.compile("![A-Za-z]+.*$")  # For finding out if message is a command
command_pat = re.compile("![A-Za-z]+")  # For isolating the command
title_pat = re.compile("\".+\"")
date_pat = re.compile("[0-9]{1,2}-[0-9]{1,2}-[0-9]{4}")
date_sans_year_pat = re.compile("[0-9]{1,2}-[0-9]{1,2}")

help_dict = {
    #Notes
    "!addNote": "\"title\" note_content",
    "!getNote": "\"title\"",
    "!getAllNotes": "",
    "!deleteNote": "\"title\"",

    #Birthday
    "!addBirthday": "\"name\" dd-mm-yyyy",
    "!getBirthday": "\"name\"",
    "!getAllBirthdays": "",
    "!deleteBirthday": "\"name\"",

    #Reminders
    "!reminder": "\"title\" reminder_content",
    "!getAllReminders": "",
    "!deleteReminder": "\"title\"",

    #Misc
    "!help": "",
    "!screenshot": "link"
}

def screenshot(file_name, url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--start-maximized')
    temp_driver = webdriver.Chrome(options=chrome_options)
    temp_driver.get(url)
    time.sleep(2)
    # original_size = temp_driver.get_window_size()
    required_width = temp_driver.execute_script('return document.body.parentNode.scrollWidth')
    required_height = temp_driver.execute_script('return document.body.parentNode.scrollHeight')
    temp_driver.set_window_size(required_width, required_height)
    # driver.save_screenshot(path)  # has scrollbar
    temp_driver.find_element_by_tag_name('body').screenshot(file_name)  # avoids scrollbar
    temp_driver.quit()

def sendMessage(msg):
    finalMsg = msg

    message = driver.find_elements_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')[0]
    message.send_keys(finalMsg)
    sendbutton = driver.find_elements_by_xpath('//*[@id="main"]/footer/div[1]/div[3]/button')[0]
    sendbutton.click()

def sendPhoto(file_name):
    button = driver.find_element_by_xpath('//*[@id="main"]/header/div[3]/div/div[2]/div/span')
    button.click()
    image = driver.find_element_by_xpath('//*[@id="main"]/header/div[3]/div/div[2]/span/div/div/ul/li[1]/button/input')
    image.send_keys(os.path.join(source_dir, file_name))
    time.sleep(2)

    sendButton = driver.find_element_by_xpath('//*[ @ id = "app"]/div/div/div[2]/div[2]/span/div/span/div/div/div[2]/span/div')  # '/html/body/div[1]/div/div/div[2]/div[2]/span/div/span/div/div/div[2]/span[2]/div/div')
    sendButton.click()

source_dir = os.path.dirname(os.path.realpath(__file__))
driver = webdriver.Chrome(os.path.join(source_dir, "chromedriver.exe"))

driver.get("https://web.whatsapp.com/")
wait = WebDriverWait(driver, 600)
print("Connected to WhatsApp")

group_title = wait.until(EC.presence_of_element_located((
    By.XPATH, x_arg)))
print("Found group")

time.sleep(2) #Compensating for delay in fetching messages

group_title.click()
print("Group selected")
print("Chatbot started")
prev_msg = ""

while True:

    #elements = driver.find_elements_by_class_name('_1ays2')[-1].find_elements_by_class_name("FTBzM")
    elements = driver.find_elements_by_class_name('selectable-text')[-2]
    print(elements)

    try:
        #data = elements[-1].find_elements_by_class_name('selectable-text')[0].text
        data = elements.text
        if data == "!close":  # Exit condition
            break

        if data != prev_msg or data == "!help":
            print(data)
            if re.match(std_pat, data):
                command = command_pat.findall(data)[0]
                if command in help_dict.keys():
                    if command == "!addNote":
                        title = title_pat.findall(data)[0].replace("\"", "")
                        content = data.replace(command + " \"" + title + "\" ", "", 1)
                        print(title, content)
                        db.addRow("notes", [title, content])
                        sendMessage("Note added : " + title)

                    elif command == "!getAllNotes":
                        result = db.searchTable("notes", ["title", ])
                        for res in result:
                            sendMessage(res[0])

                    elif command == "!getNote":
                        title = title_pat.findall(data)[0].replace("\"", "")
                        result = db.searchTable("notes", ["title", "content"], "title", title)
                        sendMessage("*" + result[0][0] + "*")
                        sendMessage(result[0][1])

                    elif command == "!deleteNote":
                        title = title_pat.findall(data)[0].replace("\"", "")
                        db.deleteRow("notes", "title", title)
                        sendMessage("Note " + title + " deleted")

                    elif command == "!addBirthday":
                        name = title_pat.findall(data)[0].replace("\"", "")
                        date = dt.datetime.strptime(date_pat.findall(data)[0], "%d-%m-%Y").date().strftime("%Y-%m-%d")
                        db.addRow("birthdays", [name, date])
                        sendMessage("Birthdate added : " + name + " " + date)

                    elif command == "!getAllBirthdays":
                        result = db.searchTable("birthdays", ["name", "birth_date"])
                        for res in result:
                            sendMessage("Name : " + res[0] + " -> Date : " + res[1])

                    elif command =="!getBirthday":
                        name = title_pat.findall(data)[0].replace("\"", "")
                        result = db.searchTable("birthdays", ["name", "birth_date"], "name", name)
                        sendMessage("*" + result[0][0] + ":*" + result[0][1])

                    elif command == "!deleteBirthday":
                        name = title_pat.findall(data)[0].replace("\"", "")
                        db.deleteRow("birthdays", "name", name)
                        sendMessage("Birthday " + name + " deleted")

                    elif command == "!screenshot":
                        link = data.replace(command + " ", "")
                        print("Link acquired")
                        file_name = "screenshot.jpeg"
                        screenshot(file_name, link)
                        print("Screenshot taken")
                        sendPhoto(file_name)
                        print("Screenshot uploaded")

                    elif command == "!reminder":
                        name = title_pat.findall(data)[0].replace("\"", "")
                        date = dt.datetime.strptime(date_sans_year_pat.findall(data)[0], "%d-%m").date().strftime("%m-%d")
                        db.addRow("reminder", [name, date])
                        sendMessage("Reminder added : " + name + " " + date)

                    elif command == "!getAllReminders":
                        result = db.searchTable("reminders", ["title", "remind_date"])
                        for res in result:
                            sendMessage("Title : " + res[0] + " -> Date : " + res[1])

                    elif command == "!deleteReminder":
                        title = title_pat.findall(data)[0].replace("\"", "")
                        db.deleteRow("reminder", "title", title)
                        sendMessage("Reminder " + title + " deleted")

                    elif command == "!help":
                        for key, value in help_dict.items():
                            sendMessage(key + " " + value)

                    prev_msg = data

                else:
                    sendMessage("You seem to have entered a wrong command. Please use !help to get more help on the correct command formats")

    except Exception as e:
        print(traceback.format_exc())
        print("Last message deleted")

    time.sleep(2) #To reduce request spam


driver.close()
