from flask import Flask
import os
from flask import request, jsonify
import aiohttp
import asyncio
import logging
from urllib.parse import parse_qs, urlparse

app = Flask(__name__)


# cookies = {
#     'ndut_fmt': 'C96770F2F5849984C2BA2A3F6284E3769F4147D175CD113DA30A8F2DE4CCD1FF',
#     'ndus': 'YvdD63MteHuiw0IgOC3Kdp-b5nahyIkzD_XdJDj2',
#     '__bid_n': '1900b9f02442253dfe4207',
#     '__stripe_mid': 'f5763c3a-0bc5-455f-8bbc-ef5a3a30f25d212bf2',
#     '__stripe_sid': '74502fe5-8572-4d7d-8171-6b47b1c5faf170be67',
#     'browserid': 'ujWfJR9sAO3NO7oCPbQ5IF_P6feJPiSxonWQoahA05CtJ1XhBmDy8oEXuDs=',
#     'csrfToken': 'X-KjyUF6Ezr5GVv53zbJSTeh',
#     'lang': 'en',
#     'PANWEB': '1'
# }

cookies = {
    'PANWEB': '1',
    'browserid': 'p4nVrnlkUVKcnbbJHnIClAhSL5uXs01e-0svx0bm7KHLUB6wIVvCUNGLIpU=',
    'lang': 'en',
    '__bid_n': '1900b9f02442253dfe4207',
    'ndut_fmt': 'BE5EF02E4FBDA93F542338752E051A84DEF30C5E3CBBF98408453BFE5D65FFE4',
    '__stripe_mid': 'b85d61d2-4812-4eeb-8e41-b1efb3fa2a002a54d5',
    'csrfToken': 'xknOoriwpXbwXMVswJ7kv1M7',
    '__stripe_sid': 'e8fd1495-017f-4f05-949c-7cb3a1c780fed92613',
    'ndus': 'YylKpiCteHuiYEqq8n75Tb-JhCqmg0g4YMH03MYD',
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    # 'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Connection': 'keep-alive',
    # 'Cookie': 'PANWEB=1; browserid=p4nVrnlkUVKcnbbJHnIClAhSL5uXs01e-0svx0bm7KHLUB6wIVvCUNGLIpU=; lang=en; __bid_n=1900b9f02442253dfe4207; ndut_fmt=26072FC247E0E0E1B7C00BECB22C3D601A075611F93E73FCD62987106604BB96; __stripe_mid=b85d61d2-4812-4eeb-8e41-b1efb3fa2a002a54d5; ndus=YQ0oArxteHuixh3XTpWEXoBKdp_oo2PImeTyMOUc; csrfToken=nqUTPwVBQj_vtISqp_pro2F5',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Priority': 'u=0, i',
}



def find_between(string, start, end):
  start_index = string.find(start) + len(start)
  end_index = string.find(end, start_index)
  return string[start_index:end_index]


async def fetch_download_link_async(url):
  try:
      async with aiohttp.ClientSession(cookies=cookies, headers=headers) as session:
          async with session.get(url) as response1:
              response1.raise_for_status()
              response_data = await response1.text()
              js_token = find_between(response_data, 'fn%28%22', '%22%29')
              #print(js_token)
              log_id = find_between(response_data, 'dp-logid=', '&')
             # print(log_id)

              if not js_token or not log_id:
                  return None

              request_url = str(response1.url)
              surl = request_url.split('surl=')[1]
              params = {
                  'app_id': '250528',
                  'web': '1',
                  'channel': 'dubox',
                  'clienttype': '0',
                  'jsToken': js_token,
                  'dplogid': log_id,
                  'page': '1',
                  'num': '20',
                  'order': 'time',
                  'desc': '1',
                  'site_referer': request_url,
                  'shorturl': surl,
                  'root': '1'
              }

              async with session.get('https://www.1024tera.com/share/list', params=params) as response2:
                  response_data2 = await response2.json()
                #   print(response_data2)
                  #print("res2", response_data2)
                  if 'list' not in response_data2:
                      return None

                  if response_data2['list'][0]['isdir'] == "1":
                      params.update({
                          'dir': response_data2['list'][0]['path'],
                          'order': 'asc',
                          'by': 'name',
                          'dplogid': log_id
                      })
                      params.pop('desc')
                      params.pop('root')

                      async with session.get('https://www.1024tera.com/share/list', params=params) as response3:
                          response_data3 = await response3.json()
                        #   print(response_data3)
                          #print("res3", response_data3)
                          if 'list' not in response_data3:
                              return None
                          return response_data3['list']
                  #print(response_data2['list'])
                  return response_data2['list']
  except aiohttp.ClientResponseError as e:
      print(f"Error fetching download link: {e}")
      return None


def extract_thumbnail_dimensions(url: str) -> str:
    """Extract dimensions from thumbnail URL's size parameter"""
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    size_param = params.get('size', [''])[0]
    
    # Extract numbers from size format like c360_u270
    if size_param:
        parts = size_param.replace('c', '').split('_u')
        if len(parts) == 2:
            return f"{parts[0]}x{parts[1]}"
    return "original"


async def get_formatted_size_async(size_bytes):
  try:
      size_bytes = int(size_bytes)
      size = size_bytes / (1024 * 1024) if size_bytes >= 1024 * 1024 else (
          size_bytes / 1024 if size_bytes >= 1024 else size_bytes
      )
      unit = "MB" if size_bytes >= 1024 * 1024 else ("KB" if size_bytes >= 1024 else "bytes")

      return f"{size:.2f} {unit}"
  except Exception as e:
      print(f"Error getting formatted size: {e}")
      return None

async def format_message(link_data):
  # Process thumbnails
    thumbnails = {}
    if 'thumbs' in link_data:
        for key, url in link_data['thumbs'].items():
            if url:  # Skip empty URLs
                dimensions = extract_thumbnail_dimensions(url)
                thumbnails[dimensions] = url
#   if link_data
    file_name = link_data["server_filename"]
    file_size = await get_formatted_size_async(link_data["size"])
    download_link = link_data["dlink"]
    sk = {
      'Title': file_name,
      'Size': file_size,
      'Direct Download Link': download_link,
      'Thumbnails': thumbnails
    }
    return sk

@app.route('/')
def hello_world():
  #result = bot.get_me()
  response = {'status': 'success', 'message': 'Working Fully',' Contact': '@Devil_0p || @GuyXD'}
  return response


@app.route(rule='/api', methods=['GET'])
async def Api():
  try:
      url = request.args.get('url', 'No URL Provided')
      logging.info(f"Received request for URL: {url}")
      link_data = await fetch_download_link_async(url)
      if link_data:
          tasks = [format_message(item) for item in link_data]
          formatted_message = await asyncio.gather(*tasks)
        #   formatted_message = await format_message(link_data[0])
          logging.info(f"Formatted message: {formatted_message}")
      else:
          formatted_message = None
      response = { 'ShortLink': url, 'Extracted Info': formatted_message,'status': 'success'}
      return jsonify(response)
  except Exception as e:
      logging.error(f"An error occurred: {e}")
      return jsonify({'status': 'error', 'message': str(e), 'Link': url})

@app.route(rule='/help', methods=['GET'])
async def help():
  try:
      response = { 'Info': "There is Only one Way to Use This as Show Below", 'Example':'https://server_url/api?url=https://terafileshare.com/s/1_1SzMvaPkqZ-yWokFCrKyA'}
      return jsonify(response)
  except Exception as e:
      logging.error(f"An error occurred: {e}")
      response = { 'Info': "There is Only one Way to Use This as Show Below", 'Example':'https://server_url/api?url=https://terafileshare.com/s/1_1SzMvaPkqZ-yWokFCrKyA'}
