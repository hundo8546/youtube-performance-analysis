# youtube-performance-analysis

youtube-performance-analysis/
├── README.md                   # Project overview and instructions
├── .gitignore                  
|
|
├── data_pipeline/              # Data collection and processing
│   ├── youtube8m.py            # Processing YouTube8m to JSON
│   ├── youtube_data_api.py     # Fetching API data using Video IDs
│   ├── preprocessing.py        # Cleaning metadata, text analysis
│   └── config/                 # API keys(maybe needed)
├── modeling/                  
│   ├── clustering.py           # Clustering
│   ├── xgBoost.py              # XGBoost
|
├── dashboard/                  # Visualization
│   ├── app.py                  
│   └── visualizations.py
|   --assets                    #css elements?
