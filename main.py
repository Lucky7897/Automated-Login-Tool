import os
import json
import sys
import subprocess
import logging
import random
import time
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit, QFileDialog, QTextEdit, QCheckBox, QMessageBox, QInputDialog, QComboBox
from PyQt5.QtCore import Qt
from playwright.sync_api import sync_playwright

# List of required modules
REQUIRED_MODULES = [
    'PyQt5',
    'playwright'
]

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except subprocess.CalledProcessError as e:
        print(f"Error installing package {package}: {e}")

def check_and_install_modules():
    for package in REQUIRED_MODULES:
        try:
            __import__(package)
        except ImportError:
            print(f"Module {package} not found. Installing...")
            install_package(package)
        else:
            print(f"Module {package} is already installed.")

# Ensure all required modules are available
check_and_install_modules()

# Playwright installation (after the module is verified)
try:
    from playwright.sync_api import sync_playwright
    # Install browser binaries for Playwright if necessary
    subprocess.run([sys.executable, "-m", "playwright", "install"], check=True)
except Exception as e:
    print(f"Error during Playwright setup: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LoginAutomationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.script_data = None
        self.show_initial_popup()

    def init_ui(self):
        self.setWindowTitle("Automated Login with Proxy and File Input")
        self.setGeometry(100, 100, 600, 500)

        # Layout
        layout = QVBoxLayout()

        # Login URL input
        self.url_label = QLabel("Login URL:")
        self.url_input = QLineEdit(self)
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)

        # Proxy input
        self.proxy_label = QLabel("Proxy Type:")
        self.proxy_type = QComboBox(self)
        self.proxy_type.addItems(["None", "HTTP", "SOCKS5"])
        layout.addWidget(self.proxy_label)
        layout.addWidget(self.proxy_type)

        self.proxy_input_label = QLabel("Proxy Address (Optional):")
        self.proxy_input = QLineEdit(self)
        layout.addWidget(self.proxy_input_label)
        layout.addWidget(self.proxy_input)

        # File selection for credentials
        self.file_label = QLabel("Credentials File (username:password):")
        self.file_path = QLineEdit(self)
        self.file_button = QPushButton("Browse", self)
        self.file_button.clicked.connect(self.open_file_dialog)
        layout.addWidget(self.file_label)
        layout.addWidget(self.file_path)
        layout.addWidget(self.file_button)

        # Success selector input
        self.success_label = QLabel("Success Element Selector (Optional):")
        self.success_input = QLineEdit(self)
        layout.addWidget(self.success_label)
        layout.addWidget(self.success_input)

        # Debug mode checkbox
        self.debug_checkbox = QCheckBox("Enable Debug Mode")
        layout.addWidget(self.debug_checkbox)

        # Start button
        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_login_process)
        layout.addWidget(self.start_button)

        # Make script button
        self.make_script_button = QPushButton("Make Script", self)
        self.make_script_button.clicked.connect(self.start_script_maker)
        layout.addWidget(self.make_script_button)

        # Import script button
        self.import_script_button = QPushButton("Import Script", self)
        self.import_script_button.clicked.connect(self.import_script)
        layout.addWidget(self.import_script_button)

        # Output log area
        self.log_area = QTextEdit(self)
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        self.setLayout(layout)

    def open_file_dialog(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Credentials File", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_path:
            self.file_path.setText(file_path)

    def log(self, message):
        self.log_area.append(message)
        self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())

    def random_delay(self, min_delay=1, max_delay=3):
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

    def show_initial_popup(self):
        message = (
            "Welcome to the Automated Login Tool!\n\n"
            "This tool allows you to automate login processes by capturing user interactions and generating scripts.\n\n"
            "Please follow these steps:\n"
            "1. Click 'Make Script' to start the script maker mode.\n"
            "2. Perform the login steps manually.\n"
            "3. Click 'Save Script' when done.\n"
            "4. Import the generated script and use it for automated login processes.\n\n"
            "Enjoy using the tool!"
        )
        QMessageBox.information(self, "Welcome", message)

    def start_script_maker(self):
        self.log("Starting script maker mode...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            # Listen for user interactions
            self.script_data = {
                "url": "",
                "actions": []
            }

            def on_navigation(request):
                self.script_data["url"] = request.url

            def on_click(element):
                self.script_data["actions"].append({
                    "type": "click",
                    "selector": page.evaluate("(element) => element.getAttribute('data-testid') || element.getAttribute('id') || element.getAttribute('class')", element)
                })

            def on_input_change(element):
                self.script_data["actions"].append({
                    "type": "fill",
                    "selector": page.evaluate("(element) => element.getAttribute('data-testid') || element.getAttribute('id') || element.getAttribute('class')", element),
                    "value": page.evaluate("(element) => element.value", element)
                })

            page.on("framenavigated", on_navigation)
            page.on("click", on_click)
            page.on("input", on_input_change)

            # Open a blank page and let the user interact with it
            page.goto("about:blank")
            self.log("Please perform the login steps manually. Press 'Save Script' when done.")

            # Add a button to save the script
            page.evaluate("""() => {
                const button = document.createElement('button');
                button.innerText = 'Save Script';
                button.style.position = 'fixed';
                button.style.top = '10px';
                button.style.right = '10px';
                button.style.zIndex = '9999';
                document.body.appendChild(button);
                button.addEventListener('click', () => {
                    window.saveScript = true;
                });
            }""")

            while not page.evaluate("() => window.saveScript"):
                time.sleep(1)

            self.save_script(page, browser)

    def save_script(self, page, browser):
        # Save the script data to a JSON file
        script_path = os.path.join(os.getcwd(), "login_script.json")
        with open(script_path, "w") as f:
            json.dump(self.script_data, f, indent=4)

        self.log(f"Script saved to {script_path}")

        # Generate a Python script based on the captured interactions
        self.generate_python_script(script_path)

        # Close the browser
        browser.close()

    def generate_python_script(self, script_path):
        # Load the script data
        with open(script_path, "r") as f:
            script_data = json.load(f)

        # Generate the Python script
        python_script = f"""
from playwright.sync_api import sync_playwright

def perform_login(username, password):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("{script_data["url"]}")

        # Perform the captured actions
"""

        for action in script_data["actions"]:
            if action["type"] == "click":
                python_script += f'        page.click("{action["selector"]}")\n'
            elif action["type"] == "fill":
                if "username" in action["selector"]:
                    python_script += f'        page.fill("{action["selector"]}", username)\n'
                elif "password" in action["selector"]:
                    python_script += f'        page.fill("{action["selector"]}", password)\n'
                else:
                    python_script += f'        page.fill("{action["selector"]}", "{action["value"]}")\n'

        python_script += "\n        browser.close()\n"

        # Save the Python script to a file
        python_script_path = os.path.join(os.getcwd(), "login_script.py")
        with open(python_script_path, "w") as f:
            f.write(python_script)

        self.log(f"Python script generated and saved to {python_script_path}")

    def import_script(self):
        options = QFileDialog.Options()
        script_path, _ = QFileDialog.getOpenFileName(self, "Open Script File", "", "JSON Files (*.json);;All Files (*)", options=options)
        if script_path:
            self.script_data = json.load(open(script_path, "r"))
            self.log(f"Script imported from {script_path}")

    def start_login_process(self):
        login_url = self.url_input.text()
        proxy_type = self.proxy_type.currentText()
        proxy_address = self.proxy_input.text() or None
        credentials_file = self.file_path.text()
        success_selector = self.success_input.text() or None
        debug_mode = self.debug_checkbox.isChecked()

        # Validate fields
        if not login_url:
            self.show_error("Please enter a login URL.")
            return

        credentials = []
        if credentials_file:
            try:
                with open(credentials_file, 'r') as file:
                    credentials = [line.strip().split(":") for line in file if line.strip()]
            except FileNotFoundError:
                self.show_error("Error: Credentials file not found.")
                return
            except Exception as e:
                self.show_error(f"Error reading credentials file: {e}")
                return

        # Perform login for each username:password pair
        if self.script_data:
            self.perform_logins_with_script(login_url, credentials, proxy_type, proxy_address, success_selector, debug_mode)
        else:
            self.perform_logins(login_url, credentials, proxy_type, proxy_address, success_selector, debug_mode)

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def perform_logins(self, login_url, credentials, proxy_type, proxy_address, success_selector, debug_mode):
        with sync_playwright() as p:
            try:
                proxy = None
                if proxy_type != "None" and proxy_address:
                    proxy = {"server": proxy_address, "type": proxy_type.lower()}

                browser = p.chromium.launch(proxy=proxy, headless=False)
                for username, password in credentials:
                    self.log(f"Logging in with username: {username}")

                    page = browser.new_page()
                    page.goto(login_url)

                    if debug_mode:
                        page.screenshot(path=f"{username}_before_login.png")

                    # Fill in the login form
                    page.fill('input[name="username"]', username)
                    page.fill('input[name="password"]', password)

                    # Click login
                    page.click('button[type="submit"]')
                    self.random_delay()

                    # Check for success element
                    if success_selector:
                        if page.query_selector(success_selector):
                            self.log(f"Login successful for user {username}")
                        else:
                            self.log(f"Login failed for user {username}")
                    else:
                        self.log(f"Login completed for user {username}, no success element specified.")

                    if debug_mode:
                        page.screenshot(path=f"{username}_after_login.png")

                    page.close()
            except Exception as e:
                self.log(f"Error during login process: {e}")
            finally:
                browser.close()

    def perform_logins_with_script(self, login_url, credentials, proxy_type, proxy_address, success_selector, debug_mode):
        with sync_playwright() as p:
            try:
                proxy = None
                if proxy_type != "None" and proxy_address:
                    proxy = {"server": proxy_address, "type": proxy_type.lower()}

                browser = p.chromium.launch(proxy=proxy, headless=False)
                for username, password in credentials:
                    self.log(f"Logging in with username: {username}")

                    page = browser.new_page()
                    page.goto(login_url)

                    if debug_mode:
                        page.screenshot(path=f"{username}_before_login.png")

                    # Perform the captured actions
                    for action in self.script_data["actions"]:
                        if action["type"] == "click":
                            page.click(action["selector"])
                        elif action["type"] == "fill":
                            if "username" in action["selector"]:
                                page.fill(action["selector"], username)
                            elif "password" in action["selector"]:
                                page.fill(action["selector"], password)
                            else:
                                page.fill(action["selector"], action["value"])

                    # Check for success element
                    if success_selector:
                        if page.query_selector(success_selector):
                            self.log(f"Login successful for user {username}")
                        else:
                            self.log(f"Login failed for user {username}")
                    else:
                        self.log(f"Login completed for user {username}, no success element specified.")

                    if debug_mode:
                        page.screenshot(path=f"{username}_after_login.png")

                    page.close()
            except Exception as e:
                self.log(f"Error during login process: {e}")
            finally:
                browser.close()

if __name__ == '__main__':
    # Verify and install required packages
    check_and_install_modules()

    app = QApplication(sys.argv)
    login_app = LoginAutomationApp()
    login_app.show()
    sys.exit(app.exec_())
