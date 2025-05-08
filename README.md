# Facebook Comment Fetcher

A simple Python script that fetches users' comments, profile links, and direct comment links from a public Facebook post.

---

## Features

- Fetches all comments from a specified Facebook post  
- Retrieves each user's profile link  
- Retrieves direct links to each comment  

---

## Requirements

- [EditThisCookie Fork Extension](https://github.com/HackerTyper/Edit-This-Cookie) — for exporting Facebook cookies  
- [`uv`](https://github.com/astral-sh/uv) — for managing dependencies and running the script  
- Python 3.8+

---

## Setup Instructions

### 1. Export Facebook Cookies

Use the **EditThisCookie Fork** extension to export your Facebook cookies as `facebook.json`, and place it in the **root directory** of the project.

### 2. Install `uv`

If `uv` is not installed yet, run:

```bash
pip install uv
uv install 
uv sync
```

### 3. set the facebook Post ID `uv`
``` bash
POST_URL = "https://www.facebook.com/your_post_url_here"
```

### RUN THE SCRIPT
``` bash
uv run main.py
```