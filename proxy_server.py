import requests

with open("valid_proxy.txt","r") as f:
    proxies=f.read().split("\n")

sites_to_check=["https://www.safeway.com","https://www.target.com/"]

counter=0
headers = {
    "Accept": "application/xhtml+xml, text/html, application/xml, */*; q=0.9,image/webp,image/apng, */*;",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

for site in sites_to_check:
    try:
        print(f"using the proxy: {proxies[counter]}")
        res=requests.get(site,headers=headers,proxies={"http":proxies[counter],
                                       "https":proxies[counter]})
        
        print(res.status_code)

    except:
        print("Failed")
    finally:
        counter += 1
        counter % len(proxies)


