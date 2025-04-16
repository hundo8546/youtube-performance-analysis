# youtube-performance-analysis

This reposistory contains the code for building a dataset combing [YouTube8m data](https://research.google.com/youtube8m/) with metadata from the YouTube API, and analyzing the factors that contribute most to view count. There are three primary areas:
* `data_pipeline` - Python scripts to ingest YouTube8m data and fetch associated metadata from the YouTube API. 
* `analysis` - Jupyter Notebooks to explore and analyze the data for feature importance and generate SHAP csv.
* `dashboard` - Contains the HTML source for the interactive visualization.

# INSTALLATION

## Part 1: Data Pipeline

### Download YouTube8m data and build data pipeline environment
You must download YouTube8m data using [their instructions](https://research.google.com/youtube8m/download.html). Navigate to `data_pipeline/` and setup the environment:
```bash
make build # to build the virtual environment
```

## Part 2: Setup Analysis Environment
**Note:** You _must_ have run Part 1 for this to work. Otherwise there is no data available for analysis.

1) Navigate to `analysis`.
2) Build environment `make build`

## Part 3: Setup Visualization Environment

1) Navigate to `dashboard`
2) Build the environment `make build`

# EXECUTION
### YouTube8m data - Get Video IDs
After downloading YouTube8m records, process them to get the YouTube Video IDs. Navigate to `data_pipeline` and execute the following:

`make process TF_FILE=path/to/y8m/directory`

### Enrich with YouTube API data
Once the YouTube8m data with IDs is ready, enrich it with YouTube API data (including view count). **Note on rate limits:** The full data pipeline cannot be run at once due to rate limits. The API restrictions also only permit a limited number of requests per day. To build the dataset in this analysis, we fetched data daily over the course of several weeks.

Steps:

1) Create a YouTube API Key according to YouTube instructions, store it in the `YOUTUBE_API_KEY` environment variable. 
2) navigate to `data_pipeline/`
3) Run `make join` to join with YouTube API until quota is reached. This processes incrementally, so if you run it again on a subsequent day it picks up where it left off.

### Run Analysis of Joined Data
You must have run the previous steps to run this one. Navigate to `analysis/`. Start Jupyter Notebook `make notebook`. Open AnalysisOfViews.ipynb and run the full script. This will take quite some time to compute. This saves summary feature importance (SHAP values) to `../dashboard/`.

### Run Visualization of Data
**Note:** You can run this without running the earlier steps, because we've saved an example feature importance CSV within this codebase.

Steps: 

1) Navigate to `dashboard/`. 
3) Start the application `make server`
4) Open the visualization in your browser at the URL and port provided (probably [http://127.0.0.1:8050/](http://127.0.0.1:8050/))
