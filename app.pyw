import os
import feedparser
import schedule
import time
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template_string, url_for, Response
import threading
from feedgen.feed import FeedGenerator
import pystray
from PIL import Image, ImageDraw
import webbrowser

app = Flask(__name__)

# Define the path to the file containing channel IDs
CHANNEL_IDS_FILE = "channel_ids.txt"
RSS_FEEDS_FILE = "rss_feeds.txt"

# Global list to store video information
video_list = []
video_ids = set()  # Set to keep track of video IDs to avoid duplicates

def sanitize_filename(filename):
    """Sanitize the filename to avoid any illegal characters"""
    return "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()

def fetch_videos_for_channel(channel_id):
    rss_feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    # Parse the RSS feed
    feed = feedparser.parse(rss_feed_url)

    for entry in feed.entries:
        video_url = entry.link
        video_id = video_url.split('v=')[1]

        if video_id in video_ids:
            continue  # Skip if the video ID is already in the set

        video_title = sanitize_filename(entry.title)
        video_description = entry.get('summary', 'No description available')
        channel_name = sanitize_filename(entry.author)
        channel_id = entry.yt_channelid
        published_date = datetime.strptime(entry.published, '%Y-%m-%dT%H:%M:%S%z')

        video_info = {
            'video_id': video_id,
            'title': video_title,
            'description': video_description[:1300],
            'published_on': published_date.isoformat(),
            'original_link': video_url,
            'channel_name': channel_name
        }

        video_list.append(video_info)
        video_ids.add(video_id)  # Add the video ID to the set

def load_channel_ids():
    with open(CHANNEL_IDS_FILE, 'r') as file:
        return [line.strip() for line in file.readlines()]

def load_rss_feeds():
    with open(RSS_FEEDS_FILE, 'r') as file:
        return [line.strip() for line in file.readlines()]

def fetch_videos():
    global video_list
    channel_ids = load_channel_ids()
    for channel_id in channel_ids:
        fetch_videos_for_channel(channel_id)

# Schedule the script to run every hour
schedule.every().hour.do(fetch_videos)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=run_scheduler).start()

@app.route('/')
def landing_page():
    landing_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Landing Page</title>
        <style>
            body {
                display: flex;
                justify-content: center;
                align-items: center;
                flex-direction: column;
                min-height: 100vh;
                margin: 0;
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
            }
            .container {
                text-align: center;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                width: 90%;
                max-width: 600px;
            }
            .navigation a {
                display: block;
                margin: 20px 0;
                text-decoration: none;
                color: #007bff;
                font-size: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome</h1>
            <div class="navigation">
                <a href="/videos">View YouTube Videos</a>
                <a href="/mixed">View News Articles</a>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(landing_template)

@app.route('/videos')
def index():
    global video_list

    # Sort the video list by publishing date in descending order
    sorted_videos = sorted(video_list, key=lambda x: datetime.fromisoformat(x['published_on']), reverse=True)

    # Limit the number of videos to 75
    limited_videos = sorted_videos[:75]

    index_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>YouTube Videos</title>
        <style>
            body {
                display: flex;
                justify-content: center;
                align-items: center;
                flex-direction: column;
                min-height: 100vh;
                margin: 0;
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
            }
            .container {
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                width: 90%;
                max-width: 1200px;
            }
            .videos {
                display: flex;
                flex-direction: column;
                align-items: center;
                width: 100%;
            }
            .video-item {
                background-color: #f9f9f9;
                padding: 10px;
                border-radius: 10px;
                box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
                margin: 10px 0;
                width: 100%;
                max-width: 600px;
            }
            .video-item iframe {
                width: 560px;
                height: 315px;
                border-radius: 5px;
            }
            .navigation {
                margin-bottom: 20px;
            }
            .navigation a {
                margin: 0 10px;
                text-decoration: none;
                color: #007bff;
            }
        </style>
        <script>
            // Refresh the page every hour (3600 seconds)
            setTimeout(function() {
                location.reload();
            }, 3600000); // 3600 seconds in milliseconds
        </script>
    </head>
    <body>
        <div class="container">
            <div class="navigation">
                <a href="/">Home</a>
                <a href="/mixed">News Articles</a>
            </div>
            <div class="videos">
                <h2>YouTube Videos</h2>
                {% for video in videos %}
                    <div class="video-item">
                        <h3>{{ video.title }}</h3>
                        <p>{{ video.description }}</p>
                        <p>Published On: {{ video.published_on }}</p>
                        <p>Channel: {{ video.channel_name }}</p>
                        <iframe width="560" height="315" src="https://www.youtube.com/embed/{{ video.video_id }}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
                    </div>
                {% endfor %}
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(index_template, videos=limited_videos)

@app.route('/mixed')
def mixed_rss_page():
    feeds = load_rss_feeds()
    combined_entries = []

    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            published_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            combined_entries.append({
                'title': entry.title,
                'link': entry.link,
                'description': entry.get('summary', 'No description available')[:1300],  # First 1300 characters of the description
                'published_date': published_date
            })

    combined_entries.sort(key=lambda x: x['published_date'], reverse=True)

    mixed_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>News Articles</title>
        <style>
            body {
                display: flex;
                justify-content: center;
                align-items: center;
                flex-direction: column;
                min-height: 100vh;
                margin: 0;
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
            }
            .container {
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                width: 90%;
                max-width: 1200px;
            }
            .entries {
                display: flex;
                flex-direction: column;
                align-items: center;
                width: 100%;
            }
            .entry-item {
                background-color: #f9f9f9;
                padding: 10px;
                border-radius: 10px;
                box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
                margin: 10px 0;
                width: 100%;
                max-width: 600px;
            }
            .navigation {
                margin-bottom: 20px;
            }
            .navigation a {
                margin: 0 10px;
                text-decoration: none;
                color: #007bff;
            }
        </style>
        <script>
            // Refresh the page every hour (3600 seconds)
            setTimeout(function() {
                location.reload();
            }, 3600000); // 3600 seconds in milliseconds
        </script>
    </head>
    <body>
        <div class="container">
            <div class="navigation">
                <a href="/">Home</a>
                <a href="/videos">YouTube Videos</a>
            </div>
            <div class="entries">
                <h2>News Articles</h2>
                {% for entry in entries %}
                    <div class="entry-item">
                        <h3>{{ entry.title }}</h3>
                        <p>{{ entry.description }}</p>
                        <p>Published On: {{ entry.published_date }}</p>
                        <a href="{{ entry.link }}" target="_blank">Read More</a>
                    </div>
                {% endfor %}
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(mixed_template, entries=combined_entries)

@app.route('/rss')
def rss_feed():
    global video_list
    fg = FeedGenerator()
    fg.title('YouTube Videos RSS Feed')
    fg.link(href=url_for('rss_feed', _external=True), rel='self')
    fg.description('RSS feed for YouTube videos.')

    # Combine and sort all entries based on published date in descending order
    combined_entries = sorted(video_list, key=lambda x: datetime.fromisoformat(x['published_on']), reverse=True)

    for video in combined_entries:
        fe = fg.add_entry()
        fe.title(video['title'])
        fe.link(href=video['original_link'], rel='alternate')
        fe.description(f"""
            {video['description']}
            <br><br>
            <iframe width="560" height="315" src="https://www.youtube.com/embed/{video['video_id']}"
                title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write;
                encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin"
                allowfullscreen></iframe>
        """)
        fe.pubDate(datetime.fromisoformat(video['published_on']).replace(tzinfo=timezone.utc))

    rss_feed_data = fg.rss_str(pretty=True)
    return Response(rss_feed_data, mimetype='application/rss+xml')

@app.route('/mixed-rss')
def mixed_rss_feed():
    feeds = load_rss_feeds()
    combined_entries = []

    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            published_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            combined_entries.append({
                'title': entry.title,
                'link': entry.link,
                'description': entry.get('summary', 'No description available')[:1300],  # First 1300 characters of the description
                'published_date': published_date
            })

    combined_entries.sort(key=lambda x: x['published_date'], reverse=True)

    fg = FeedGenerator()
    fg.title('Combined RSS Feed')
    fg.link(href=url_for('mixed_rss_feed', _external=True), rel='self')
    fg.description('A combined RSS feed of multiple sources.')

    for entry in combined_entries:
        fe = fg.add_entry()
        fe.title(entry['title'])
        fe.link(href=entry['link'], rel='alternate')
        fe.description(f"""
            {entry['description']}
            <br><br>
            <iframe width="560" height="315" src="{entry['link']}"
                title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write;
                encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin"
                allowfullscreen></iframe>
        """)
        fe.pubDate(entry['published_date'])

    mixed_rss_feed_data = fg.rss_str(pretty=True)
    return Response(mixed_rss_feed_data, mimetype='application/rss+xml')

def on_clicked(icon, item):
    if str(item) == "Exit":
        icon.stop()
        os._exit(0)
    elif str(item) == "Open YouTube Feed":
        webbrowser.open("http://127.0.0.1/videos")
    elif str(item) == "Open News Articles Feed":
        webbrowser.open("http://127.0.0.1/mixed")

menu = pystray.Menu(
    pystray.MenuItem("Open YouTube Feed", on_clicked),
    pystray.MenuItem("Open News Articles Feed", on_clicked),
    pystray.MenuItem("Exit", on_clicked)
)

# Use the created .ico file for the tray icon
icon = pystray.Icon("youtube_downloader", Image.open("icon.ico"), "RSS Feeds", menu)

def run_flask():
    app.run(debug=False, host='0.0.0.0', port=80)

if __name__ == "__main__":
    threading.Thread(target=fetch_videos).start()
    threading.Thread(target=run_flask).start()
    icon.run()