# Automated-Login-Tool
Automated Login Tool with GUI



Automated Login Tool

This tool allows you to automate login processes by capturing user interactions and generating scripts.

## Features

- Capture user interactions to generate login scripts.
- Import and use generated scripts for automated login processes.
- Support for different types of proxies (HTTP, SOCKS5).
- Optional credentials file for username and password pairs.
- Debug mode with screenshots before and after login.
- Polished GUI with clear instructions.

## Installation

1. Ensure you have Python installed on your system.
2. Install the required packages by running the following command:

```bash
pip install PyQt5 playwright
```

3. Install the browser binaries for Playwright:

```bash
playwright install
```

## Usage

1. Run the script:

```bash
python login_automation_tool.py
```

2. Follow the instructions in the initial popup.
3. Click "Make Script" to start the script maker mode.
4. Perform the login steps manually.
5. Click "Save Script" when done.
6. Import the generated script and use it for automated login processes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
