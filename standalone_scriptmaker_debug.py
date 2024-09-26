import os
import json
import sys
import subprocess
import logging
import random
import time
import asyncio
from playwright.sync_api import sync_playwright

# List of required modules
REQUIRED_MODULES = [
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

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ScriptMaker:
    def __init__(self):
        self.script_data = {"actions": []}
        self.page = None

    def start(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            self.page = browser.new_page()
            self.page.on("framenavigated", self.on_navigate)
            self.page.on("click", self.on_click)
            self.page.on("input", self.on_input)
            self.page.goto("about:blank")
            self.log("Press 'Save Script' when done.")
            while not self.page.evaluate("() => window.saveScript"):
                time.sleep(1)
            browser.close()
            self.save_script()

    def on_navigate(self, request):
        self.log(f"Navigated to: {request.url}")
        self.script_data["actions"].append({"type": "goto", "url": request.url})

    def on_click(self, element):
        selector = self.page.evaluate("(element) => element.getAttribute('id') || element.getAttribute('class')", element)
        self.log(f"Clicked: {selector}")
        self.script_data["actions"].append({"type": "click", "selector": selector})

    def on_input(self, element):
        selector = self.page.evaluate("(element) => element.getAttribute('id') || element.getAttribute('class')", element)
        value = self.page.evaluate("(element) => element.value", element)
        self.log(f"Filled: {selector} with {value}")
        self.script_data["actions"].append({"type": "fill", "selector": selector, "value": value})
import os
import json
import sys
import subprocess
import logging
import random
import time
import asyncio
from playwright.sync_api import sync_playwright

# List of required modules
REQUIRED_MODULES = [
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

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ScriptMaker:
    def __init__(self):
        self.script_data = {"actions": []}
        self.page = None

    def start(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            self.page = browser.new_page()
            self.page.on("framenavigated", self.on_navigate)
            self.page.on("click", self.on_click)
            self.page.on("input", self.on_input)
            self.page.goto("about:blank")
            self.log("Press 'Save Script' when done.")
            while not self.page.evaluate("() => window.saveScript"):
                time.sleep(1)
            browser.close()
            self.save_script()

    def on_navigate(self, request):
        self.log(f"Navigated to: {request.url}")
        self.script_data["actions"].append({"type": "goto", "url": request.url})

    def on_click(self, element):
        selector = self.page.evaluate("(element) => element.getAttribute('id') || element.getAttribute('class')", element)
        self.log(f"Clicked: {selector}")
        self.script_data["actions"].append({"type": "click", "selector": selector})

    def on_input(self, element):
        selector = self.page.evaluate("(element) => element.getAttribute('id') || element.getAttribute('class')", element)
        value = self.page.evaluate("(element) => element.value", element)
        self.log(f"Filled: {selector} with {value}")
        self.script_data["actions"].append({"type": "fill", "selector": selector, "value": value})

    def save_script(self):
        script_path = os.path.join(os.getcwd(), "login_script.json")
        with open(script_path, "w") as f:
            json.dump(self.script_data, f, indent=4)
        self.log(f"Script saved to {script_path}")

    def log(self, message):
        print(message)

if __name__ == "__main__":
    check_and_install_modules()
    script_maker = ScriptMaker()
    script_maker.start()
    def save_script(self):
        script_path = os.path.join(os.getcwd(), "login_script.json")
        with open(script_path, "w") as f:
            json.dump(self.script_data, f, indent=4)
        self.log(f"Script saved to {script_path}")

    def log(self, message):
        print(message)

if __name__ == "__main__":
    check_and_install_modules()
    script_maker = ScriptMaker()
    script_maker.start()
