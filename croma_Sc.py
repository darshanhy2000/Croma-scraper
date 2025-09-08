


# import time
# import pickle
# import pandas as pd
# import os
# from datetime import datetime
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager

# # ----------------------------
# # CONFIGURATION
# # ----------------------------
# url = "https://www.croma.com/oneplus-13r-5g-12gb-ram-256gb-astral-trail-/p/312533"
# cookies_file = "croma_cookies.pkl"
# csv_file = "croma_product_offers.csv"

# # ----------------------------
# # SETUP DRIVER
# # ----------------------------
# options = webdriver.ChromeOptions()
# options.add_argument("start-maximized")
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# wait = WebDriverWait(driver, 15)

# # ----------------------------
# # MANUAL LOGIN (first time only)
# # ----------------------------
# driver.get("https://www.croma.com")
# input("⚠️ Please log in manually on Croma, then press Enter here...")

# # Save cookies after login
# pickle.dump(driver.get_cookies(), open(cookies_file, "wb"))
# print("✅ Croma cookies saved for future use.")

# # ----------------------------
# # LOAD PRODUCT PAGE WITH COOKIES
# # ----------------------------
# driver.get("https://www.croma.com")
# for cookie in pickle.load(open(cookies_file, "rb")):
#     driver.add_cookie(cookie)
# driver.get(url)
# time.sleep(5)

# # ----------------------------
# # PRODUCT TITLE & PRICE
# # ----------------------------
# try:
#     title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.pdp-title, h1.pd-title"))).text
# except:
#     title = "Not Found"

# try:
#     price = driver.find_element(By.CSS_SELECTOR, "span.amount, span.new-price").text
# except:
#     price = "Not Found"

# # ----------------------------
# # SCRAPE OFFERS (deduplicated)
# # ----------------------------
# offers = []
# timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# try:
#     offer_sections = driver.find_elements(By.CSS_SELECTOR, "div.offers, div[class*='offer'], section[class*='Offer']")
    
#     for section in offer_sections:
#         section_text = section.text.strip()
#         if section_text:
#             # Split multiple offers inside section by double line breaks
#             split_offers = [o.strip() for o in section_text.split("\n\n") if o.strip()]
#             for o in split_offers:
#                 offers.append({
#                     "Product_Title": title,
#                     "Price": price,
#                     "Offer_Description": o,
#                     "Timestamp": timestamp
#                 })

# except Exception as e:
#     print(f"⚠️ No offers found: {e}")

# # ----------------------------
# # CLOSE DRIVER
# # ----------------------------
# driver.quit()

# # ----------------------------
# # SAVE TO CSV (deduplicate before saving)
# # ----------------------------
# df_new = pd.DataFrame(offers)
# if not df_new.empty:
#     df_new.drop_duplicates(subset=["Product_Title", "Price", "Offer_Description"], inplace=True)

# if os.path.exists(csv_file) and os.path.getsize(csv_file) > 0:
#     try:
#         df_existing = pd.read_csv(csv_file, encoding="utf-8-sig")
#         df_combined = pd.concat([df_existing, df_new], ignore_index=True)
#         df_combined.drop_duplicates(subset=["Product_Title", "Price", "Offer_Description"], inplace=True)
#         df_combined.to_csv(csv_file, index=False, encoding="utf-8-sig")
#     except pd.errors.EmptyDataError:
#         df_new.to_csv(csv_file, index=False, encoding="utf-8-sig")
# else:
#     df_new.to_csv(csv_file, index=False, encoding="utf-8-sig")

# print(f"✅ Data saved/appended to {csv_file}")
# print(f"🔹 Total unique offers scraped this run: {len(df_new)}")


import time
import pickle
import pandas as pd
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ----------------------------
# CONFIGURATION
# ----------------------------
input_csv = "FK_link.csv"       # Input file with headers: Brand, Model, Asin, FK link, Croma link
cookies_file = "croma_cookies.pkl"
output_csv = "croma_product_offers.csv"

# ----------------------------
# SETUP DRIVER
# ----------------------------
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 15)

# ----------------------------
# MANUAL LOGIN (first time only)
# ----------------------------
driver.get("https://www.croma.com")
input("⚠️ Please log in manually on Croma, then press Enter here...")

# Save cookies after login
pickle.dump(driver.get_cookies(), open(cookies_file, "wb"))
print("✅ Croma cookies saved for future use.")

# ----------------------------
# LOAD PRODUCT LINKS
# ----------------------------
df_links = pd.read_csv(input_csv)
if "Croma link" not in df_links.columns:
    raise ValueError("CSV must have a column named 'Croma link'")

all_offers = []

# ----------------------------
# SCRAPE EACH PRODUCT
# ----------------------------
for idx, row in df_links.iterrows():
    url = row["Croma link"]
    brand = row.get("Brand", "")
    model = row.get("Model", "")
    asin = row.get("Asin", "")
    fk_link = row.get("FK link", "")
    
    # Load page with cookies
    driver.get("https://www.croma.com")
    for cookie in pickle.load(open(cookies_file, "rb")):
        driver.add_cookie(cookie)
    driver.get(url)
    time.sleep(5)
    
    # Get product title and price
    try:
        title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.pdp-title, h1.pd-title"))).text
    except:
        title = "Not Found"

    try:
        price = driver.find_element(By.CSS_SELECTOR, "span.amount, span.new-price").text
    except:
        price = "Not Found"
    
    # Scrape offers
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        offer_sections = driver.find_elements(By.CSS_SELECTOR, "div.offers, div[class*='offer'], section[class*='Offer']")
        for section in offer_sections:
            section_text = section.text.strip()
            if section_text:
                lines = section_text.split("\n")
                offer_type = lines[0].strip() if len(lines) > 0 else "Offer"
                offer_description = "\n".join(lines[1:]).strip() if len(lines) > 1 else section_text
                
                all_offers.append({
                    "Brand": brand,
                    "Model": model,
                    "Asin": asin,
                    "FK_link": fk_link,
                    "Croma_link": url,
                    "Product_Title": title,
                    "Price": price,
                    "Offer_Type": offer_type,
                    "Offer_Description": offer_description,
                    "Timestamp": timestamp
                })
    except Exception as e:
        print(f"⚠️ No offers found for {url}: {e}")

# ----------------------------
# CLOSE DRIVER
# ----------------------------
driver.quit()

# ----------------------------
# SAVE TO CSV (deduplicate)
# ----------------------------
df_new = pd.DataFrame(all_offers)
if not df_new.empty:
    df_new.drop_duplicates(subset=[
        "Brand","Model","Asin","FK_link","Croma_link","Product_Title",
        "Price","Offer_Type","Offer_Description"
    ], inplace=True)

if os.path.exists(output_csv) and os.path.getsize(output_csv) > 0:
    try:
        df_existing = pd.read_csv(output_csv, encoding="utf-8-sig")
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.drop_duplicates(subset=[
            "Brand","Model","Asin","FK_link","Croma_link","Product_Title",
            "Price","Offer_Type","Offer_Description"
        ], inplace=True)
        df_combined.to_csv(output_csv, index=False, encoding="utf-8-sig")
    except pd.errors.EmptyDataError:
        df_new.to_csv(output_csv, index=False, encoding="utf-8-sig")
else:
    df_new.to_csv(output_csv, index=False, encoding="utf-8-sig")

print(f"✅ Data saved/appended to {output_csv}")
print(f"🔹 Total unique offers scraped: {len(df_new)}")
