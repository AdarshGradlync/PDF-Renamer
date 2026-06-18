# PDF Research Library Manager

## Overview

PDF Research Library Manager is a Python-based GUI application designed to automate the organization of academic literature.

The tool reads PDF metadata and first-page content to generate meaningful filenames, detects duplicate files using SHA256 hashing, copies renamed files to a destination folder, and creates an Excel log for tracking changes.

---

## Features

* PDF metadata extraction
* First-page title extraction
* Automatic file renaming
* Duplicate detection using SHA256 hash
* Excel log generation
* User-friendly Tkinter GUI
* Original files remain unchanged

---

## Technologies Used

* Python
* Tkinter
* PyMuPDF
* Pandas
* OpenPyXL

---

## Folder Structure

```text
pdf-research-library-manager
│
├── src
│   └── pdf_renamer_gui.py
│
├── screenshots
│   └── gui.png
│
├── requirements.txt
└── README.md
```

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Running the Application

```bash
python src/pdf_renamer_gui.py
```

---

## Example Output

Original:

```text
paper123.pdf
```

Renamed:

```text
Deep Reinforcement Learning for Swarm UAV Navigation_2024.pdf
```

---

## Future Improvements

* DOI extraction
* Author extraction
* Abstract extraction
* Keyword extraction
* Zotero export
* Research paper classification

---

## Author

Adarsh Krishnamurthy

Assistant Professor – Aerospace Engineering

Research Area: Swarm UAVs, Artificial Intelligence, Reinforcement Learning
