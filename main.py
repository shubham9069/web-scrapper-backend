import requests
from bs4 import BeautifulSoup
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import json 
import time

# print(os.path.abspath('')+'\chromedriver-win64\chromedriver')


headers = {
    "Accept": "application/xhtml+xml, text/html, application/xml, */*; q=0.9,image/webp,image/apng, */*;",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0.2 Safari/605.1.15"
    }
def walmartScraper(product_url):
    
    url = product_url["url"]
    platform = product_url['platform']
    driver = webdriver.Chrome()
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": headers["User-Agent"]}) 
    driver.get(url)
    response = driver.page_source
    walmart_obj = {}
    soup=BeautifulSoup(response,"html.parser")
    with open('file.html', 'w',encoding="utf-8") as file:
        file.write(soup.prettify())
        
    if("Robot or human" in response):
        print(True)
        # driver.implicitly_wait(10) 
    
        # button =driver.find_element(By.XPATH, "Press & Hold")
        #         # Create an ActionChains object
        # actions = ActionChains(driver)
        # # Click and hold the button
        # actions.click_and_hold(button).perform()
        # time.sleep(10)

        # # Here you can perform further actions while holding the button
        # # For instance, you might move the mouse or wait for a certain duration

        # # Release the button (this can be placed after the actions you want to perform)
        # actions.release(button).perform()
        
       
    else:
        print("walmart")
        soup=BeautifulSoup(response,"html.parser")
          # with open('file.html', 'w',encoding="utf-8") as file:
        #     file.write(safeway_soup.prettify())
        
        content_array_of_object = soup.find_all("script",attrs={"type": "application/ld+json"})
        
        mrp = soup.find(class_="mr2 f6 gray strike")
        
        print(mrp)
        if hasattr(mrp,'text'):
            walmart_obj["mrp"]= mrp.text.split('$',2)[1].strip()
        else:
            walmart_obj["mrp"]= '' 
        
        price = soup.find('span',itemprop="price")
        print(price)
        if hasattr(price,'text'):
            walmart_obj["price"]= price.text.split('$',2)[1].strip()
        else:
            walmart_obj["price"]= ''         
        
        
        # attribute = soup.find_all("section",attrs={"aria-describedby":"delivery-instructions"})
       
        for x in content_array_of_object:
            json_data = json.loads(x.string)
            if json_data["@type"]=="Product": 
           
             walmart_obj["url"]=url
             walmart_obj["platform"]=platform
             walmart_obj["name"]=json_data["name"]
             walmart_obj["description"]=json_data["description"]
             walmart_obj["priceCurrency"]="USD"
             if type(json_data["image"]) == list:
                 walmart_obj["image"]=json_data["image"][0]
             else:
                 walmart_obj["image"]=json_data["image"]
             if "aggregateRating" in json_data:
                 walmart_obj["ratingValue"]=str(json_data["aggregateRating"]["ratingValue"])
                 walmart_obj["reviewCount"]=str(json_data["aggregateRating"]["reviewCount"])
             else:
                 walmart_obj["ratingValue"]='0' 
                 walmart_obj["reviewCount"]='0' 
             
            #  for att in :
            #     h2_name = att.find("h2",class_="w-100 ma0 pa3 f5 lh-copy normal undefined")
            #     if h2_name is not None and h2_name.text == "Specifications":
            #         product_attribute = []   
            #         list_of_att = att.find("div",class_="nt1")
            #         for  child in list(list_of_att.children):
            #             product_attribute.append({
            #             'name':child.h3.text,
            #             'value':child.span.text
            #             })
            #         walmart_obj["productAttribute"] = product_attribute
           
    return walmart_obj         
                   


def safewayScraper(product_url):
    url = product_url["url"]
    platform = product_url['platform']
    driver = webdriver.Chrome()
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": headers["User-Agent"]}) 
    driver.get(url)
    response = driver.page_source
    safeway_obj = {}
    if("Robot or human" in response):
        print(True)
        safewayScraper(product_url)
    
    else:
        print("safeway")
        
        safeway_soup = BeautifulSoup(response, 'html.parser')
        # with open('file.html', 'w',encoding="utf-8") as file:
        #     file.write(safeway_soup.prettify())
        content_array_of_object = safeway_soup.find_all("script",attrs={"type": "application/ld+json"})
        
        mrp = safeway_soup.find(class_=["product-details__product-price__value-baseprice body-text"])
        print(mrp)
        if hasattr(mrp,'text'):
            safeway_obj["mrp"]= mrp.text.split('$',2)[1].strip()
        else:
            safeway_obj["mrp"]= '' 
            
        price = safeway_soup.find(class_=["display-6 display-6--bold price-lg product-details__product-price__value","display-6 display-6--bold price-lg product-details__product-price__value product-strike-price"])
        
        print(price)
        if hasattr(price,'text'):
            safeway_obj["price"]= price.text.split('$',2)[1].split(" ")[0]
        else:
            safeway_obj["price"]= ''        
        
        for x in content_array_of_object:
            json_data = json.loads(x.string)
            # print(f"safeway {json_data}")
            
            if json_data["@type"]=="Product": 
             safeway_obj["url"]=url
             safeway_obj["platform"]=platform
             safeway_obj["name"]=json_data["name"]
             safeway_obj["description"]=json_data["description"]
             safeway_obj["priceCurrency"]="USD"
             if type(json_data["image"]) == list:
                 safeway_obj["image"]=json_data["image"][0]
             else:
                 safeway_obj["image"]=json_data["image"]
    
             if "aggregateRating" in json_data:
                 safeway_obj["ratingValue"]=str(json_data["aggregateRating"]["ratingValue"])
                 safeway_obj["reviewCount"]=str(json_data["aggregateRating"]["reviewCount"])
             else:
                 safeway_obj["ratingValue"]='0' 
                 safeway_obj["reviewCount"]='0' 
   
    return safeway_obj      
   

def krogerScraper(product_url):
    
    url = product_url["url"]
    platform = product_url['platform']
    driver = webdriver.Chrome()
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": headers["User-Agent"]}) 
    driver.get(url)
    response = driver.page_source
    kroger_obj = {}

    if("Robot or human" in response):
        print(True)
    else:
        print("kroger")
        
        soup = BeautifulSoup(response, 'html.parser')
       
        # with open('file.html', 'w',encoding="utf-8") as file:
        #     file.write(soup.prettify())
        content_array_of_object = soup.find_all("script",attrs={"type": "application/ld+json"})
        
        mrp = soup.find(class_="kds-Price-original")
        print(mrp)
        if hasattr(mrp,'text'):
            kroger_obj["mrp"]= mrp.text.split('$',2)[1].strip()
        else:
            kroger_obj["mrp"]= '' 
        
        price = soup.find(class_="kds-Price kds-Price--alternate mb-8")
        print(price)
        if price is not None :
            kroger_obj["price"]= price["value"]
        else:
            kroger_obj["price"]= ''     
        
        for x in content_array_of_object:
            json_data = json.loads(x.string)

            if json_data["@type"]=="Product":
          
             kroger_obj["url"]=url
             kroger_obj["platform"]=platform
             kroger_obj["name"]=json_data["name"]
             kroger_obj["description"]=json_data["description"]
             kroger_obj["priceCurrency"]="USD"
             if type(json_data["image"]) == list:
                 kroger_obj["image"]=json_data["image"][0]
             else:
                 kroger_obj["image"]=json_data["image"]
                
             if "aggregateRating" in json_data:
                 kroger_obj["ratingValue"]=str(json_data["aggregateRating"]["ratingValue"])
                 kroger_obj["reviewCount"]=str(json_data["aggregateRating"]["reviewCount"])
             else:
                 kroger_obj["ratingValue"]='0' 
                 kroger_obj["reviewCount"]='0' 
                 
    
    return kroger_obj   

  
    
    
