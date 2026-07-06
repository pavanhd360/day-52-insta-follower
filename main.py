import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException

# ==================== GLOBAL VARIABLES ====================
TARGET_ACCOUNT = "insta account you wanna follow"
MAX_FOLLOWS = 5

# Local path for preserving login sessions
PROFILE_PATH = os.path.join(os.getcwd(), "instagram_profile")


# ==========================================================

class InstaFollower:

    def __init__(self):
        """Initializes Chrome cleanly with only essential arguments to prevent crashes."""
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(f"--user-data-dir={PROFILE_PATH}")

        # Windows stability flags to prevent ntdll crashes
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        print(f"[*] Opening browser using profile at: {PROFILE_PATH}")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 12)

    def check_login_status(self):
        """Navigates to Instagram and checks if your session is active."""
        print("[*] Loading Instagram...")
        self.driver.get("https://www.instagram.com/")
        time.sleep(6)

        try:
            self.driver.find_element(By.CSS_SELECTOR, "svg[aria-label='Home']")
            print("[+] Session verified! You are logged in.")
            return True
        except Exception:
            print("\n[!] No active session detected.")
            print("[!] ACTION REQUIRED: Log in manually inside the browser window now.")
            input("[!] Once you see your home feed, come back here and press ENTER... ")
            return False

    def find_followers(self):
        """Navigates to the target account and opens the followers popup cleanly."""
        print(f"[*] Navigating straight to: https://www.instagram.com/{TARGET_ACCOUNT}/")
        self.driver.get(f"https://www.instagram.com/{TARGET_ACCOUNT}/")

        # Give the profile page plenty of time to fully render
        time.sleep(6)

        print("[*] Clicking the followers link...")

        # Advanced broad selectors to catch links, text boxes, or spans containing 'followers'
        selectors = [
            (By.XPATH, "//*[contains(text(), 'followers') or contains(text(), 'Followers')]"),
            (By.XPATH, "//a[contains(@href, 'followers')]"),
            (By.CSS_SELECTOR, "a[href*='followers']")
        ]

        followers_link = None
        for by_method, locator in selectors:
            try:
                followers_link = self.wait.until(
                    EC.element_to_be_clickable((by_method, locator))
                )
                if followers_link:
                    break
            except TimeoutException:
                continue

        if followers_link:
            try:
                followers_link.click()
                print("[+] Followers window opened automatically.")
                time.sleep(4)
                return
            except Exception:
                self.driver.execute_script("arguments[0].click();", followers_link)
                print("[+] Followers window opened via JS fallback.")
                time.sleep(4)
                return

        # Emergency manual fallback option if all else fails
        print("\n[-] Could not locate the button automatically.")
        print("[!] ACTION REQUIRED: Click the 'followers' link manually on the Chrome screen right now.")
        input("[!] Once the popup list of names is visible, press ENTER here to start following... ")

    def follow(self):
        """Locates the scroll list using universal dialog selectors and clicks Follow buttons."""
        print("[*] Finding the scrollable modal wrapper...")

        try:
            # 1. Target the absolute main popup dialog frame wrapper
            dialog_box = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='dialog']"))
            )

            # 2. Find the actual internal scrollable container div inside that dialog box
            try:
                modal_container = dialog_box.find_element(By.XPATH,
                                                          ".//div[contains(@style, 'overflow-y: auto') or contains(@style, 'overflow: auto')]")
                print("[+] Target scroll container hooked successfully.")
            except Exception:
                # Fallback directly to the dialog frame itself if sub-div structure shifts
                modal_container = dialog_box
                print("[*] Using primary dialog frame as scroll container.")

        except TimeoutException:
            print("[-] Fatal: Could not find the popup dialog box on screen. Ensure the list is open.")
            return

        followed_count = 0

        while followed_count < MAX_FOLLOWS:
            # Gather all buttons inside our active dialog box frame
            all_buttons = dialog_box.find_elements(By.TAG_NAME, "button")

            # Filter to keep ONLY active, visible buttons that match the word 'Follow' exactly
            follow_buttons = [
                btn for btn in all_buttons
                if btn.text == "Follow" and btn.is_displayed()
            ]

            if not follow_buttons:
                print("[-] Out of visible targets. Scrolling down to load more rows...")
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal_container)
                time.sleep(3)
                continue

            for button in follow_buttons:
                if followed_count >= MAX_FOLLOWS:
                    break

                try:
                    # Scroll smoothly to the individual button element to ensure visibility
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                    time.sleep(random.uniform(1.5, 2.5))

                    button.click()
                    followed_count += 1
                    print(f"[+] Followed account ({followed_count}/{MAX_FOLLOWS})")

                    # Essential human pacing wait window to protect account reputation
                    delay = random.uniform(20, 30)
                    print(f"[*] Pacing... sleeping for {delay:.1f} seconds...")
                    time.sleep(delay)

                except ElementClickInterceptedException:
                    self.driver.execute_script("arguments[0].click();", button)
                    followed_count += 1
                    time.sleep(random.uniform(20, 30))
                except Exception:
                    continue

            # Scroll container down to update DOM row rendering batch chunks
            try:
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal_container)
                time.sleep(4)
            except Exception:
                break

        print(f"[SUCCESS] Finished! Total new follows processed: {followed_count}")


if __name__ == "__main__":
    bot = InstaFollower()
    bot.check_login_status()
    bot.find_followers()
    bot.follow()