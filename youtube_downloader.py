from pytube import YouTube, Stream
import logging
import io

logging.basicConfig(level=logging.INFO)
logging.getLogger('pytube').setLevel(logging.INFO)

# Define mp3_metadata dictionary
mp3_metadata = {
    'Title': '',
    'Size': 0.0
}

# Static variables
DOMAIN = "://download.blueprismo.com"
PORT = 8080


# Extract first audio stream
def extract_mp3_first_audio_stream(youtube_url) -> Stream | None:
    """
    Extracts the first audio stream from the youtube link
    :param youtube_url: the youtube URL where we will extract the stream
    :type youtube_url: str

    :returns: The first audio stream found or None if not found
    :rtype: Youtube.Stream | None
    """
    yt = YouTube(youtube_url)
    return yt.streams.filter(only_audio=True, adaptive=True).first()


# Download the YouTube video to buffer (no write anywhere)
def convert_mp3_buffer(youtube_url) -> tuple[io.BytesIO, mp3_metadata]:
    """
    Gets a youtube video URL, extract it's first audio stream and metadata
    Write the stream into a memory buffer
    Return the buffer and the metadata in a tuple

    :param youtube_url: the youtube URL where we will extract the stream
    :type youtube_url: str

    :returns: Tuple with in-memory buffer and mp3_metadata dict
    :rtype: tuple[io.BytesIO, dict[str,Any]]
    """

    mp3 = extract_mp3_first_audio_stream(youtube_url)
    metadata = stream_metadata(mp3)

    # Initialize a new byte buffer
    buffer = io.BytesIO()
    mp3.stream_to_buffer(buffer)

    return buffer.getvalue(), metadata


# Download the Youtube video into Filesystem (into NFS or some storage)
# def convert_mp3_fs(youtube_url) -> (str, mp3_metadata):
def convert_mp3_fs(youtube_url) -> (str, mp3_metadata):
    """
    Gets a youtube video url, extract it's audio stream and metadata,
    Write the stream into an mp3 file in the current directory,
    then return the link for the mp3 static file to be downloaded
    """
    mp3 = extract_mp3_first_audio_stream(youtube_url)
    # mp3 = extract_mp3_first_audio_stream("https://youtube.com/WXxV9g7lsFE?si=6XtKMC49ozSErESi")
    metadata = stream_metadata(mp3)

    # Download the file into FS
    mp3.download("./", f'{metadata["Title"]}.mp3', max_retries=1)

    return f'{DOMAIN}:{PORT}/{metadata["Title"]}.mp3', metadata


# Check for stream metadata
def stream_metadata(mp3_stream) -> mp3_metadata:
    """
    Extracts metadata from the youtube URL to be send back into the telegram channel
    :param youtube_url: The youtube URL where we will extract the stream
    :type youtube_url: str

    :return: The dictionary that contains metadata about the audio stream
    :rtype: dict[str,Any]
    """

    # Assign metadata
    mp3_metadata['Title'] = mp3_stream.title
    mp3_metadata['Size'] = mp3_stream.filesize_mb

    # Log information about metadata
    logging.info(f'Stream size: {mp3_stream.filesize_mb:.1f} MBSteam')
    logging.info(f'Stream Title: {mp3_stream.title}\n')

    return mp3_metadata


if __name__ == "__main__":
    convert_mp3_fs()