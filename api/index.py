from flask import Flask, request, jsonify
import os
import aiohttp
import asyncio
from urllib.parse import parse_qs, urlparse
from api.logger import logger  # Import custom logger
from api.config import cookies, headers

app = Flask(__name__)

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
                log_id = find_between(response_data, 'dp-logid=', '&')

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
                            if 'list' not in response_data3:
                                return None
                            return response_data3['list']

                    return response_data2['list']
    except aiohttp.ClientResponseError as e:
        logger.error(f"Error fetching download link: {e}")
        return None


def extract_thumbnail_dimensions(url: str) -> str:
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    size_param = params.get('size', [''])[0]
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
        logger.error(f"Error getting formatted size: {e}")
        return None


async def format_message(link_data):
    thumbnails = {}
    if 'thumbs' in link_data:
        for key, url in link_data['thumbs'].items():
            if url:
                dimensions = extract_thumbnail_dimensions(url)
                thumbnails[dimensions] = url

    file_name = link_data["server_filename"]
    file_size = await get_formatted_size_async(link_data["size"])
    download_link = link_data["dlink"]
    return {
        'Title': file_name,
        'Size': file_size,
        'Direct Download Link': download_link,
        'Thumbnails': thumbnails
    }


@app.route('/')
def home():
    logger.info('Home page accessed')
    return {
        'status': 'success',
        'message': 'Working Fully',
        'Contact': '@ftmdeveloperz || @ftmdeveloperr'
    }


@app.route('/help', methods=['GET'])
async def help():
    logger.info('Help page accessed')
    return {
        'Info': 'Use the API like this:',
        'Example': 'https://yourdomain.com/api?link=https://1024terabox.com/s/example'
    }


@app.route('/api', methods=['GET'])
async def api():
    try:
        url = request.args.get('link') or request.args.get('url')
        if not url:
            logger.warning('No link or url parameter provided')
            return jsonify({'status': 'error', 'message': 'No link or url parameter provided', 'Link': None})

        logger.info(f"Received request for URL: {url}")
        link_data = await fetch_download_link_async(url)

        if link_data:
            tasks = [format_message(item) for item in link_data]
            formatted_message = await asyncio.gather(*tasks)
        else:
            formatted_message = None

        logger.info(f"Returning response for URL: {url}")
        return jsonify({
            'ShortLink': url,
            'Extracted Info': formatted_message,
            'status': 'success'
        })

    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'Link': request.args.get('link') or request.args.get('url')
        })


if __name__ == '__main__':
    app.run(debug=True)
