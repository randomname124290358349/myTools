<p align="center">
  <img src="https://raw.githubusercontent.com/randomname124290358349/myTools/main/favicon.ico" width="128" alt="myTools Logo">
</p>

A web wrapper for machine programs with support for customizable commands.

---

## Features

*   **Web-based Interface**: Provides a user-friendly web interface to execute machine programs.
*   **Customizable Commands**: Easily add or modify commands through a simple JSON configuration file (`commands.json`).
*   **Python Backend**: Built with Python, making it easy to extend and customize.
*   **Lightweight**: A minimal set of files makes the project easy to understand and maintain.

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

*   Python 3.8+
*   uv (or pip)

### Installation

1.  Clone the repo
    ```sh
    git clone https://github.com/randomname124290358349/myTools.git
    ```
2.  Navigate to the project directory
    ```sh
    cd myTools
    ```

### Running the Application

1.  Run the main application:
    ```sh
    uv run app.py
    ```
2.  Open your browser and navigate to `http://127.0.0.1:5000` (or the address shown in the terminal).

## Folder Structure

```
.
├── guides/
├── templates/
│   └── index.html
├── app.py
├── commands.json
├── favicon.ico
├── pyproject.toml
└── uv.lock
```

*   **guides/**: Contains additional documentation and guides.
*   **templates/**: Holds the HTML templates for the web interface.
*   **app.py**: The main Flask application file.
*   **commands.json**: The configuration file for the custom commands.
*   **favicon.ico**: The application's icon.
*   **pyproject.toml**: The project's build configuration.
*   **uv.lock**: The lock file for the project's dependencies.
