# Data-Res-Aview

## Streamlit App

This is a Streamlit web app that provides Youtube trend analysis for top channel by countries and specific channels

### Installation and Setup

1. Clone the repository: 

`git clone https://github.com/proudjiao/Data-Res-Aview.git`

2. Navigate to the project directory:

`cd [your-repo]`

3. Install packages automatically managed by pipenv using pipenv:

`pipenv install`

4. add a `secret.toml` file to folder `.streamlit`

In `secret.toml` file, add

`YOUTUBE_API_KEY = [YOUR API KEY HERE]`


## Usage

1. Run the Streamlit app:

`streamlit run home.py`

If more console outputs "module [\*] not found", install other required dependencies using pip:

`pip install -r [Whatever package is not installed]`

2. If app does not pop up automatically, access the app in your web browser by opening the provided URL (usually http://localhost:8501).


## Folder Structure

- `home.py`:  Main entry point of the Streamlit app.
- pages/                 # Folder containing subpages
  - Specific Channel.py ...               # Subpages end in .py

## Contact

jiaop24@g.ucla.edu


