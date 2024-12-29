from flask import Flask, render_template, request
from YouTube import YouTubeAnalyzer
import os

# Create a Flask app
app = Flask(__name__)


# Create home page route
@app.route("/", methods=["GET", "POST"])
def home_page():
    summary = None
    error_message = None

    if request.method == "POST":
        # Get the URL submitted by the user
        url = request.form["url"]

        # Check if URL is valid
        if url:
            try:
                # Use the YouTubeAnalyzer to summarize the content
                api_key = os.getenv("OPENAI_API_KEY")  # Ensure correct retrieval of the API key
                analyzer = YouTubeAnalyzer(openai_api_key=api_key)

                # Process the video and get the summary
                result = analyzer.process_video(url)

                # You can format the result here if needed
                summary = result.get('output_text', 'No summary found')  # Assuming the result has 'output_text'

                print(summary)  # Optionally log the summary for debugging
            except Exception as e:
                error_message = f"Error: {str(e)}"
                print(f"Error processing video: {str(e)}")  # Log error for debugging
        else:
            error_message = "Please provide a valid URL."

    return render_template("index.html", summary=summary, error_message=error_message)


if __name__ == "__main__":
    app.run()  # Enable debug mode for easier troubleshooting during development
