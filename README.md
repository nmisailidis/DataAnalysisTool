# DataAnalysisTool

A lightweight desktop application for analyzing Excel datasets through a simple graphical user interface.

**DataAnalysisTool** was developed in Python to make basic spreadsheet analysis more accessible without requiring users to write Python or SQL queries. The application allows users to load an Excel dataset, select a category for grouping, choose numerical columns to aggregate, generate a summary report, and review previously imported datasets through a local SQLite database.

## Overview

DataAnalysisTool combines a graphical interface with data-processing and database functionality to provide a simple workflow for spreadsheet analysis.

The application is built around three main components:

* **Graphical User Interface** — built with Tkinter and ttk
* **Data Processing** — handled with Pandas
* **Data Persistence** — handled with SQLite

The current implementation focuses on Excel-based datasets and category-level aggregation.

## Features

### 📊 Excel Data Analysis

Load an Excel spreadsheet from:

* A local file path
* A supported HTTPS data source

After loading the spreadsheet, the application automatically reads the available column names and presents them to the user.

### 🔎 Interactive Column Selection

Users can select:

1. A primary column to group the data by
2. One or more columns whose numerical values should be aggregated

The application then uses Pandas grouping and aggregation functionality to calculate a summary of the selected data.

### 📄 Automatic Report Generation

After completing the analysis, the application generates a text-based report containing the calculated category summary.

The report is stored as:

```text
Report.txt
```

If a report already exists, new analysis results are appended to the existing file.

### 🗃️ Dataset History

DataAnalysisTool maintains a local history of imported datasets using SQLite.

The history window displays:

* Dataset filename/source
* Source type
* Import timestamp

Users can double-click a dataset to inspect the records stored for that dataset.

### 💾 Local SQLite Storage

Imported datasets are stored in:

```text
data_analysis.db
```

The database contains separate tables for dataset metadata and individual records.

This provides a persistent history between application sessions.

## Technology Stack

| Technology | Purpose                          |
| ---------- | -------------------------------- |
| Python     | Core application language        |
| Tkinter    | Desktop graphical user interface |
| Pandas     | Excel loading and data analysis  |
| SQLite     | Local data persistence           |
| JSON       | Serialization of dataset records |
| ttk        | Styled Tkinter widgets           |

## Project Structure

```text
DataAnalysisTool/
│
├── dataAnalysis.py
├── database.py
├── data_analysis.db
├── Report.txt
├── dataAnalysis.spec
│
└── README.md
```

### `dataAnalysis.py`

The main application file.

It is responsible for:

* Creating the graphical user interface
* Accepting the dataset source
* Loading Excel files
* Displaying available columns
* Handling user selections
* Performing Pandas-based aggregation
* Generating reports
* Displaying dataset history
* Displaying stored records

The application interface is implemented using Tkinter and `ttk`.

### `database.py`

Contains the SQLite database functionality.

The module provides functions for:

* Initializing the database
* Saving datasets
* Saving dataset records
* Retrieving dataset history
* Retrieving records belonging to a dataset

### `data_analysis.db`

A local SQLite database automatically used by the application to store imported dataset metadata and records.

### `Report.txt`

The generated text report containing the results of the selected analysis.

### `dataAnalysis.spec`

PyInstaller configuration used for packaging the Python application into a standalone executable.

## How It Works

The application's workflow can be summarized as follows:

```text
        ┌──────────────────────┐
        │   Select Data Source │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │    Load Excel Data   │
        │       Pandas         │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Display Data Columns │
        └──────────┬───────────┘
                   │
          ┌────────┴─────────┐
          ▼                  ▼
   Select Grouping     Select Metrics
       Column             to Sum
          │                  │
          └────────┬─────────┘
                   ▼
        ┌──────────────────────┐
        │  Group & Aggregate   │
        │       Pandas         │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │   Generate Report    │
        │     Report.txt       │
        └──────────────────────┘

                   +
                   
        ┌──────────────────────┐
        │    SQLite History    │
        │  data_analysis.db    │
        └──────────────────────┘
```

## Installation

### Requirements

Python 3.x is required.

The project uses the following Python libraries:

```bash
pip install pandas openpyxl
```

Tkinter and SQLite are part of the standard Python installation on most systems. On some Linux distributions, Tkinter may need to be installed separately through the system package manager.

### Clone the Repository

```bash
git clone https://github.com/nmisailidis/DataAnalysisTool.git
cd DataAnalysisTool
```

### Install Dependencies

```bash
pip install pandas openpyxl
```

### Run the Application

```bash
python dataAnalysis.py
```

## Usage

### 1. Start the application

Run:

```bash
python dataAnalysis.py
```

The application opens a desktop window titled:

```text
Excel Analysis App
```

### 2. Provide a data source

Enter the path to an Excel file in the source field.

For example:

```text
C:/Users/username/Documents/sales.xlsx
```

The application also contains logic for HTTPS sources that can expose Excel-compatible data.

### 3. Load the dataset

Click:

```text
Analysis
```

The application reads the Excel file with Pandas and retrieves the available column names.

The imported dataset is also saved to the local SQLite database.

### 4. Select a grouping column

After loading the dataset, select the main column that should be used to group the data.

For example:

```text
Product Category
```

### 5. Select metrics

Choose one or more columns that should be aggregated.

For example:

```text
Quantity
Revenue
```

### 6. Generate the report

Click:

```text
Generate Report!
```

The application groups the dataset by the selected category and calculates the sum of the selected metrics.

The resulting summary is written to:

```text
Report.txt
```

### 7. View dataset history

Click:

```text
View History
```

This opens a separate window containing previously imported datasets.

Double-clicking a dataset allows you to inspect its stored records.

## Example

Suppose the input spreadsheet contains:

| Product | Category    | Quantity | Revenue |
| ------- | ----------- | -------- | ------- |
| Laptop  | Electronics | 5        | 5000    |
| Phone   | Electronics | 10       | 7000    |
| Desk    | Furniture   | 4        | 1200    |
| Chair   | Furniture   | 12       | 1800    |

The user can select:

**Grouping column:**

```text
Category
```

**Metrics:**

```text
Quantity
Revenue
```

The resulting analysis produces a category-level summary similar to:

```text
Category
Electronics    Quantity: 15    Revenue: 12000
Furniture      Quantity: 16    Revenue: 3000
```

This summary is then written to `Report.txt`.

## Database Design

The application uses SQLite to maintain a history of imported datasets.

### `datasets`

Stores information about each imported dataset.

| Column            | Description               |
| ----------------- | ------------------------- |
| `id`              | Unique dataset identifier |
| `source_filename` | Original dataset source   |
| `source_type`     | Source classification     |
| `imported_at`     | Import timestamp          |

### `records`

Stores individual dataset rows as JSON.

| Column       | Description              |
| ------------ | ------------------------ |
| `id`         | Unique record identifier |
| `dataset_id` | Associated dataset       |
| `data_json`  | Serialized row data      |

The relationship between the tables is:

```text
datasets
   │
   │ 1
   │
   │
   │ N
   ▼
records
```

This allows multiple records to be associated with a single imported dataset.

## Design Decisions

### Why Pandas?

Pandas provides a convenient and efficient API for working with tabular data. It is used to:

* Read Excel spreadsheets
* Identify columns
* Group data
* Calculate aggregate values

### Why Tkinter?

Tkinter was selected because it is included with Python and provides the functionality required to build a lightweight desktop interface without introducing a large GUI framework.

### Why SQLite?

SQLite provides a simple embedded database solution without requiring a separate database server.

This makes it suitable for a local desktop application where dataset history needs to persist between sessions.

## Error Handling

The application includes user-facing error messages for common problems such as:

* Invalid data sources
* Failure to load an Excel file
* Missing grouping selections
* Missing metric selections
* Report generation errors

For example, the application prevents report generation when no grouping column or metric has been selected.

## Packaging

The repository also contains a PyInstaller specification file:

```text
dataAnalysis.spec
```

The project includes `build/` and `dist/` directories associated with application packaging.

This makes it possible to distribute the application as a packaged desktop executable rather than requiring users to run the Python source directly.

## Limitations

The current version is intentionally focused on a straightforward Excel-analysis workflow.

Current limitations include:

* Excel is the primary supported data format.
* Analysis is currently focused on grouping and summing selected columns.
* Reports are generated as plain text.
* The application does not currently provide graphical charts.
* The application is designed as a local desktop application rather than a web service.
* Database records are stored as JSON rather than being dynamically mapped to relational columns.

These limitations also provide opportunities for future development.

## Future Improvements

Potential improvements include:

* [ ] Add CSV support
* [ ] Add interactive charts and visualizations
* [ ] Add additional aggregation methods such as average, minimum, maximum, and count
* [ ] Add filtering functionality
* [ ] Add sorting options
* [ ] Add data validation and cleaning
* [ ] Export reports to Excel or PDF
* [ ] Improve URL-based dataset handling
* [ ] Add automated tests
* [ ] Add a requirements file
* [ ] Improve database indexing and normalization
* [ ] Add a more advanced dashboard interface
* [ ] Package releases for Windows, macOS, and Linux

## Learning Objectives

This project demonstrates practical experience with several areas of software development:

* Python application development
* Desktop GUI development
* Data analysis with Pandas
* Excel file processing
* SQL/SQLite database integration
* JSON serialization
* Event-driven programming
* Error handling
* Application packaging

It also demonstrates how multiple technologies can be combined to create a complete desktop data-analysis workflow.

## Project Status

**Status:** Functional / Development Project

The current version provides the core workflow for importing Excel data, performing category-based aggregation, generating reports, and maintaining dataset history.

Further development can extend the application toward a more complete desktop data-analysis platform.


## Author

**N. Misailidis**

GitHub:
https://github.com/nmisailidis

## Repository

The source code is available on GitHub:

https://github.com/nmisailidis/DataAnalysisTool
