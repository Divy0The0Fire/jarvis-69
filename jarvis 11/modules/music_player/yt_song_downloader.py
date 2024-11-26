import yt_dlp
import os
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import sqlite3
from pathlib import Path
import pywhatkit

class YTSongDownloader:
    def __init__(self, download_dir: str = None):
        # Set up download directory
        if download_dir is None:
            download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)
        
        # Set up database directory
        self.db_dir = self.download_dir
        os.makedirs(self.db_dir, exist_ok=True)
        
        self.default_opts = {
            'format': 'bestaudio/best',
            'prefer_ffmpeg': True,
            'keepvideo': False,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'noplaylist': True,
        }
        
        self.executor = ThreadPoolExecutor(max_workers=1000)
        
        # Initialize database with connection pooling
        self.db_path = os.path.join(self.db_dir, '.song_cache.db')
        self.conn_pool = []
        self.pool_size = 5
        self.pool_lock = threading.Lock()
        self._init_db()
        self._init_connection_pool()
        
        # Two-step caching system
        self.query_to_url = {}  # Maps search query to video URL
        self.url_to_song = {}   # Maps video URL to song data
        self._load_cache()

    def _init_connection_pool(self):
        """Initialize a pool of database connections"""
        for _ in range(self.pool_size):
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row  # Enable row factory for better performance
            self.conn_pool.append(conn)

    def _get_connection(self):
        """Get a connection from the pool or create a new one"""
        with self.pool_lock:
            if self.conn_pool:
                return self.conn_pool.pop()
            else:
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                conn.row_factory = sqlite3.Row
                return conn

    def _return_connection(self, conn):
        """Return a connection to the pool"""
        with self.pool_lock:
            self.conn_pool.append(conn)

    def _init_db(self):
        """Initialize SQLite database with two-step caching"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS songs (
                    url TEXT PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    title TEXT,
                    duration INTEGER,
                    download_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    search_terms TEXT  -- Store search terms for faster lookup
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS url_cache (
                    search_query TEXT PRIMARY KEY,
                    video_url TEXT NOT NULL,
                    cache_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_songs_title ON songs(title)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_songs_search ON songs(search_terms)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_url_cache ON url_cache(video_url)')
            conn.commit()
        finally:
            self._return_connection(conn)

    def _load_cache(self):
        """Load both URL and song caches into memory"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Load URL cache
            cursor.execute('SELECT search_query, video_url FROM url_cache')
            for row in cursor.fetchall():
                self.query_to_url[row[0].lower()] = row[1]
            
            # Load song cache
            cursor.execute('SELECT url, file_path, title, duration FROM songs')
            for row in cursor.fetchall():
                if os.path.exists(row[1]):  # Only cache if file exists
                    self.url_to_song[row[0]] = {
                        'file_path': row[1],
                        'title': row[2],
                        'duration': row[3]
                    }
                else:
                    # Remove from database if file doesn't exist
                    cursor.execute('DELETE FROM songs WHERE url = ?', (row[0],))
            conn.commit()
        finally:
            self._return_connection(conn)

    def _cache_url(self, search_query: str, video_url: str):
        """Cache the URL mapping"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO url_cache 
                (search_query, video_url, cache_time)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (search_query, video_url))
            conn.commit()
            self.query_to_url[search_query.lower()] = video_url
        finally:
            self._return_connection(conn)

    def _cache_song(self, url: str, file_path: str, title: str, duration: Optional[int], search_terms: str):
        """Cache the song data"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO songs 
                (url, file_path, title, duration, download_time, search_terms)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
            ''', (url, file_path, title, duration, search_terms))
            conn.commit()
            
            # Update memory cache
            self.url_to_song[url] = {
                'file_path': file_path,
                'title': title,
                'duration': duration
            }
        finally:
            self._return_connection(conn)

    def _get_cached_url(self, search_query: str) -> Optional[str]:
        """Get cached video URL for search query"""
        return self.query_to_url.get(search_query.lower())

    def _get_cached_song(self, url: str) -> Optional[Dict[str, Any]]:
        """Get cached song data for URL"""
        data = self.url_to_song.get(url)
        if data and os.path.exists(data['file_path']):
            print(f"Cache hit: Found {data['file_path']} in cache")
            return {
                'success': True,
                'file_path': data['file_path'],
                'title': data['title'],
                'duration': data['duration'],
                'error': None,
                'cached': True
            }
        return None

    def _normalize_url(self, url: str) -> str:
        """Normalize YouTube URL by removing extra parameters"""
        if not url:
            return url
        # Remove escaped characters
        url = url.replace('\\u0026', '&')
        # Get the base video ID
        if 'youtube.com/watch?v=' in url:
            video_id = url.split('watch?v=')[1].split('&')[0]
            return f'https://www.youtube.com/watch?v={video_id}'
        return url

    def _get_video_url(self, song_name: str) -> str:
        """Get video URL with caching"""
        # Check URL cache first
        cached_url = self._get_cached_url(song_name)
        if cached_url:
            print(f"URL cache hit: {cached_url}")
            return cached_url
            
        # Get URL from pywhatkit
        try:
            url = pywhatkit.playonyt(song_name, open_video=False)
            if url:
                # Normalize URL before caching
                url = self._normalize_url(url)
                print(f"Got new URL: {url}")
                self._cache_url(song_name, url)
                return url
        except Exception as e:
            print(f"Error getting video URL: {str(e)}")
        return None

    def sanitize_filename(self, filename: str) -> str:
        """Clean filename to be Windows-compatible"""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*｜'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        
        # Replace spaces and dots to make it more readable
        filename = filename.replace('  ', ' ')
        filename = filename.strip()
        
        return filename

    def download_song(self, song_name: str, output_dir: str, filename: Optional[str] = None) -> Dict[str, Any]:
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Get video URL (from cache or pywhatkit)
            if not song_name.startswith('http'):
                video_url = self._get_video_url(song_name)
                if not video_url:
                    raise Exception("Could not find video URL")
            else:
                # Normalize input URL if it's a direct URL
                video_url = self._normalize_url(song_name)
            
            # Check song cache using URL
            cached_song = self._get_cached_song(video_url)
            if cached_song:
                return cached_song
            
            # Get video info without downloading
            with yt_dlp.YoutubeDL(self.default_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                # Prepare filename
                if filename:
                    base_filename = self.sanitize_filename(filename)
                else:
                    base_filename = self.sanitize_filename(info['title'])
                
                # Configure download options
                download_opts = dict(self.default_opts)
                file_path = os.path.join(output_dir, f"{base_filename}.mp3")
                download_opts['outtmpl'] = os.path.splitext(file_path)[0]
                
                print(f"Downloading to: {file_path}")
                
                # Download and convert the song
                with yt_dlp.YoutubeDL(download_opts) as ydl:
                    ydl.download([video_url])
                
                # Verify file exists
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"Downloaded file not found: {file_path}")
                
                # Cache both URL and song data
                if not song_name.startswith('http'):
                    self._cache_url(song_name, video_url)
                self._cache_song(video_url, file_path, info['title'], info.get('duration'), song_name)
                
                return {
                    'success': True,
                    'file_path': file_path,
                    'title': info['title'],
                    'duration': info.get('duration'),
                    'error': None,
                    'cached': False
                }
                
        except Exception as e:
            print(f"Error downloading song: {str(e)}")
            return {
                'success': False,
                'file_path': None,
                'error': str(e),
                'duration': None,
                'cached': False
            }

def download_song(song_name: str, output_dir: str = None, filename: Optional[str] = None) -> Dict[str, Any]:
    """Download a song using the YTSongDownloader class"""
    downloader = YTSongDownloader(download_dir=output_dir)
    return downloader.download_song(song_name, downloader.download_dir, filename)

if __name__ == "__main__":
    import time
    import os
    import pywhatkit
    from rich import print
    
    start_time = time.time()
    result = download_song("BONITA")
    
    if result['success']:
        print(f"[green]✓ Download successful![/green]")
        print(f"[blue]  - Saved to: {result['file_path']}[/blue]")
        print(f"[yellow]  - Title: {result['title']}[/yellow]")
        if result['duration']:
            print(f"[cyan]  - Duration: {result['duration']} seconds[/cyan]")
        print(f"[magenta]  - Time taken: {time.time() - start_time:.2f} seconds[/magenta]")
    else:
        print(f"[red]✗ Download failed: {result['error']}[/red]")
