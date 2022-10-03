from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
from tkinter import *

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--ignore-certificate-errors-spki-list")
chrome_options.add_argument("--ignore-ssl-errors")

driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))

output = ""
scrape_fail = ""
new_chapter = 0

def scrape_other_pages(url, row):
    global scrape_fail
    global new_chapter

    try:
        driver.get(url)
        chapters_list = driver.find_element(By.XPATH, "//*[@id='shortcodes-ultimate-3']/div/ul")
        latest_chapter_text = chapters_list.find_element(By.TAG_NAME, "a").text
        new_chapter = int(latest_chapter_text.split(" ")[-1])
        if_new(row)
    except:
        scrape_fail += url + "\n"

def scrape_mangapark(url, row):
    global scrape_fail
    global new_chapter

    try:
        driver.get(url)
        latest_chapter_text = driver.find_element(By.CLASS_NAME, "text-sm.text-base-content.opacity-50").text
        latest_chapter_text = latest_chapter_text.replace("(", "")
        new_chapter = int(latest_chapter_text.replace(")", ""))
        if_new(row)
    except:
        scrape_fail += url + "\n"

def scrape_webtoon(url, row):
    global scrape_fail
    global new_chapter

    try:
        driver.get(url)
        new_chapter = int(driver.find_element(By.CLASS_NAME, "_episodeItem").get_attribute("data-episode-no"))
        if_new(row)
    except:
        scrape_fail += url + "\n"

def if_new(row):
    global output

    num_new_chapter = 0

    if new_chapter > 0:
        df = pd.read_excel("./data.xlsx")
        old_scrape_chapter = int(df.iat[row, 2])
        
        if new_chapter > old_scrape_chapter:
            num_new_chapter = new_chapter - old_scrape_chapter
            output += f"\n{df.iat[row, 1]}: {num_new_chapter} New Chapter(s)\n"
            df.iat[row, 2] = new_chapter
            df.to_excel("./data.xlsx", index=False)

def display_output():
    global output
    global scrape_fail

    if len(output) == 0:
        output = "\nNo New Chapter.\n"
    
    if len(scrape_fail) > 0:
        output += "\nUnable to scrape:\n"
        output += scrape_fail

    output += "\n"

    root = Tk()
    root.resizable(False, False)
    root.title('Result')
    label = Label(
        root, 
        text=output, 
        font=("Arial", 13), 
        background="black", 
        foreground="yellow",
        width=55,
        height=21
    )
    label.config(anchor=CENTER)
    label.pack()

    root.mainloop()

def start_scrape():
    global output

    df = pd.read_excel("./data.xlsx")

    for i in range(len(df.index)):
        globals()[df.iat[i, 3]](df.iat[i, 0], i) 
        df = pd.read_excel("./data.xlsx")

    display_output()
    driver.quit()

start_scrape()