# Video-Summarization-Using-Transformer

This project aims to provide a solution for video summarization using Natural Language Processing (NLP) techniques. The project utilizes popular libraries such as `youtube_dl`, `transformer`, and `moviepy` to download videos, extract key information, and generate a summarized version of the video.

## Requirements

- Python 3.6 or higher
- `youtube_dl` library
- `transformer` library
- `moviepy` library

## Installation

1. Clone the project repository:

```
git clone https://github.com/Pragyan02/Video-Summarization-Using-Transformer.git
```

2. Install the required libraries using pip:

```
pip install requirements.txt
```

## Usage

1. Obtain the YouTube video URL.

2. Run the `video_summarization.py` script:

```
python video_summarization.py --video_url <url> --output_path <path for output file> --keep_original_file <True or False>
```

Replace `<video_url>` with the URL of the YouTube video.

3. The script will download the video and extract the subtitle text. Then, it will perform extractive summarization using the transformer-based model.

4. After the summarization process completes, a summarized version of the video will be generated using `moviepy`. The output video will be saved in the project directory.

## Acknowledgments

- The `youtube_dl` library is used for downloading the YouTube video. For more information about the library, visit: [https://github.com/ytdl-org/youtube-dl](https://github.com/ytdl-org/youtube-dl)

- The `transformer` library is used for extractive summarization. It provides pre-trained transformer models for natural language processing tasks. For more information about the library, visit: [https://github.com/huggingface/transformers](https://github.com/huggingface/transformers)

- The `moviepy` library is used for video editing and generating the summarized version of the video. For more information about the library, visit: [https://github.com/Zulko/moviepy](https://github.com/Zulko/moviepy)

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.
