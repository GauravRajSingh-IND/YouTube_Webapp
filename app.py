from flask import Flask, render_template, request
import os
from YouTube import YoutubeAnalyzer

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home_page():
    content = None
    error_message = None

    if request.method == "POST":
        url = request.form["url"]
        print(f"Received URL: {url}")  # Debug print

        if url:
            try:
                api_key = os.getenv("OPENAI_API_KEY")
                analyzer = YoutubeAnalyzer(url=url)
                content = analyzer.load_content()
                print(f"Content received: {content}")  # Debug print

                # If content is None or empty, set an error message
                if not content:
                    error_message = "No content was retrieved from the video."
                    print("Content is empty")  # Debug print

            except Exception as e:
                error_message = f"Error: {str(e)}"
                print(f"Error processing video: {str(e)}")  # Debug print
        else:
            error_message = "Please provide a valid URL."
            print("Empty URL provided")  # Debug print

    print(f"Rendering template with content: {content}")  # Debug print
    return render_template("index.html", content=content, error_message=error_message)


if __name__ == "__main__":
    app.run()