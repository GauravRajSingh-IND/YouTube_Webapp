from dotenv import load_dotenv
import pytube
import os

from langchain_openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import YoutubeLoader
from langchain.chains.summarize import load_summarize_chain

class YouTubeAnalyzer:
    def __init__(self, openai_api_key=os.getenv(key="OPENAI_API_KEY")):
        """
        Initialize the YouTubeSummarizer with OpenAI API key

        Args:
            openai_api_key (str, optional): OpenAI API key. If not provided, will try to load from environment
        """
        load_dotenv()
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.llm = OpenAI(
            temperature=0.1,
            openai_api_key=self.openai_api_key
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=0
        )

    def load_youtube_content(self, url, method="direct"):
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
                video_id = url.split("watch?v=")[1].split("&")[0]
                clean_url = f"https://www.youtube.com/watch?v={video_id}"

                loader = YoutubeLoader.from_youtube_url(
                    youtube_url=clean_url,
                    add_video_info=False
                )
                return loader.load()

            elif method == "alternative":
                # Method 2: Use alternative parameters
                loader = YoutubeLoader.from_youtube_url(
                    youtube_url=url,
                    add_video_info=False,
                    language=["en"],
                    translation="en"
                )
                return loader.load()

            elif method == "pytube":
                # Method 3: Use pytube directly
                yt = pytube.YouTube(url)
                transcript = yt.captions.get_by_language_code('en')
                if transcript is None:
                    transcript = yt.captions.all()[0]  # Get first available caption

                text = transcript.generate_srt_captions()
                return [{"page_content": text, "metadata": {"title": yt.title, "url": url}}]

            else:
                raise ValueError(f"Unsupported method: {method}")

        except Exception as e:
            raise Exception(f"Error loading YouTube content: {str(e)}")

    def split_text(self, documents):
        """
        Split documents into smaller chunks

        Args:
            documents (list): List of documents to split

        Returns:
            list: Split chunks of text
        """
        return self.text_splitter.split_documents(documents)

    def summarize_video(self, chunks):
        """
        Summarize video content from text chunks

        Args:
            chunks (list): List of text chunks to summarize

        Returns:
            dict: Summarized text
        """
        chain = load_summarize_chain(
            llm=self.llm,
            chain_type="map_reduce",
            verbose=True
        )
        return chain.invoke(input=chunks)

    def process_video(self, url, method="direct"):
        """
        Complete pipeline to process a video: load, split, and summarize

        Args:
            url (str): YouTube video URL
            method (str): Loading method for YouTube content

        Returns:
            dict: Summarized video content
        """
        try:
            # Load content
            documents = self.load_youtube_content(url, method)
            if not documents:
                raise Exception("No content loaded from video")

            # Split text
            chunks = self.split_text(documents)
            if not chunks:
                raise Exception("No chunks created from documents")

            # Summarize
            summary = self.summarize_video(chunks)
            return summary

        except Exception as e:
            raise Exception(f"Error processing video: {str(e)}")