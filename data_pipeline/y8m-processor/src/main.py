import datetime
import json
from numpyencoder import NumpyEncoder
from pathlib import Path
import re
import requests
import sys
import tensorflow as tf

Y8M_FEATURE_DESCRIPTION = {
    "id": tf.io.FixedLenFeature([], tf.string),  # YouTube-8M random ID, different from video ID but 1:1
    "labels": tf.io.VarLenFeature(tf.int64),    # List of video label numbers
    "mean_rgb": tf.io.FixedLenFeature([1024], tf.float32),  # Mean RGB features
    "mean_audio": tf.io.FixedLenFeature([128], tf.float32),  # Mean audio features
}

def parse_video_id(jsonp_input):
  """
  The JSONP format of the video ID pair is: 
  i("nXSc","0sf943sWZls");
  Rather than loading with another library it's easy to just parse with regexp
  """
  match = re.search(r'i\(".*?","(.*?)"\);', jsonp_input)
  if match:
      return match.group(1) # Youtube video ID is second item
  else:
      return None

def fetch_youtube_id(y8m_id):
  """
  Given a YouTube8m ID, fetch the YouTube video's ID from the mapping endpoint
  Details: https://research.google.com/youtube8m/video_id_conversion.html
  Note: documentation suggests HTTPS but server doesn't support it, and will raise an exception.
        Since we're not transmitting any sensitive data (only requesting IDs), use standard http.
  """
  base_url = "http://data.yt8m.org/2/j/i"
  directory_path = y8m_id[:2]  # First two characters are directory
  lookup_url = f"{base_url}/{directory_path}/{y8m_id}.js"
  try:
      response = requests.get(lookup_url)
      response.raise_for_status()
      video_id = parse_video_id(response.text)
      return video_id
  except Exception as e:
      #print(f"Request error for {lookup_url}: {e}")
      return None

def parse_example_record(serialized_example):
    """Parse a single TFRecord example and return a dictionary.
    """
    example = tf.io.parse_single_example(serialized_example, Y8M_FEATURE_DESCRIPTION)
    
    # The 4 character Youtube8m ID is not the same as the YouTubeID, which must be retrieved
    # from an endpoint mapping them together.
    y8m_id = example["id"].numpy().decode("utf-8")  # Convert bytes to string
    youtube_id = fetch_youtube_id(y8m_id)  # Get the real YouTube ID from the lookup function
    
    # Return the parsed details
    return {
        "youtube8m_id": y8m_id,
        "youtube_id": youtube_id,
        "url": f"https://www.youtube.com/watch?v={youtube_id}" if youtube_id is not None else "Not Found",
        "labels": list(example["labels"].values.numpy()),
    }


if __name__=="__main__":
  # Path to the TFRecord file, provided as commandline argument
  tfrecord_path = sys.argv[1]
  filename = Path(tfrecord_path).stem
  # Read the TFRecord dataset
  raw_dataset = tf.data.TFRecordDataset(tfrecord_path)
  count=0
  error_count = 0
  current_time = datetime.datetime.now()
  error_file_path = f"output/logs/errors_{filename}_{current_time.strftime('%H%M%S')}.log"
  output_data = []
  print(f"Starting count at {current_time.strftime('%H:%M:%S')}...")
  with open(error_file_path, "a") as errorfile:
    for video in raw_dataset:
        parsed_record = parse_example_record(video)
        if parsed_record["youtube_id"] is None:
            errorfile.write(f"{parsed_record['youtube8m_id']}\n")
            error_count += 1
        else:
            output_data.append(parsed_record)
        count+=1
    print(f"Checked {count} videos, {error_count} could not be retrieved ({float(error_count)/count*100} percent)")
    with open(f"output/data/{filename}.json", "w") as f:
        json.dump(output_data, f, ensure_ascii=False, cls=NumpyEncoder, indent=2)
        f.close()
