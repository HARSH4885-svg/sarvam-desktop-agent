import os
import time
from playwright.sync_api import sync_playwright, BrowserContext, Page

class BrowserController:
    """Manages browser automation using Playwright with persistent user profile."""

    def __init__(self, user_data_dir: str = "browser_data"):
        self.user_data_dir = os.path.abspath(user_data_dir)
        os.makedirs(self.user_data_dir, exist_ok=True)
        self._playwright = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    def start(self):
        """Start Playwright and launch persistent browser context."""
        if self._context is not None:
            return self._page

        self._playwright = sync_playwright().start()
        # Launch with visible browser so user can see actions and authenticate if needed
        self._context = self._playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--disable-blink-features=AutomationControlled"]
        )
        if len(self._context.pages) > 0:
            self._page = self._context.pages[0]
        else:
            self._page = self._context.new_page()
        return self._page

    def get_current_page(self) -> Page:
        if not self._page or self._page.is_closed():
            return self.start()
        return self._page

    def open_website(self, url: str) -> dict:
        """Navigate to a website URL."""
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"
        page = self.get_current_page()
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        return {"status": "success", "url": page.url, "title": page.title()}

    def search_web(self, query: str) -> dict:
        """Search query on Google or YouTube."""
        page = self.get_current_page()
        search_url = f"https://www.google.com/search?q={requests_quote(query)}"
        page.goto(search_url, timeout=30000, wait_until="domcontentloaded")
        return {"status": "success", "query": query, "url": page.url, "title": page.title()}

    def get_open_browser_tabs(self) -> dict:
        """Return list of open browser tabs."""
        if not self._context:
            return {"status": "success", "tabs": []}
        tabs = []
        for i, p in enumerate(self._context.pages):
            try:
                tabs.append({"index": i, "title": p.title(), "url": p.url})
            except Exception:
                pass
        return {"status": "success", "tabs": tabs}

    def find_page_text(self, query: str) -> dict:
        """Check if specific text exists on current page."""
        page = self.get_current_page()
        try:
            content = page.content()
            found = query.lower() in content.lower()
            return {"status": "success", "query": query, "found": found}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def click_element(self, description: str) -> dict:
        """Click an element matching text, label, or role."""
        page = self.get_current_page()
        try:
            # Try text locator first
            loc = page.get_by_text(description, exact=False).first
            if loc.is_visible(timeout=3000):
                loc.click()
                return {"status": "success", "clicked": description}

            # Try button with name
            btn = page.get_by_role("button", name=description).first
            if btn.is_visible(timeout=2000):
                btn.click()
                return {"status": "success", "clicked": description}

            # Fallback to css selector if it looks like one
            if any(char in description for char in ["#", ".", "[", ">"]):
                page.locator(description).first.click(timeout=3000)
                return {"status": "success", "clicked": description}

            return {"status": "error", "error": f"Element '{description}' not found or not clickable."}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def fill_input(self, description: str, value: str) -> dict:
        """Fill input field matching label, placeholder, or selector."""
        page = self.get_current_page()
        try:
            # Try placeholder
            loc = page.get_by_placeholder(description).first
            if loc.is_visible(timeout=2000):
                loc.fill(value)
                return {"status": "success", "filled": description, "value": value}

            # Try label
            loc = page.get_by_label(description).first
            if loc.is_visible(timeout=2000):
                loc.fill(value)
                return {"status": "success", "filled": description, "value": value}

            # Try generic input
            loc = page.locator(description).first
            loc.fill(value)
            return {"status": "success", "filled": description, "value": value}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def upload_file(self, file_path: str) -> dict:
        """Upload a file to the currently active file input."""
        page = self.get_current_page()
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            return {"status": "error", "error": f"File does not exist: {abs_path}"}
        
        try:
            file_input = page.locator('input[type="file"]').first
            if file_input.count() > 0:
                file_input.set_input_files(abs_path)
                return {"status": "success", "uploaded": abs_path}
            return {"status": "error", "error": "No file input element found on the active page."}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # ==========================================
    # Google Classroom Specific Handlers
    # ==========================================

    def open_classroom(self) -> dict:
        """Open Google Classroom and verify login status."""
        page = self.get_current_page()
        page.goto("https://classroom.google.com", timeout=30000, wait_until="domcontentloaded")
        time.sleep(2)

        # Check if redirected to Google sign-in
        current_url = page.url
        if "accounts.google.com" in current_url:
            return {
                "status": "auth_required",
                "message": "Google Classroom requires sign-in. Please log in on the browser window. Your session will be saved for next time.",
                "url": current_url
            }

        return {"status": "success", "message": "Google Classroom opened successfully.", "url": current_url}

    def get_pending_classroom_assignments(self) -> dict:
        """List courses and pending assignments on Google Classroom."""
        page = self.get_current_page()
        if "classroom.google.com" not in page.url:
            self.open_classroom()
            time.sleep(2)

        # Navigate to To-Do tab
        try:
            page.goto("https://classroom.google.com/u/0/a/not-turned-in/all", timeout=20000, wait_until="domcontentloaded")
            time.sleep(3)
        except Exception:
            pass

        # Extract visible assignment titles and courses
        assignments = []
        try:
            # Google classroom to-do lists have assignments in cards or list items
            elements = page.locator("div[role='listitem'], div[data-item-id], a[href*='/c/']").all()
            for el in elements:
                try:
                    txt = el.inner_text().strip()
                    if txt and len(txt) < 300 and ("due" in txt.lower() or "assignment" in txt.lower() or "probability" in txt.lower() or "pns" in txt.lower()):
                        lines = [line.strip() for line in txt.split("\n") if line.strip()]
                        assignments.append({
                            "text": " | ".join(lines),
                            "title": lines[0] if lines else "Unknown Assignment"
                        })
                except Exception:
                    continue
        except Exception as e:
            return {"status": "error", "error": f"Failed reading assignments: {e}"}

        # If to-do page empty, check stream/course cards on home
        if not assignments:
            try:
                page.goto("https://classroom.google.com", timeout=20000, wait_until="domcontentloaded")
                time.sleep(2)
                cards = page.locator("div[role='listitem'], a[aria-label]").all()
                for c in cards:
                    text = c.inner_text().strip()
                    if text and len(text) < 200:
                        assignments.append({"text": text, "title": text.split("\n")[0]})
            except Exception:
                pass

        return {
            "status": "success",
            "count": len(assignments),
            "assignments": assignments[:10]  # Cap at top 10
        }

    def prepare_classroom_submission(self, assignment_query: str, file_path: str) -> dict:
        """Find the assignment, open it, and attach the specified file."""
        page = self.get_current_page()
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            return {"status": "error", "error": f"Attachment file not found: {abs_path}"}

        # 1. Search for matching assignment link
        found_link = None
        links = page.locator(f"text={assignment_query}").all()
        if links:
            found_link = links[0]
        else:
            # Try case-insensitive substring
            for a in page.locator("a, div[role='button']").all():
                try:
                    if assignment_query.lower() in a.inner_text().lower():
                        found_link = a
                        break
                except Exception:
                    pass

        if found_link:
            try:
                found_link.click()
                page.wait_for_load_state("domcontentloaded", timeout=15000)
                time.sleep(2)
            except Exception as e:
                return {"status": "error", "error": f"Could not open assignment: {e}"}

        # 2. Look for 'Add or create' button (+ button in Your work / Assigned section)
        add_btn = None
        for selector in [
            "button:has-text('Add or create')",
            "button:has-text('+ Add or create')",
            "div[role='button']:has-text('Add or create')",
            "button:has-text('Add')",
            "button[aria-label*='Add or create']"
        ]:
            loc = page.locator(selector).first
            if loc.is_visible(timeout=1500):
                add_btn = loc
                break

        if add_btn:
            add_btn.click()
            time.sleep(1)

        # 3. Look for file input or 'File' option in menu
        file_option = page.locator("span:has-text('File'), div[role='menuitem']:has-text('File')").first
        if file_option.is_visible(timeout=2000):
            file_option.click()
            time.sleep(2)

        # 4. Attach file via file input
        file_input = page.locator("input[type='file']").first
        if file_input.count() > 0:
            file_input.set_input_files(abs_path)
            time.sleep(3)
            return {
                "status": "prepared",
                "message": f"Attached '{os.path.basename(abs_path)}' to assignment '{assignment_query}'. Submission is prepared. Explicit confirmation is required before clicking Submit/Turn in.",
                "file": abs_path,
                "confirmation_required": True
            }

        return {
            "status": "prepared",
            "message": f"Opened assignment '{assignment_query}'. Please verify attachment of '{os.path.basename(abs_path)}'. Confirmation is required before turning in.",
            "file": abs_path,
            "confirmation_required": True
        }

    def submit_classroom_assignment(self, assignment_query: str) -> dict:
        """Click Turn in / Hand in after explicit user confirmation."""
        page = self.get_current_page()
        # Find Turn in / Hand in / Resubmit button
        submit_btn = None
        for selector in [
            "button:has-text('Turn in')",
            "button:has-text('Hand in')",
            "button:has-text('Submit')",
            "div[role='button']:has-text('Turn in')"
        ]:
            loc = page.locator(selector).first
            if loc.is_visible(timeout=2000):
                submit_btn = loc
                break

        if not submit_btn:
            return {"status": "error", "error": "Could not find 'Turn in' or 'Hand in' button on the current page."}

        submit_btn.click()
        time.sleep(1.5)

        # Handle confirmation dialog if Google Classroom displays a confirmation popup
        confirm_dialog_btn = page.locator("div[role='dialog'] button:has-text('Turn in'), div[role='dialog'] button:has-text('Hand in')").first
        if confirm_dialog_btn.is_visible(timeout=2000):
            confirm_dialog_btn.click()
            time.sleep(2)

        return {"status": "success", "message": f"Successfully submitted assignment '{assignment_query}'."}

    def close(self):
        """Close browser context."""
        try:
            if self._context:
                self._context.close()
            if self._playwright:
                self._playwright.stop()
        except Exception:
            pass


def requests_quote(text: str) -> str:
    import urllib.parse
    return urllib.parse.quote_plus(text)
