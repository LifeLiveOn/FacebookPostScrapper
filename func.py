import time
from urllib.parse import urlparse, parse_qs, unquote
from dateutil import parser
import base64
import re
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd

def extract_comment_id(full_url):
    """
    Extracts the actual comment ID from a Facebook comment URL.

    This function decodes the base64-encoded `comment_id` parameter
    and retrieves the comment's numeric or alphanumeric ID.

     comment ID is expected to be in the format "comment:POSTID_COMMENTID".
    Args:
        full_url (str): The full URL containing the encoded comment ID.

    Returns:
        (commentId) or None: The extracted comment ID if found, otherwise None.
    """
    try:
        parsed = urlparse(full_url)
        qs = parse_qs(parsed.query)
        encoded = qs.get("comment_id", [None])[0]
        if not encoded:
            return None

        decoded = base64.b64decode(encoded).decode('utf-8')
        # Expecting format: "comment:POSTID_COMMENTID"
        match = re.search(r'comment:\d+_(\d+)', decoded)
        return match.group(1) if match else None
    except Exception as e:
        print("Error decoding comment_id:", e)
        return None
    

def extract_username_from_url(url):
    """
    Extracts the username or ID from a Facebook profile URL.

    Handles both standard usernames (e.g., facebook.com/username)
    and numeric ID-based URLs (e.g., facebook.com/profile.php?id=123456789).

    Args:
        url (str): The full URL of the Facebook profile.

    Returns:
        str: The extracted username or ID.
    """
    try:
        parsed = urlparse(url)
        if "profile.php" in parsed.path:
            # Handle ID-based profile
            user_id = parse_qs(parsed.query).get("id", [""])[0]
            return f"id_{user_id}" if user_id else "N/A"
        else:
            # Username-based profile
            return parsed.path.strip("/").split("/")[0]
    except:
        return ""
    

def find_scrollable_parent(driver,element):
    """
    Finds the nearest scrollable parent of a given element by checking computed styles.

    This function traverses up the DOM from the given element to find the first parent
    with scrollable overflow behavior (e.g., 'auto' or 'scroll').

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        element (WebElement): The starting element to search from.

    Returns:
        WebElement or None: The first scrollable parent element found, or None if none exist.
    """
    return driver.execute_script("""
        let el = arguments[0];
        while (el && el !== document.body) {
            const style = window.getComputedStyle(el);
            if (el.scrollHeight > el.clientHeight &&
                (style.overflowY === 'auto' || style.overflowY === 'scroll')) {
                return el;
            }
            el = el.parentElement;
        }
        return null;
    """, element)


def switch_to_all_comments(wait):
    """
    Switches the comment sorting to 'Tất cả bình luận' (All comments).

    This changes the view from 'Phù hợp nhất' (Most relevant) to show all comments,
    ensuring full visibility. Assumes the user is already on the Facebook post page.

    Args:
        wait (WebDriverWait): The WebDriverWait instance used to wait for clickable elements.

    Returns:
        None
    """
    try:
   # Click the "Phù hợp nhất" dropdown
        sort_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(text(), 'Phù hợp nhất')]/ancestor::div[@role='button']")
        ))
        sort_button.click()
        print("Clicked the 'Phù hợp nhất' button.")
    except Exception as e:
        print("Could not click 'Phù hợp nhất':", e)
    try:
    # Wait for the dropdown to appear and click "Tất cả bình luận"
        all_comments_option = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(text(), 'Tất cả bình luận')]")
        ))
        all_comments_option.click()
        print("Switched to 'Tất cả bình luận'.")
    except Exception as e:
        print("Could not select 'Tất cả bình luận':", e)
    return None




# --- Helpers ---

def expand_see_more_buttons(driver, comment_container):
    """
    Expands all truncated comments by clicking on 'Xem thêm' buttons within the comment container.

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance used to execute JavaScript clicks.
        comment_container (WebElement): The HTML element that contains all comment elements.
    
    Returns:
        None
    """
    see_more_buttons = comment_container.find_elements(By.XPATH, ".//span[contains(text(), 'Xem thêm')]")
    for btn in see_more_buttons:
        try:
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.5)
        except:
            pass  # Safe fail if button isn't clickable


def extract_comment_data(comment, POST_URL):
    """
    Extracts profile link, username, numeric response, and comment link from a single comment element.

    Args:
        comment (WebElement): The HTML element representing one comment.
        POST_URL (str): The URL of the Facebook post, used to construct the full comment link.

    Returns:
        List[str]: A list containing:
            - profile_link (str): URL to the user's profile.
            - username (str): Username extracted from the profile URL.
            - response_int (str): Digits found in the comment text.
            - comment_link (str): Direct link to the specific comment.
    """
    profile_link = ""
    username = ""
    comment_text = ""
    comment_link = ""
    response_int = ""

    # Profile link and username
    try:
        profile_elem = comment.find_element(By.XPATH, ".//a[@role='link' and contains(@href, 'facebook.com')]")
        profile_link = profile_elem.get_attribute("href")
        username = extract_username_from_url(profile_link)

        # Extract comment ID from link
        comment_links = comment.find_elements(By.XPATH, ".//a[contains(@href, 'comment_id=')]")
        for link in comment_links:
            href = link.get_attribute("href")
            comment_id = extract_comment_id(href)
            if comment_id:
                comment_link = f"{POST_URL}?comment_id={comment_id}"
                break
    except Exception:
        pass

    # Comment text and response_int
    try:
        text_elems = comment.find_elements(By.XPATH, ".//div[@dir='auto']")
        comment_text = "\n".join([e.text.strip() for e in text_elems if e.text.strip()])
        digits = re.findall(r'\d+', comment_text)
        response_int = ''.join(digits) if digits else "N/A"
    except Exception:
        comment_text = ""
        response_int = "N/A"

    return [profile_link, username, comment_text, response_int, comment_link]



def process_all_comments(driver, comment_container, POST_URL):
    """
    Extracts data from all comments within the given container.

    Expands truncated comments, parses user profile links, usernames,
    comment text, and comment IDs to generate structured comment data.

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        comment_container (WebElement): The container element holding all comments.
        POST_URL (str): The base URL of the Facebook post (used to construct comment links).

    Returns:
        List[List[str]]: A list of comment data, where each entry contains:
                         [profile_link, username, response_int, comment_link].
    """
    expand_see_more_buttons(driver, comment_container)
    comments = comment_container.find_elements(By.XPATH, ".//div[@role='article']")
    print(f"Found {len(comments)} comments.")
    
    data = []
    for comment in comments:
        try:
            data.append(extract_comment_data(comment, POST_URL))
        except Exception as e:
            print("Error processing comment:", e)
    
    return data


def clean_and_save_comments(data, output_path):
    """
    Cleans comment data and saves it to a CSV file.

    - Removes rows with empty fields (except Response)
    - Deduplicates entries
    - Resets index
    - Saves as UTF-8 with BOM for Excel compatibility
    """
    df = pd.DataFrame(data, columns=[
        "User Profile", "Username", "Comment Text", "Response (int)", "Comment Link"
    ])
    df = df.dropna()
    df = df[~df[["User Profile", "Username", "Comment Text", "Comment Link"]].isin(["", "N/A"]).any(axis=1)]
    df = df.drop_duplicates(subset=[
        "User Profile", "Username", "Comment Text", "Response (int)", "Comment Link"
    ], keep='first')
    df = df.reset_index(drop=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
