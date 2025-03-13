# Flask Image Gallery



A simple web gallery to view and manage AI-generated images. Supports searching by prompt, filtering by tags, and adding/removing tags.

## Features
- Displays images stored in `static/images/`
- Reads metadata from `database.json`
- Search by prompt or filter by tags
- Add and remove tags dynamically
- **Fetcher script** to automate JSON updates
  
## Run the app: Double-click **`run.bat`**

## JSON Database & Fetcher Script
- The app uses `database.json` to store image metadata.
- The **fetcher script (`fetcher.py`)** scans new images and JSON metadata from `imagefx/json/` and `imagefx/jpg/`.
- **New JSON entries must be manually added to the database** after running the fetcher.

### Running the Fetcher:
- Ensure the **Google ImageFX Downloader** used and downloaded images and JSON files.
- This will generate a **`combined.json`** file, which needs to be manually added to `database.json`.

## Notes
- The **`run.bat`** script:
  - Activates the virtual environment.
  - Starts the Flask app.
  - Opens the gallery in your browser automatically.
- The **fetcher script must be run separately** from the Flask app.

## Google ImageFX Downloader
- [Google ImageFX Automation](https://github.com/onurakay/googleimagefx-downloader) - Tampermonkey script to automate image downloads.
