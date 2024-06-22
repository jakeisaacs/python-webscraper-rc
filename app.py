import os
import time
import pandas as pd
import smtplib, ssl
from email.message import EmailMessage
from bs4 import BeautifulSoup
from re import sub
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def Notify_Price_Drop(df):

    print("New lower price found...")

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender = os.environ.get('MAIL_SENDER')
    recipients = os.environ.get('MAIL_RECIPIENTS').split(',')
    password = os.environ.get('MAIL_PASSWORD')

    msg = EmailMessage()
    msg['Subject'] = "Royal Caribbean: New Lower Price"
    msg['From'] = sender
    msg['To'] = recipients
    msg.add_header('Content-Type','text/html')
    msg.set_payload(str(df.to_html(index=False)))

    # Send the message via SMTP server.
    context = ssl.create_default_context()
    gmail = smtplib.SMTP_SSL(smtp_server, port, context=context) 
    gmail.login(sender, password)
    gmail.sendmail(sender, recipients, msg.as_string().encode("utf8"))
    gmail.quit()


def Notify_Error(e):

    print(e)

    error_msg = f"Error Message: {str(e)}"

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender = os.environ.get('MAIL_SENDER')
    recipients = os.environ.get('MAIL_RECIPIENTS').split(',')
    password = os.environ.get('MAIL_PASSWORD')

    msg = EmailMessage()
    msg['Subject'] = "Royal Caribbean: Checked Price Failed"
    msg['From'] = sender
    msg['To'] = sender
    msg.add_header('Content-Type','text/html')
    msg.set_payload(error_msg)

    # Send the message via SMTP server.
    context = ssl.create_default_context()
    gmail = smtplib.SMTP_SSL(smtp_server, port, context=context) 
    gmail.login(sender, password)
    gmail.sendmail(sender, recipients, msg.as_string().encode("utf8"))
    gmail.quit()


def main():  
    # headers = {'User-Agent': 'Mozilla/5.0'}
    
    # Cruise Info
    booking_id = os.getenv('BOOKING_ID')
    ship_code = os.getenv('SHIP_CODE')
    sail_date = os.getenv('SAIL_DATE')
    

    # URLs
    key_url = f'https://www.royalcaribbean.com/account/cruise-planner/category/pt_packages/product/33K7?bookingId={booking_id}&shipCode={ship_code}&sailDate={sail_date}'
    excursions_url = f'https://www.royalcaribbean.com/account/cruise-planner/category/pt_shoreX/product/Y6Y2?bookingId={booking_id}&shipCode={ship_code}&sailDate={sail_date}'
    drinkpackage_url = f'https://www.royalcaribbean.com/account/cruise-planner/category/pt_beverage/product/3222?bookingId={booking_id}&shipCode={ship_code}&sailDate={sail_date}'

    # Directory location for files
    wd = os.getcwd()

    # Startup browser
    firefox_options = Options()
    firefox_options.add_argument("--private")
    firefox_options.add_argument("--headless")

    browser = webdriver.Firefox(options=firefox_options)

    load_dotenv()

    try:
        # Get Key prices
        browser.get(key_url)

        elem = WebDriverWait(browser, 120).until(
        EC.presence_of_element_located((By.CLASS_NAME, "cruise-planner-page"))
        )

        html = browser.page_source
        soup = BeautifulSoup(html, 'html.parser')

        key_val = soup.find('span', class_='text-promo-1').text
        key_price = float(sub(r'[^\d.]', '', key_val))

        # Get Hideaway prices
        browser.get(excursions_url)

        elem = WebDriverWait(browser, 120).until(
        EC.presence_of_element_located((By.CLASS_NAME, "cruise-planner-page"))
        )

        html = browser.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # hideaway_val = soup.find('a', attrs={'data-title': 'Hideaway Beach (Adults-Only) — Day Pass'}).find('span', class_='product-card__price-offer').text
        hideaway_val = soup.find('span', class_='text-promo-1').text
        hideaway_price = float(sub(r'[^\d.]', '', hideaway_val))

        # Get Drink Package prices
        browser.get(drinkpackage_url)

        elem = WebDriverWait(browser, 120).until(
        EC.presence_of_element_located((By.CLASS_NAME, "cruise-planner-page"))
        )

        html = browser.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # drinkpackage_val = soup.find('a', attrs={'data-title': 'Deluxe Beverage Package'}).find('span', class_='product-card__price-offer').text
        drinkpackage_val = soup.find('span', class_='text-promo-1').text
        drinkpackage_price = float(sub(r'[^\d.]', '', drinkpackage_val))

        # Outputs
        print(f"Current key price: {key_price}")
        print(f"Current hideaway price: {hideaway_price}")
        print(f"Current drink package price: {drinkpackage_price}")

        fpath = os.path.join(wd, 'rc_prices.csv')

        if os.path.isfile(fpath):
            print("Found file...")
            df = pd.read_csv(fpath)
        else:
            print("Creating new file...")
            df = pd.DataFrame({'Name': ['The Key', 'Hideaway Beach (Adults-Only) — Day Pass', 'Deluxe Beverage Package'], 'Lowest Price': [key_price, hideaway_price, drinkpackage_price], 'Current Price': [key_price, hideaway_price, drinkpackage_price]})


        df['Current Price'] = [key_price, hideaway_price, drinkpackage_price]
        df['New Lower Price?'] = df['Current Price'].lt(df['Lowest Price']).replace({True: 'Yes', False: 'No'})

        if 'Yes' in df['New Lower Price?'].values:
            Notify_Price_Drop(df)

        df['Lowest Price'] = df.apply(lambda x: x['Current Price'] if x['Current Price'] <= x['Lowest Price'] else x['Lowest Price'], axis=1)
        df.to_csv(fpath, index=False)

        with open(os.path.join(wd, "rc_log.txt"), "a+") as f:
            f.write(f"file succeeded on: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}\n")

    except Exception as e:
        Notify_Error(e)

        with open(os.path.join(wd, "rc_log.txt"), "a+") as f:
            f.write(f"program failed on: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}\n")

    finally:
        browser.quit()
        

if __name__ == "__main__":
    main()