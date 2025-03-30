# Waves OTT Channel Scraper

A Python script to scrape and generate M3U8 playlists from Waves OTT platform. This tool creates a merged playlist combining data from both API and web scraping sources.

## Features

- Fetches channel data from Waves OTT API
- Scrapes channel information from the website
- Generates merged M3U8 playlist with:
  - Channel information (ID, name, logo)
  - Stream URLs
  - Group categorization
  - EPG support
- Progress bars for all operations
- Detailed job summary with statistics

## Prerequisites

- Python 3.7 or higher
- Internet connection
- Access to Waves OTT platform

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sunilprregmi/pb-waves.git
cd pb-waves
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Ensure you have a valid `mainpage.html` file in the project directory
2. Run the script:
```bash
python waves.py
```

The script will:
1. Create a temporary API playlist
2. Create a temporary scrape playlist
3. Merge both playlists into a final `waves.m3u8` file
4. Clean up temporary files
5. Display a detailed job summary

## Output Files

- `waves.m3u8`: Final merged playlist with all channels
- Temporary files (automatically cleaned up):
  - `temp_api.m3u8`
  - `temp_scrape.m3u8`

## Categories

- All
- News
- Entertainment
- Music
- Devotional
- DD National Channels
- DD Regional Channels

## Contributing

Feel free to open issues or submit pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Original work by Sunil Prasad (sunilprasad.com.np)
- EPG data source: pb-waves-epg repository

## Disclaimer

This tool is for educational purposes only. Please ensure you have the necessary permissions to access and use the content.