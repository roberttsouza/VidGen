# VidGen

VidGen is an automated video generation system designed to create engaging videos. It leverages various APIs and tools to generate videos from different data sources.

## Overview

This project automates the process of creating videos by:

- Fetching news headlines from a news API.
- Generating images using a text-to-image API.
- Converting text to speech.
- Combining these elements into a final video.

## Setup

### Prerequisites

- Python 3.6+
- pip
- FFmpeg (for video editing)

### Installation

1.  Clone the repository:

    ```bash
    git clone https://github.com/your-username/VidGen.git
    cd VidGen
    ```

2.  Create a virtual environment (recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4.  Set up API keys:

    -   Obtain API keys from the following services:
        -   News API (e.g., NewsAPI)
        -   Pexels API
        -   YouTube API
    -   Create a `.env` file in the project root and add your API keys:

        ```
        NEWS_API_KEY=your_news_api_key
        PEXELS_API_KEY=your_pexels_api_key
        YOUTUBE_API_KEY=your_youtube_api_key
        ```

    -   **Note:** Ensure that the `.env` file is added to your `.gitignore` to prevent accidental commits of your API keys.

### Configuration

-   Modify the `src/config.py` file to adjust settings such as:
    -   Video resolution
    -   Frame rate
    -   Audio settings
    -   Text-to-speech voice

## Usage

1.  Run the `app.py` script:

    ```bash
    python app.py
    ```

2.  The script will:
    -   Fetch news headlines.
    -   Generate images for each headline.
    -   Convert the headlines to speech.
    -   Create a video from the generated content.
    -   Upload the video to YouTube (optional).

## Project Structure

```
VidGen/
├── .env                    # API keys and configuration
├── app.py                  # Main application script
├── README.md               # Project documentation
├── requirements.txt        # Project dependencies
├── data/                   # Directory for generated data
│   ├── audio/              # Audio files
│   ├── images/             # Image files
│   └── videos/             # Video files
├── logs/                   # Log files
│   └── crypto_caster.log   # Application log
├── src/                    # Source code
│   ├── config.py           # Configuration settings
│   ├── main.py             # Main script for video generation
│   ├── apis/               # API clients
│   │   ├── news_api.py     # News API client
│   │   ├── pexels_api.py   # Pexels API client
│   │   └── youtube_api.py  # YouTube API client
│   ├── utils/              # Utility functions
│   │   ├── helpers.py      # Helper functions
│   │   ├── text_to_speech.py # Text-to-speech functionality
│   │   └── video_creator.py  # Video creation functionality
└── .gitignore              # Specifies intentionally untracked files that Git should ignore
```

## Dependencies

-   `requests`: For making HTTP requests to APIs.
-   `gTTS`: For text-to-speech conversion.
-   `moviepy`: For video editing.
-   `google-api-python-client`: For interacting with the YouTube API.
-   `python-dotenv`: For loading environment variables from the `.env` file.

## Contributing

Contributions are welcome! Please submit a pull request with your changes.

## License

[MIT](LICENSE)
