import requests
from bs4 import BeautifulSoup
import re
import time
import os
from tqdm import tqdm  # For progress bar

# Headers and cookies for API
MAIN_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Content-Type': 'application/x-www-form-urlencoded',
    'x-newrelic-id': 'UAUBVVNSARABVFRSDgEHVlAA',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Brave";v="134"',
    'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjQzNjQ1MTkiLCJhcCI6IjExMjAzNDk2MTIiLCJpZCI6ImM5M2ExMTI3M2E5YjlkODMiLCJ0ciI6ImI1MzZmM2JmMjJiOTk0YjhkZWU5Yjc5ZGQ0MmZlYjE4IiwidGkiOjE3NDMwNjYxMDE2MTl9fQ==',
    'sec-ch-ua-mobile': '?0',
    'traceparent': '00-b536f3bf22b994b8dee9b79dd42feb18-c93a11273a9b9d83-01',
    'x-requested-with': 'XMLHttpRequest',
    'tracestate': '4364519@nr=0-1-4364519-1120349612-c93a11273a9b9d83----1743066101619',
    'sec-gpc': '1',
    'accept-language': 'en-US,en;q=0.7',
    'origin': 'https://www.wavespb.com',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.wavespb.com/pb_live',
    'priority': 'u=1, i'
}

MAIN_COOKIES = {
    'ci_session': 'ndpn2funlqjqakdvruj0mpn22a0jtpok',
    '_pk_id.1.2a5f': 'f88fb98868072aef.1743066073.',
    '_pk_ses.1.2a5f': '1'
}

# Headers and cookies for scraping
SCRAPE_HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'dnt': '1',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not?A_Brand";v="99", "Chromium";v="130"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'sec-gpc': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
}

SCRAPE_COOKIES = {
    'ci_session': 'sp9m9s13lc6t1l0dgjkbiho8svgt9mv6'  # Update if expired
}

def fetch_category_data(category_id, category_name):
    data = {'id': category_id, 'type': '0'}
    try:
        response = requests.post(
            'https://www.wavespb.com/web/live/filter_live_data',
            headers=MAIN_HEADERS,
            cookies=MAIN_COOKIES,
            data=data,
            timeout=10
        )
        return response.json()['data'] if response.status_code == 200 else [], category_name
    except Exception as e:
        print(f"Error fetching category {category_name}: {e}")
        return [], category_name

def create_temp_api_playlist():
    categories = [
        ('0', 'All'), ('70', 'News'), ('71', 'Entertainment'), ('73', 'Music'),
        ('72', 'Devotional'), ('76', 'DD National Channels'), ('77', 'DD Regional Channels')
    ]
    
    channels_dict = {}
    print("Waves OTT Channel Scraper")
    print("------------------------")
    print("By Sunil Prasad @ sunilprasad.com.np")
    print("------------------------")
    print("Made with love <3")
    print("------------------------")
    print("Fetching API data...")
    with open('./temp_api.m3u8', 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')
        for cat_id, cat_name in tqdm(categories, desc="Processing API categories"):
            channels, category = fetch_category_data(cat_id, cat_name)
            for channel in channels:
                tvg_id = str(channel['id'])
                tvg_name = channel['title'].replace(' ', '-').lower()
                playlist_line = f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{tvg_name}" tvg-logo="{channel["poster_url"]}" group-title="{category}",{channel["title"]}\n'
                placeholder_url = f'https://in2.sunilprasad.com.np/stream/{tvg_id}/master.m3u8\n'
                f.write(playlist_line)
                f.write(placeholder_url)
                channels_dict[tvg_id] = {
                    'line': playlist_line,
                    'url': placeholder_url,
                    'tvg_logo': channel['poster_url'],
                    'group_title': category,
                    'title': channel['title']
                }
    
    print(f"Temporary API playlist saved to temp_api.m3u8 with {len(channels_dict)} channels")
    return channels_dict

def process_channel(box):
    try:
        href_link = box.find('a')['href']
        response = requests.get(href_link, headers=SCRAPE_HEADERS, cookies=SCRAPE_COOKIES, timeout=10)
        if response.status_code != 200:
            return None, None, None
        
        detail_soup = BeautifulSoup(response.text, 'html.parser')
        
        video_elem = detail_soup.find('video')
        if video_elem and video_elem.get('title'):
            title_parts = video_elem['title'].split('/')
            if len(title_parts) >= 2:
                tvg_id = str(title_parts[0].strip())
                channel_name = title_parts[1].strip()
            else:
                return None, None, None
        else:
            return None, None, None
        
        script_tags = detail_soup.find_all('script')
        stream_url = None
        for script in script_tags:
            if script.string and 'cloudfront.net' in script.string:
                url_match = re.search(r'url\s*=\s*"([^"]+)"', script.string)
                if url_match:
                    stream_url = url_match.group(1)
                    break
        if not stream_url:
            return None, None, None
        
        return tvg_id, channel_name, stream_url
    except Exception as e:
        return None, None, None

def create_temp_scrape_playlist():
    try:
        with open('mainpage.html', 'r', encoding='utf-8') as file:
            html_content = file.read()
    except FileNotFoundError:
        print("Error: mainpage.html not found")
        return {}
    
    soup = BeautifulSoup(html_content, 'html.parser')
    channel_boxes = soup.find_all('div', class_='channelBox')
    total_channels = len(channel_boxes)
    print(f"\nFound {total_channels} channels to process for scrape playlist")
    
    channels_dict = {}
    with open('./temp_scrape.m3u8', 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')
        for box in tqdm(channel_boxes, desc="Scraping channels"):
            tvg_id, channel_name, stream_url = process_channel(box)
            if tvg_id and channel_name and stream_url:
                tvg_name = channel_name.replace(' ', '-').lower()
                playlist_line = f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{tvg_name}",{channel_name}\n'
                f.write(playlist_line)
                f.write(f"{stream_url}\n")
                channels_dict[tvg_id] = {
                    'line': playlist_line,
                    'url': f"{stream_url}\n",
                    'name': channel_name
                }
    
    print(f"Temporary scrape playlist saved to temp_scrape.m3u8 with {len(channels_dict)} channels")
    return channels_dict

def merge_playlists(api_dict, scrape_dict):
    group_counts = {}
    print("\nMerging playlists...")
    with open('./waves.m3u8', 'w', encoding='utf-8') as f:
        # Write custom header
        f.write('#EXTM3U x-tvg-url="https://github.com/sunilprregmi/pb-waves-epg/raw/refs/heads/main/pb-waves.xml.gz"\n')
        f.write('# Waves OTT Scraped Playlist\n')
        f.write('# By Sunil Prasad @ sunilprasad.com.np\n')
        f.write('# Made with love <3\n')
        
        merged_count = 0
        unmatched_count = 0
        for tvg_id in tqdm(api_dict, desc="Merging channels"):
            api_info = api_dict[tvg_id]
            group = api_info['group_title']
            group_counts[group] = group_counts.get(group, 0) + 1
            if tvg_id in scrape_dict:
                scrape_info = scrape_dict[tvg_id]
                merged_line = (
                    f'\n#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{scrape_info["name"].replace(" ", "-").lower()}" '
                    f'tvg-logo="{api_info["tvg_logo"]}" group-title="{group}", {scrape_info["name"]}\n'
                    f'#KODIPROP:inputstream=inputstream.adaptive\n'
                    f'#KODIPROP:inputstream.adaptive.manifest_type=hls\n'
                    f'#EXTVLCOPT:http-user-agent=Dart/2.19 (dart:io)\n'
                )
                f.write(merged_line)
                f.write(scrape_info['url'])
                merged_count += 1
            else:
                f.write(api_info['line'])
                f.write(api_info['url'])
                unmatched_count += 1
    
    print(f"Final playlist saved to waves.m3u8: {merged_count} merged, {unmatched_count} unmatched")
    return group_counts

def main():
    print("------------------------")
    start_time = time.time()
    
    api_dict = create_temp_api_playlist()
    scrape_dict = create_temp_scrape_playlist()
    group_counts = merge_playlists(api_dict, scrape_dict)
    
    # Remove temporary files
    for temp_file in ['temp_api.m3u8', 'temp_scrape.m3u8']:
        if os.path.exists(temp_file):
            os.remove(temp_file)
            print(f"Removed temporary file: {temp_file}")
    
    end_time = time.time()
    total_time = end_time - start_time
    total_channels = len(api_dict)
    
    # Display detailed stats
    print("\n=== Job Summary ===")
    print(f"Total time taken: {total_time:.2f} seconds")
    print(f"Total channels processed: {total_channels}")
    print("Channels per group:")
    for group, count in sorted(group_counts.items()):
        print(f"  {group}: {count}")
    print("===================")

if __name__ == "__main__":
    main()