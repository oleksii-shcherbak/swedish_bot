import requests

url = "https://svn.spraakbanken.gu.se/sb-arkiv/pub/lmf/saldo/saldo.xml"

print("Downloading SALDO dictionary...")
response = requests.get(url, stream=True)

with open('data/saldo.xml', 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            f.write(chunk)

print("Download complete! File saved as data/saldo.xml")
