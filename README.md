# youtube-performance-analysis

This reposistory contains the code for building a dataset combing [YouTube8m data](https://research.google.com/youtube8m/) with metadata from the YouTube API, and analyzing the factors that contribute most to view count. There are three primary areas:
* `data_pipeline` - Python scripts to ingest YouTube8m data and fetch associated metadata from the YouTube API. 
* `exploratory_analysis` - Jupyter Notebooks to explore and analyze the data for feature importance.
* `dashboard` - Contains the HTML source for the interactive visualization.

# Part 1: Data Pipeline

## YouTube8m data
1) You must download YouTube8m data using [their instructions](https://research.google.com/youtube8m/download.html).
2) YouTube Video IDs are not in the raw download, you must extend it with video IDs using the y8m-processor script:
  * Navigate to `data_pipeline/`.
  * Run the following in a bash terminal:
```bash
make build # to build the virtual environment
make process TF_FILE=path/to/y8m/directory
```

## YouTube API data enrichment
Once the YouTube8m data with IDs is ready, enrich it with YouTube API data (including view count). **Note on rate limits:** The full data pipeline cannot be run at once due to rate limits. The API restrictions also only permit a limited number of requests per day. To build the dataset in this analysis, we fetched data daily over the course of several weeks.

Steps:

1) Create a YouTube API Key according to YouTube instructions, store it in the `YOUTUBE_API_KEY` environment variable. 
2) navigate to `data_pipeline/`
3) Run `make join` to join with YouTube API until quota is reached. This processes incrementally, so if you run it again on a subsequent day it picks up where it left off.

# Part 2: Data Analysis and Modeling
**Note:** You _must_ have run Part 1 for this to work. Otherwise there is no data available for analysis.

1) Navigate to `analysis`.
2) Build environment `make build`
3) Start Jupyter Notebook `make notebook`
4) Open AnalysisOfViews.ipynb and run it.

This saves summary feature importance (SHAP values) to `../dashboard/`.

# Part 3: Visualization
**Note:** You can run this without running the earlier steps, because we've saved an example feature importance CSV within this codebase.

1) Navigate to `dashboard`
2) Build the environment `make build`
3) Start the application `make server`
4) Open the visualization in your browser at the URL and port provided (probably [http://127.0.0.1:8050/](http://127.0.0.1:8050/))

