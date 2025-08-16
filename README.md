# Music Library Dashboard

## 🎵 Overview

This script creates an interactive web dashboard to visualize and analyze your iTunes music library. It reads an exported iTunes `Library.xml` file and presents two key insights:

1. **Album Releases by Year:** A bar chart showing the total number of unique albums in your library for each release year.

2. **Top Albums of the Year:** A detailed table listing your top 5 most-played albums for each month of the current year, complete with artist, album title, and total play count.

The dashboard is built using Python with the Dash and Plotly libraries, providing a clean, dark-themed interface to explore your listening habits.

## ✨ Features

* **Interactive Bar Chart:** Hover over the bars to see the exact number of albums for each year.

* **Detailed Top 5 Table:** Ranks your most-listened-to albums for the current year, based on the sum of play counts for each track on an album.

* **Clean & Modern UI:** A dark-themed, web-based interface that's easy to read and navigate.

* **Automatic Data Parsing:** Reads and processes the standard iTunes XML library format.

## 📋 Requirements

To run this script, you will need Python 3 and the following libraries:

* `dash`

* `pandas`

* `plotly`

## 🚀 Installation

1. **Install Python:** If you don't already have it, install Python from the official [python.org](https://www.python.org/downloads/) website.

2. **Install Libraries:** Open your terminal or command prompt and run the following command to install the necessary packages:

   ```
   pip install dash pandas plotly
   
   ```

## 💻 Usage

1. **Export Your Library:** In the Music or iTunes app, go to `File > Library > Export Library...` and save the file as an `.xml` file (e.g., `Library.xml`).

2. **Place the File:** Save the Python script in the **same directory** as your exported `AugLibrary.xml` file. If your XML file has a different name, you must update the filename inside the script on this line:

   ```
   df = parse_itunes_xml('YourFileName.xml') 
   
   ```

3. **Run the Script:** Open your terminal or command prompt, navigate to the directory where you saved the files, and run the script:

   ```
   python your_script_name.py
   
   ```

4. **View the Dashboard:** After running the script, you will see a message in the terminal with a local web address, usually `http://127.0.0.1:8050/`. Open this URL in your web browser to view your dashboard.

## 📂 Data Source

* This script is designed to work with an XML file exported from the Apple Music or iTunes application.

* The script specifically looks for the `AugLibrary.xml` file by default. Ensure your library file is named accordingly or update the script to point to the correct file.
