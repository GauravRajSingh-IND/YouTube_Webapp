from YouTube import YouTubeAnalyzer
import os

url="https://www.youtube.com/watch?v=h0DHDp1FbmQ&list=PLqZXAkvF1bPNQER9mLmDbntNfSpzdDIU5&index=10"
# Create an instance of YouTubeAnalyzer
analyzer = YouTubeAnalyzer(openai_api_key=os.getenv(key="OPENAI_API_KEY"))
response = analyzer.process_video(url=url, method="direct")
print(response['output_text'])
