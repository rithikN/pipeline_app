# Pipeline Task Manager

## Description

The **Pipeline Task Manager** is a **PySide6-based desktop application** designed for **task and workflow management**. It provides features such as user authentication, task management, and a customizable UI in a modular structure.

## Features

- **Frontend Only**: No data processing occurs in the frontend; all operations are managed through the backend.
- **API Integration**: The application communicates with backend API endpoints for all data transactions.
- **Modular UI Components**: Designed for reusability and maintainability.

## Installation

### Prerequisites

Ensure you have Python installed (version 3.10 or later).

### Install Dependencies

Run the following command to install required dependencies:

```sh
pip install -r requirements.txt
```

## Running the Application

To start the application, navigate to the `src/` directory and run:

```sh
python main.py
```

## Project Structure

```sh
.
├── src/               # Application source code
│   ├── main.py        # Entry point of the application
│   ├── ui/            # UI design files (.ui, QSS, icons)
│   ├── resources/     # Images, fonts, and other assets
│   ├── manager/       # Centralized UI interactions and signals
│   ├── stylesheets/   # CSS files for UI styling
│   ├── views/         # High-level UI views
│   ├── utils/         # Utility scripts for UI operations
├── requirements.txt   # Python dependencies
├── setup.py           # Script to build executable files for Windows and Mac
└── README.md          # Project documentation
```

## Building an Executable

To package the application into an executable, use PyInstaller:

```sh
python setup.py
```

This will generate an executable file in the `dist/` directory.

## Contributing

1. Clone the repository.
2. Create a new branch:

   ```sh
   git checkout -b feature-branch
   ```

3. Commit your changes:

   ```sh
   git commit -m 'Add new feature'
   ```

4. Push to the branch:

   ```sh
   git push origin feature-branch
   ```

5. Create a pull request.

## Development Guidelines

### Adding or Modifying Features

- **Editing UI Forms**:

  - Modify the corresponding `.ui` file in `ui/components/forms/`.
  - Use a PySide UI designer tool for visual editing.
  - Convert `.ui` files to `.py` using:
    
    ```sh
    pyside6-uic input.ui -o output.py
    ```

- **Styling**:

  - Update the relevant CSS file in `stylesheets/`.

- **Debugging**:

  - Enable Python logging in the `main.py` file.

## Contact

- **Current Maintainer**: *Rithik Nayampally*
- **Email**: *[suvarna.rithik@gmail.com](mailto:suvarna.rithik@gmail.com)*
- **GitHub Repository**: *[https://github.com/rithikN/pipeline_app](https://github.com/rithikN/pipeline_app)*

## Next Steps

- Implement **data caching** for improved performance.
- Add an **event handler/manager** to trigger events dynamically.
- Add a **smart refresh button**.
- Use **PySide's QDebug** for UI-related debugging.
- Add **unit tests** for validation.

