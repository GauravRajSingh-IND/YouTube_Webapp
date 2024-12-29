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
                analyzer = YouTubeAnalyzer(openai_api_key=os.getenv(key="OPENAI_API_KEY"))  # Replace with your key or load from .env
                summary = analyzer.process_video(url)['output_text']

                print(summary)
            except Exception as e:
                error_message = f"Error: {str(e)}"
        else:
            error_message = "Please provide a valid URL."

    return render_template("index.html", summary=summary, error_message=error_message)

if __name__ == "__main__":
    app.run()
