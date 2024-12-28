from dotenv import load_dotenv
import pytube
import os

from langchain_openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import YoutubeLoader


class YouTubeAnalyzer:
    def __init__(self, url):
        load_dotenv()

        self.url = url

        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.llm = OpenAI(
            temperature=0.1,
            openai_api_key=self.openai_api_key,
            max_tokens=1000,

        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=0,
            model="gpt-4o-mini"
        )

    def load_youtube_content(self, method="direct"):
        """
        Load YouTube video content using different methods

        Args:
            url (str): YouTube video URL
            method (str): Loading method ('direct', 'alternative', or 'pytube')

        Returns:
            list: Loaded documents
        """
        try:
            if method == "direct":
                # Method 1: Clean URL and use basic parameters
                video_id = self.url.split("watch?v=")[1].split("&")[0]
                clean_url = f"https://www.youtube.com/watch?v={video_id}"

                loader = YoutubeLoader.from_youtube_url(
                    youtube_url=clean_url,
                    add_video_info=False
                )
                return loader.load()

            elif method == "alternative":
                # Method 2: Use alternative parameters
                loader = YoutubeLoader.from_youtube_url(
                    youtube_url=self.url,
                    add_video_info=False,
                    language=["en"],
                    translation="en"
                )
                return loader.load()

            elif method == "pytube":
                # Method 3: Use pytube directly
                yt = pytube.YouTube(self.url)
                transcript = yt.captions.get_by_language_code('en')
                if transcript is None:
                    transcript = yt.captions.all()[0]  # Get first available caption

                text = transcript.generate_srt_captions()
                return [{"page_content": text, "metadata": {"title": yt.title, "url": self.url}}]

            else:
                raise ValueError(f"Unsupported method: {method}")

        except Exception as e:
            raise Exception(f"Error loading YouTube content: {str(e)}")

