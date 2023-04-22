import httpx
from bs4 import BeautifulSoup
   
async def httpcat_msgs(url):
    async with httpx.AsyncClient(verify=False, timeout=None) as client:
      resp = await client.get(
        url,    
      )
      page = resp.text 
      soup = BeautifulSoup(page, 'html.parser')
      bf = soup.find('p')
      waste = soup.find('a')
      bf.replace_with(waste,'')
      return bf