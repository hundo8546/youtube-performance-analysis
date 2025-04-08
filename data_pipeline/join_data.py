# Script to orchestrate the join of y8m-processor output with data from the Youtube APIs
# using YTApiDataJoiner.
# Requires an environment variable called YOUTUBE_API_KEY with a valid API key.

import json
import os
from pathlib import Path
import sys

sys.path.append(os.path.abspath("."))
from youtube_data_api_joiner import YTApiDataJoiner
API_KEY = os.environ.get("YOUTUBE_API_KEY")
yt_joiner = YTApiDataJoiner(API_KEY)
y8m_data_dir = Path("y8m-processor/output/data")
for json_file in y8m_data_dir.glob("*.json"):
    output_file = f"output/data/{json_file.name}"
    if not os.path.isfile(output_file):
      yt_joiner.joinWithYTApiData(input_file=json_file, output_file=output_file)
    else:
       print(f"{json_file.name} already processed, skipping")
