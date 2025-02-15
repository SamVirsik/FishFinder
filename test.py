import requests
import zstandard as zstd
import pandas as pd
from bs4 import BeautifulSoup
import re

def get_html_for_id(id):
    # Define the URL
    url = "https://usa.fishermap.org/ajax/fm-popup-data"

    # Define the headers
    headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Content-Length": "56",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Cookie": "_ga=GA1.1.94088925.1736672341; __gads=ID=afc3396d461444f3:T=1736672341:RT=1736672341:S=ALNI_MZhIO2ElU-9MjDqLAE-5UH7fO_RJw; __gpi=UID=00000fba1fa3bfeb:T=1736672341:RT=1736672341:S=ALNI_MZ8oBpwZ4o-Ff6-gyYYUoAugP0HbA; __eoi=ID=e81556d8d038ea5a:T=1736672341:RT=1736672341:S=AA-Afjan0pPUa6_4byGeh6CQdFzU; XSRF-TOKEN=eyJpdiI6IjFTY2JseTNTWWF6ci9BUktWZEk5Vnc9PSIsInZhbHVlIjoiZTlqR0pPdzFFejhhWnJndzVBMk9IZ21FSHdCeWFVY2QxejBOUnpQRlRhZ2VvNENBaXZ1RTl6MEV0Sld2dkxCQ0g3eGpPNGZxWlFHRFlkUFJFSmw5NnRFbGJZS1J0YzhUY0N6WVozdGx4c0JLZkNnVlFlZmxjV1p4R2VwakVIS3oiLCJtYWMiOiI1OTQ0MzA2ZWZiYzMyYzkyN2Q3ODFlMGY4NTc3MTQ3MDUwNmE1MjM1YjBkYWE3NjJlYzU5NTdhOTA0MmFjOWRhIiwidGFnIjoiIn0%3D; fishermap_session=eyJpdiI6ImJ5dXpLUTlVZmZ6dldPaEhZR1crdGc9PSIsInZhbHVlIjoiMm9CcW14cE9zOU1VWUJVTStuL21pcEFvQ05aSHJlRU8rTmJieXVQU3NTYWpjTkhtRGRnN1ZTY3k3a0l0eloxWExWdnBnSUMwZDFEczZCRm5DVWI5aFpHRUdyMDMxOURSc2l1aVpxcnFUOEhYY0N5VldVUTkxd28xVXNUd0F3bEEiLCJtYWMiOiJlZDNiODgyMjczOTcxMGE1NDVkMmJmN2Y3ODU3NzQyNzI5NzFmMDhjYTNiOWU3NTMxMjQzMjQyYWUwNzg3MzI5IiwidGFnIjoiIn0%3D; FCNEC=%5B%5B%22AKsRol9emKzvVXs1SkaqQ1DMVtzwPS3jW4sdlCUdx-iSm6fO0Nx5w1kh1LJmugRTSlB8oH1DUzQcHROGqrZzA97qZXjhbmWRC14dsV52L9qBnVbjee60FrHH9tklkwZ8nqyC26W7CCoWw2U06PMIlO_fr1ea-kNQ3g%3D%3D%22%5D%5D; _ga_WYPN43XNP7=GS1.1.1736672340.1.1.1736672375.25.0.0",
    "Host": "usa.fishermap.org",
    "Origin": "https://usa.fishermap.org",
    "Referer": "https://usa.fishermap.org/fish-map/",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}

    # Define the request body
    data = {
        "_token": "sBRMBEEZzOCtXiNMlVuddmWFwvCXjxWQLZTWTjLr",
        "id": str(id)
    }

    # Send the POST request
    response = requests.post(url, headers=headers, data=data)

    # Ensure response content is interpreted as HTML
    response.encoding = response.apparent_encoding  # Sets encoding to the server's suggestion

    print(response.headers.get("Content-Encoding"))

    # Assuming `response` is the result of your `requests.post` or `requests.get` call
    # if "zstd" in response.headers.get("Content-Encoding", ""):
    #     try:
    #         dctx = zstd.ZstdDecompressor()
    #         # Decompress the content
    #         decompressed_content = dctx.decompress(response.content).decode("utf-8")
    #         print("Decompressed Content:")
    #         print(decompressed_content)
    #     except zstd.ZstdError as e:
    #         print("Error during Zstandard decompression:", e)
    # else:
    #     # If no compression or different encoding
    #     decompressed_content = response.text
    #     print("Uncompressed Content:")
    #     print(decompressed_content)
    return response

def safe_float(val):
    try:
        return float(val)
    except (ValueError, TypeError, AttributeError):
        return None

def parse_fishing_data(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
    except:
        return None
    
    # Get coordinates
    try:
        coords_text = soup.select_one('.popup-coords .coords').text.strip()
        lat, lon = map(safe_float, coords_text.split(','))
    except:
        lat, lon = None, None
    
    # Get date and time
    try:
        date = soup.select_one('.popup-date span.popup-date').text.strip()
        time_elem = soup.select_one('.popup-date span.popup-time')
        time = time_elem.text.strip() if time_elem else ''
        date_time = f"{date} {time}".strip()
    except:
        date_time = None
    
    # Get weather data
    try:
        temp = safe_float(soup.select_one('.marker-popup-temper-div span').text.strip())
    except:
        temp = None
        
    try:
        wind_div = soup.select_one('.marker-popup-wind-div img')
        wind_match = re.search(r'rotate\((\d+)deg\)', wind_div['style'])
        wind_direction = safe_float(wind_match.group(1)) if wind_match else None
    except:
        wind_direction = None
        
    try:
        pressure = safe_float(soup.select_one('.marker-popup-press-div span').text.strip())
    except:
        pressure = None
    
    # Get fish types
    try:
        fish_types = [span.text.strip() for span in soup.select('.carousel-item-name')]
        if not fish_types:
            fish_types = None
    except:
        fish_types = None
    
    return {
        'latitude': lat,
        'longitude': lon,
        'datetime': date_time,
        'temperature': temp,
        'wind_direction': wind_direction,
        'pressure': pressure,
        'fish_types': fish_types
    }

# Usage with your existing code


known = [104678, 95250]
# for i in range(100000, 1000000):
    # print(i, get_html_for_id(i)[0])

# print(get_html_for_id(95250))

#50 in 11 seconds -> 110,000 in 11 * 110,000 / 50 = 24,200 seconds = 403 minutes = 6.7 hours
#less than 110,000
columns = ['latitude', 'longitude', 'datetime', 'temperature', 'wind_direction', 'pressure', 'fish_types']
df = pd.DataFrame(columns=columns)
for i in range(1,10):
    print(f"Fetching record {i}...", end=' ')
    try:
        response_text = get_html_for_id(i).text
        data = parse_fishing_data(response_text)
        if data:  # Check if data was successfully parsed
            # Convert dictionary to Series and append to DataFrame
            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
            print("Success")
        else:
            print("No data")
    except Exception as e:
        print(f"Error: {str(e)}")
        continue

print("\nFinal DataFrame:")
print(df)