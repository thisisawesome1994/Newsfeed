# YouTube-and-News-Mirror
A Webpage That Mirrors your Favourite YouTube Channels and RSS Feeds in an aggregated manner

<h2>YouTube Video Feed and RSS Feed Generator</h2>

<h3>Overview</h3>

This project provides a Python Flask web application that automatically adds new YouTube videos from a list of channels and generates RSS feeds for the videos. The application also combines multiple RSS feeds and sorts entries by their published date and time.

<h3>Features</h3>

- Automatic Video Feed: Update the feed for new YouTube videos from specified channels every hour.
- RSS Feed Generation: Generates an RSS feed for the downloaded videos and another combined RSS feed from multiple sources.
- Web Interface: Provides a web interface to view and watch youtube videos.

  <h3>Prerequisites</h3>

- Python 3.x
- pip

<h3>Installation</h3>

1. Clone the repository:

```


```

2. Install dependencies:
```
pip install -r requirements.txt

```

3. Create necessary files:

- channel_ids.txt: Add YouTube channel IDs (one per line) to this file.
- rss_feeds.txt: Add RSS feed URLs (one per line) to this file.

4. Run the application:
```
python app.py

```

<h3>Usage</h3>

* Access the web interface at http://127.0.0.1:80/ to view and watch videos and RSS Feeds.
* View the RSS feed for videos at http://127.0.0.1:8000/rss.
* View the combined RSS feed for newsarticles at http://127.0.0.1:8000/mixed-rss.

<h3>Project Structure</h3>

```
yt-video-downloader/
├── app.py              # Main application file
├── app.exe             # Main application file (exe)
├── channel_ids.txt     # List of YouTube channel IDs
├── rss_feeds.txt       # List of RSS feed URLs
├── requirements.txt    # Python dependencies

```

<h3>Configuration</h3>

- Video Handling: The application checks for new videos every hour and adds them to the feed.
- RSS Feeds: The RSS feeds are updated every hour.

<h3>Contributing</h3>
Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

Note: I made this by using chatgpt and asking the right questions, while having limited knowledge of coding. Any bugfixes are welcome. I might discontinue this project any time, rendering the file as is for archival or reference use.
