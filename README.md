# Company Search Tool (Version 1.1.1)

## Description
The **Company Search Tool** is a Python-based GUI application that extracts company data from the websites **firmen.wko.at** (Austria) and **gelbeseiten.de** (Germany). Users can search for companies based on industry and location, and save the results to an Excel file. The program also supports an option to display only companies without a website.

## Features:
- Scraping company information (name, address, phone number, website, email) for Austria and Germany.
- Option to filter companies without a website.
- Save results to an Excel file.

## Requirements

Ensure you have Python 3.x installed on your system.

Install the following Python libraries by running this command in your terminal or command prompt:

```bash
pip install -r requirements.txt
```

Running the Program

Clone the repository or download the source code.

```bash
git clone https://github.com/yourusername/company-scraper.git
```

Navigate to the project directory:

```bash
cd company-scraper
```

Install the required libraries (see the "Requirements" section).

```bash
pip install -r requirements.txt
```

Run the Python script:

```bash
python main_V_1.1.1.py
```

Creating an Executable (.exe) File

If you want to distribute the program as a standalone executable file (.exe) without requiring Python to be installed, you can use the PyInstaller module.

Installing PyInstaller
To install PyInstaller, if you haven't done so already, run:

```bash
pip install pyinstaller
```

Creating the .exe File
To create an .exe file from your Python script, run the following command in the directory where main_V_1.1.1.py is located:

```bash
pyinstaller --onefile --windowed main_V_1.1.1.py
```

Explanation of the options:
--onefile: Packages the entire program and its dependencies into a single .exe file.
--windowed: Prevents a console window from appearing when the application is launched (useful for GUI applications).
After running this command, an executable file (main_V_1.1.1.exe) will be generated in the dist folder.

Using the Application

Launch the application.
Select the country (Austria or Germany).
Enter an industry and location for the search.
Optionally, check the "Only entries without a website" box if you want to filter results.
Click "Start Search" to begin fetching results.
Once the search is complete, save the results to an Excel file.
Error Logging

Any errors encountered during the search process are logged in the error_log.txt file.

