from langchain_community.document_loaders import YoutubeLoader

class YoutubeAnalyzer:
    def __init__(self, url):
        self.url=url

    def load_content(self):
        loader = YoutubeLoader.from_youtube_url(youtube_url=self.url,
                                        add_video_info=False,
                                        )
        response= loader.load()
        return response[0].page_content