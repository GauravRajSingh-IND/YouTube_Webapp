from dotenv import load_dotenv
from pytubefix import YouTube
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
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")
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
                # Method 3: Use pytubefix directly
                try:
                    yt = YouTube(url)
                    if 'en' in yt.captions:
                        transcript = yt.captions['en']
                    elif yt.captions:
                        transcript = next(iter(yt.captions.values()))
                    else:
                        raise ValueError("No captions available for this video")

                    text = transcript.generate_srt_captions()
                    return [{"page_content": text, "metadata": {"title": yt.title, "url": url}}]
                except Exception as e:
                    raise ValueError(f"Error retrieving captions: {str(e)}")

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

    def process_video(self, url):
        """
        Complete pipeline to process a video: load, split, and summarize.
        Tries multiple methods to load content until one succeeds.

        Args:
            url (str): YouTube video URL

        Returns:
            dict: Summarized video content
        """
        methods = ["direct", "alternative", "pytube"]  # Available methods
        documents = None

        # Try each method until one succeeds
        for method in methods:
            try:
                # Load content using the current method
                documents = self.load_youtube_content(url, method)
                if documents:
                    print(f"Successfully loaded content using method: {method}")
                    break  # Exit the loop if content is successfully loaded
            except Exception as e:
                # If a method fails, log the error and try the next method
                print(f"Method '{method}' failed: {str(e)}")

        # If no content is loaded after trying all methods, raise an error
        if not documents:
            raise Exception("Failed to load content from video using any method")

        try:
            # Split text
            chunks = self.split_text(documents)
            if not chunks:
                raise Exception("No chunks created from documents")

            # Summarize
            summary = self.summarize_video(chunks)
            return summary

        except Exception as e:
            raise Exception(f"Error processing video: {str(e)}")
