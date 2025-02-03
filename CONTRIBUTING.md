# Architectural Design

## Overview

The **TaskMancer** application is a modular PySide6-based desktop application designed for managing complex project workflows in a 3D production pipeline. It incorporates user authentication, dynamic forms, task management, and project review areas. Its architecture follows a layered approach, separating UI components, business logic, and backend services.

## High-Level Architecture

The application consists of the following major components:

### UI Layer:

- Built using **PySide6**.
- Organized into **views, widgets, and components**.
- Each view is represented as a distinct class (e.g., `LoginPage`, `FormPage`, `TaskMancerPage`).
- UI files are designed using **Qt Designer**, and automatically generated Python files are included for seamless integration.

### Service Layer:

- Handles communication with the backend API.
- Utilizes `data_service.py` to manage data fetching and sending.

### Backend API:

- External **Django-based REST API** for data handling.
- Facilitates user authentication, data retrieval, and updates.

### Styling:

- Modular **CSS-like stylesheets** managed by `stylesheet_loader.py`.

## Interaction Flow

1. The user logs in through `LoginPage`, authenticating via the backend API.
2. Depending on the user’s role or project selection, the application navigates between `FormPage`, `ProjectPage`, `TaskMancerPage`, and others using a **QStackedWidget** in `MainWindow`.
3. Task and project details are dynamically loaded and displayed based on user inputs.
4. Work and review areas are managed using tabs in the `TaskMancerPage`, built dynamically with components such as `SelectionWidget`, `TaskListWidget`, and `TaskDetailsWidget`.

## Major Modules

### **Main Window**

- Central control for navigation and UI updates.

### **TaskMancer Page**

- Manages tasks, reviews, and work files.

### **Project Page**

- Displays project details with dynamic widgets.

### **Review Area**

- Contains task logs and detailed review components.

## Technologies Used

- **Python**: Core programming language.
- **PySide6**: For building the UI.
- **CSS-like Styling**: Custom styles applied through `stylesheet_loader.py`.
- **REST API**: Communication with the backend.

## Detailed Design

### **Components and Functionality**

#### **UI Components**

##### **LoginPage**

- **Purpose**: Authenticates users.
- **Key Classes**: `LoginPage`.
- **Features**:
  - Username and password fields.
  - Callback to transition to the next page upon successful login.

##### **FormPage**

- **Purpose**: Gathers user input for dynamic forms.
- **Key Classes**: `FormPage`.
- **Features**:
  - Dynamically generated form fields (e.g., text inputs, dropdowns).
  - Validation and submission to the backend.

##### **ProjectPage**

- **Purpose**: Displays a grid of project cards.
- **Key Classes**: `ProjectPage`, `ProjectCard`.
- **Features**:
  - Interactive project selection.
  - Navigation callbacks.

##### **TaskMancerPage**

- **Purpose**: Central hub for task management.
- **Key Classes**: `TaskMancerPage`.
- **Features**:
  - Tabs for **Work Area** and **Review Area**.
  - Widgets for task details, logs, and file management.

#### **Widgets**

- `SelectionWidget`: Handles filtering and selections.
- `TaskListWidget`: Displays tasks with filtering and search capabilities.
- `WorkFilesWidget`: Manages files related to tasks.

### **Backend Service**

##### **DataService (********`data_service.py`********\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*)**

- Provides methods to fetch and send data to the backend.
- Implements error handling for HTTP requests.

### **Styling**

##### **StylesheetLoader (********`stylesheet_loader.py`********\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*)**

- Dynamically loads and applies stylesheets.
- Ensures consistent theming across all UI components.

## Interactions

### **Login Flow**

1. User enters credentials.
2. `data_service.login_user` is called.
3. On success, `MainWindow` navigates to `FormPage`.

### **Dynamic Form Handling**

1. `FormPage` fetches form metadata from the backend.
2. Components are instantiated dynamically based on metadata.

### **Task Management**

- Tasks are displayed using `TaskListWidget`.
- Selections update the display of related files and logs.

### **Review Workflow**

- Tasks are reviewed in `ReviewAreaWidget`.
- Logs and details are fetched and displayed dynamically.

## Dependencies

- **PySide6**: For UI rendering.
- **Requests**: For API communication.

## Error Handling

- User inputs are validated locally before submission.
- Backend responses are checked for success, with error messages displayed using `MessageBox`.

## Extensibility

- **New widgets** can be integrated by following the modular design of existing components.
- **Additional API endpoints** can be supported by extending `data_service.py`.





# Tutorials

## Signals and Slots

PySide6 uses the **signal-slot** mechanism for event handling. This allows decoupled communication between UI components.

### **Example Usage:**

```python
from PySide6.QtCore import Signal, QObject

class Communicator(QObject):
    custom_signal = Signal(str)

    def send_signal(self, message):
        self.custom_signal.emit(message)

def handle_signal(msg):
    print(f"Received: {msg}")

comm = Communicator()
comm.custom_signal.connect(handle_signal)
comm.send_signal("Hello TaskMancer!")
```

## Auto-generating `.py` Files from `.ui`

UI files created in **Qt Designer** (`.ui` files) can be converted into Python files using:

```sh
pyside6-uic input.ui -o output.py
```

This allows easy integration of Qt Designer-built UI files into the PySide6 application.

---



