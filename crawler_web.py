# -*- coding: big5 -*-
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date
from colorama import init, Fore, Style
import yfinance as yf
import os
init(autoreset=True)

def safe_divide(a, b):
    return a / b if a is not None and b is not None and b != 0 else None

def get_fundamentals(stock_code):
    ticker = yf.Ticker(f"{stock_code}.TWO")
    info = ticker.info
    bs = ticker.balance_sheet

    get_value = lambda label: bs.get(label, [None])[0]

    eps = info.get("trailingEps")
    gross_margin = info.get("grossMargins")
    pe = info.get("trailingPE")
    pbr = info.get("priceToBook")
    fcf = info.get("freeCashflow")
    dividend_yield = info.get("dividendYield")

    total_liabilities = get_value("Total Liabilities Net Minority Interest")
    total_assets = get_value("Total Assets")
    current_assets = get_value("Current Assets")
    current_liabilities = get_value("Current Liabilities")

    debt_ratio = safe_divide(total_liabilities, total_assets)
    current_ratio = safe_divide(current_assets, current_liabilities)

    return {
        "EPS": eps,
        "Gross Margin": gross_margin,
        "PE": pe,
        "PBR": pbr,
        "Free Cash Flow": fcf,
        "Dividend Yield": dividend_yield,
        "Debt Ratio": debt_ratio,
        "Current Ratio": current_ratio
    }



def colorize(n: int) -> str:
    if n > 0:
        return f"{Fore.RED}{n:>10}{Fore.RESET}"
    elif n < 0:
        return f"{Fore.GREEN}{n:>10}{Fore.RESET}"
    else:
        return f"{Fore.WHITE}{n:>10}{Fore.RESET}"

def get_stock_info(stock_code, return_data = False):
    today = date.today
    folder_path = "D:/�{��/NCKU/113_2_project/web_crawler/TW_web_crawler/stock_data"
    content_path = os.path.join(folder_path, f"{stock_code}.txt")
    # if os.path.exists(content_path):
    #     print(f"{stock_code}.txt �w�s�b�AŪ����...")
    #     with open(content_path, "r", encoding="utf-8") as f:
    #         content = f.read()
    #     return content

    service =  Service("D:/chromedriver.exe")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # �i��G���}�����I������]�������|�ݨ��s�����^
    lines = []
    
    # �Ұ��s����
    driver = webdriver.Chrome(service=service, options=options)
    today = date.today()
    # ���} Yahoo �x�n�q����
    site = "https://tw.stock.yahoo.com/quote/" + str(stock_code) + ".TW"
    max_retries = 3
    for a in range(max_retries):
        try:
            driver.get(site)
            break
        except:
            print(f"�� {a+1} �� SSL ���~�A���s���դ�...")
            time.sleep(1)
    #�o��O�A���Ƹ��J�B���ݦ�����X�{�]�̦h�� 10 ��^
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.D\\(f\\).Fld\\(c\\).Flw\\(w\\).H\\(192px\\).Mx\\(-16px\\)'))
    )
    #�o��O�b�s���䪺��ul
    ul = driver.find_element(By.CSS_SELECTOR, 'ul.D\\(f\\).Fld\\(c\\).Flw\\(w\\).H\\(192px\\).Mx\\(-16px\\)')
    lis = ul.find_elements(By.TAG_NAME, 'li')
    name = driver.find_element(By.CSS_SELECTOR, 'h1.C\\(\\$c-link-text\\).Fw\\(b\\).Fz\\(24px\\).Mend\\(8px\\)').text
    open_ = float(lis[1].find_elements(By.TAG_NAME,'span')[1].text.replace(",",""))
    high = float(lis[2].find_elements(By.TAG_NAME,'span')[1].text.replace(",",""))
    gap = float(lis[8].find_elements(By.TAG_NAME,'span')[1].text.replace(",",""))
    low = float(lis[3].find_elements(By.TAG_NAME,'span')[1].text.replace(",",""))
    close = float(lis[0].find_elements(By.TAG_NAME,'span')[1].text.replace(",",""))
    close_yesterday = float(lis[6].find_elements(By.TAG_NAME,'span')[1].text.replace(",",""))
    change_percent = (close-close_yesterday)/close_yesterday
    avg = float(lis[4].find_elements(By.TAG_NAME,'span')[1].text.replace(",",""))
    if close >= open_:    #�W�v�u
        upper_shadow = (high-close)/open_
    else:
        upper_shadow = (high-open_)/open_
    if close >= open_:    #�U�v�u
        lower_shadow = (open_-low)/open_
    else:
        lower_shadow = (close-low)/open_
    volume = int(lis[9].find_elements(By.TAG_NAME,'span')[1].text.replace(",",""))
    volume_yesterday = float(lis[10].find_elements(By.TAG_NAME,'span')[1].text.replace(",",""))
    volume_change_percent  = (volume-volume_yesterday)/volume_yesterday #ok
    summary = {
        "stock_name": name,
        "stock_code": stock_code,
        "date": str(today),
        "price_info": {
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "gap": gap,
            "change_percent": round(change_percent * 100, 2),
            "close_yesterday": close_yesterday,
            "avg": avg,
            "upper_shadow": round(upper_shadow*100, 2),
            "lower_shadow": round(lower_shadow*100, 2),
            "volume": volume,
            "volume_change_percent": round(volume_change_percent * 100, 2)
        },
        "institutional_trading": []
    }
    
    site = "https://tw.stock.yahoo.com/quote/" + str(stock_code) + ".TW/institutional-trading"
    for a in range(max_retries):
        try:
            driver.get(site)
            break
        except:
            print(f"�� {a+1} �� SSL ���~�A���s���դ�...")
            time.sleep(1)
    rows = driver.find_elements(By.CSS_SELECTOR, "div.Bgc\\(\\#fff\\).table-row")
    total_foreign = 0
    total_investment = 0
    total_dealer = 0
    total_total = 0
    time = 0
    for row in rows[4:19]:  # ��e5��
        time += 1
        cols = row.find_elements(By.CSS_SELECTOR, "div")
        day = cols[1].text
        foreign = int(cols[2].text.replace(',', ''))
        investment = int(cols[3].text.replace(',', ''))
        dealer = int(cols[4].text.replace(',', ''))
        total = foreign + investment + dealer
        total_foreign += foreign
        total_investment += investment
        total_dealer += dealer
        total_total += total
        summary["institutional_trading"].append({
            "date": day,
            "foreign": foreign,
            "investment": investment,
            "dealer": dealer,
            "total": total
        })    
        if(time % 5 == 0):
            date_de ="�� " + str(time) + " ���`�M"
            summary["institutional_trading"].append({
            "date": date_de,
            "foreign": total_foreign,
            "investment": total_investment,
            "dealer": total_dealer,
            "total": total_total
            })
    # print(f"{Style.BRIGHT}�򥻭��ƾ�")
    # data = get_fundamentals(stock_code)
    # print("***��Q��O***")
    # print(f"EPS(�C�Ѭվl) = {data['EPS']}")
    # print(f"��Q�v = {data["Gross Margin"]}")
    
    # print("***�ѻ�����***")
    # print(f"PE(���q��) = {data['PE']}")
    # print(f"PBR(�ѻ��b�Ȥ�) = {data["PBR"]}")
    
    # print("***�]�Ȧw����***")
    # print(f"Debt Ratio(�t�Ť�) = {data['Debt Ratio']}")
    # print(f"Current Ratio(�y�ʤ�) = {data["Current Ratio"]}")
    
    # print("***�{���y�P�Ѯ�***")
    # print(f"FCF(�ۥѲ{���y) = {data["Free Cash Flow"]}")
    # print(f"Dividend Yield(�ާQ�v) = {data['Dividend Yield']}")
    
    driver.quit()
    return summary
    