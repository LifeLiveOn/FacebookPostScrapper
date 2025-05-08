Facebook Comment Fetcher
This is a simple Python script that allows you to fetch users' comments, their profile links, and their comment links from a Facebook post.

Features
Fetches all comments from a specified Facebook post

Retrieves each user's profile link

Retrieves direct links to each comment

Requirements
EditThisCookie Fork Extension (to export your Facebook cookies)

uv (for managing dependencies and running the script)

Python 3.10+

Setup Instructions
Export Facebook Cookies
Use the EditThisCookie Fork extension to export your Facebook cookies as facebook.json.
Place this file in the root directory of the project.

Install uv
If you don't have uv installed, run:

bash
pip install uv
Install Dependencies
Use uv to install all dependencies:

bash
uv install
uv sync
Set the Facebook Post ID
Open main.py and set the POST_URL variable to your desired Facebook post ID.

Run the Script
Execute the script using:

bash
uv run main.py