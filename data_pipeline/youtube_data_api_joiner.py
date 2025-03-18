from googleapiclient.discovery import build
import json
import os

# from numpyencoder import NumpyEncoder

API_KEY = os.environ.get("YOUTUBE_API_KEY")

if not API_KEY:
    raise ValueError("Set API_KEY environment variables")


class YTApiDataJoiner:
    _youtube = None

    def __init__(self, api_key):
        # Build the YouTube API client
        self._youtube = build("youtube", "v3", developerKey=api_key)

    def fetchVideoData(self, video_id):
        request = self._youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        )
        response = request.execute()

        # print(json.dumps(response, ensure_ascii=False, indent=2))

        if "items" not in response:
            return None
        if len(response["items"]) != 1:
            return None

        return response["items"][0]

    def joinWithYTApiData(self, input_file, output_file):
        data = []
        with open(input_file, "r") as f:
            content = f.read()
            # print(content)
            # print(len(content))
            data = json.loads(content)

        output_data = []
        error_videos = []

        for record in data:
            print("Processing ", record["url"])
            yt_api_data = self.fetchVideoData(record["youtube_id"])
            if not yt_api_data or ("snippet" not in yt_api_data):
                print("Data not found for ", record["youtube_id"])
                error_videos.append(record["url"])
                continue

            snippet_data = yt_api_data["snippet"]
            record["title"] = snippet_data.get("title")
            record["description"] = snippet_data.get("description")
            record["channel_title"] = snippet_data.get("channelTitle")
            record["publish_time"] = snippet_data.get("publishedAt")

            if "localized" in record:
                localized_data = snippet_data["localized"]
                record["localized_title"] = localized_data.get("title")
                record["localized_description"] = localized_data.get("description")


            record["tags"] = snippet_data.get("tags")

            if "statistics" in yt_api_data:
                stats = yt_api_data["statistics"]
                record["view_count"] = stats.get("viewCount")
                record["like_count"] = stats.get("likeCount")
                record["favorite_count"] = stats.get("favoriteCount")
                record["comment_count"] = stats.get("commentCount")

            output_data.append(record)

        print("Got {0} errors while fetching API data for videos".format(len(error_videos)))

        with open(output_file, "w") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            f.close()


if __name__ == "__main__":
    api_joiner = YTApiDataJoiner(API_KEY)
    api_joiner.joinWithYTApiData(input_file="train0093.json", output_file="train0093_out.json")
