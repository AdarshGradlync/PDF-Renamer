# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 12:13:04 2026

@author: Adarsh
"""

import os
import re
import shutil
import hashlib
import fitz  # PyMuPDF
import pandas as pd
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox
from tkinter.ttk import Progressbar

# ============================================================
# CONFIGURATION
# ============================================================

MAX_TITLE_LENGTH = 100

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_filename(text):
    """
    Remove invalid Windows filename characters
    """
    text = re.sub(r'[<>:"/\\|?*]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def calculate_hash(filepath):
    """
    Generate SHA256 hash for duplicate detection
    """
    sha256 = hashlib.sha256()

    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            sha256.update(chunk)

    return sha256.hexdigest()


def extract_year(text):
    """
    Find likely publication year
    """
    years = re.findall(r'\b(19\d{2}|20\d{2})\b', text)

    if years:
        years = [int(y) for y in years]
        years = [y for y in years if 1950 <= y <= 2035]

        if years:
            return str(max(years))

    return "UnknownYear"


def extract_title_from_first_page(doc):
    """
    Extract likely title from first page
    using largest font size.
    """

    try:
        page = doc[0]

        blocks = page.get_text("dict")["blocks"]

        candidates = []

        for block in blocks:
            if "lines" not in block:
                continue

            for line in block["lines"]:
                line_text = ""

                max_size = 0

                for span in line["spans"]:
                    line_text += span["text"] + " "
                    max_size = max(max_size, span["size"])

                line_text = line_text.strip()

                if len(line_text) > 5:
                    candidates.append((max_size, line_text))

        if candidates:

            candidates.sort(reverse=True)

            title = candidates[0][1]

            # remove excessive spaces
            title = re.sub(r'\s+', ' ', title)

            return title

    except:
        pass

    return None


def get_pdf_metadata(pdf_path):
    """
    Extract title and year
    """

    title = None
    year = None

    try:

        doc = fitz.open(pdf_path)

        metadata = doc.metadata

        # -----------------------
        # TITLE
        # -----------------------
        meta_title = metadata.get("title", "")

        if meta_title and len(meta_title.strip()) > 5:
            title = meta_title.strip()

        if not title:
            title = extract_title_from_first_page(doc)

        if not title:
            title = os.path.splitext(os.path.basename(pdf_path))[0]

        # -----------------------
        # YEAR
        # -----------------------

        creation_date = metadata.get("creationDate", "")

        if creation_date:

            year_match = re.search(r'(19\d{2}|20\d{2})', creation_date)

            if year_match:
                year = year_match.group(1)

        if not year:

            first_page_text = doc[0].get_text()

            year = extract_year(first_page_text)

        if not year:
            year = "UnknownYear"

        doc.close()

    except Exception as e:

        title = os.path.splitext(os.path.basename(pdf_path))[0]
        year = "UnknownYear"

    # clean title

    title = clean_filename(title)

    if len(title) > MAX_TITLE_LENGTH:
        title = title[:MAX_TITLE_LENGTH]

    return title, year


# ============================================================
# MAIN PROCESSING
# ============================================================

def process_pdfs():

    source_folder = source_entry.get().strip()
    destination_folder = destination_entry.get().strip()

    if not source_folder or not destination_folder:

        messagebox.showerror(
            "Error",
            "Please select source and destination folders."
        )
        return

    pdf_files = [
        f for f in os.listdir(source_folder)
        if f.lower().endswith(".pdf")
    ]

    total_files = len(pdf_files)

    if total_files == 0:
        messagebox.showwarning(
            "No Files",
            "No PDF files found."
        )
        return

    log_data = []

    hash_set = set()

    progress["value"] = 0

    for index, pdf_file in enumerate(pdf_files):

        source_path = os.path.join(source_folder, pdf_file)

        try:

            file_hash = calculate_hash(source_path)

            if file_hash in hash_set:

                log_data.append([
                    pdf_file,
                    "",
                    "",
                    "",
                    "Duplicate Skipped"
                ])

                continue

            hash_set.add(file_hash)

            title, year = get_pdf_metadata(source_path)

            new_filename = f"{title}_{year}.pdf"

            destination_path = os.path.join(
                destination_folder,
                new_filename
            )

            # Handle filename collisions

            counter = 1

            while os.path.exists(destination_path):

                destination_path = os.path.join(
                    destination_folder,
                    f"{title}_{year}_{counter}.pdf"
                )

                counter += 1

            shutil.copy2(
                source_path,
                destination_path
            )

            pages = ""

            try:
                doc = fitz.open(source_path)
                pages = doc.page_count
                doc.close()
            except:
                pass

            log_data.append([
                pdf_file,
                os.path.basename(destination_path),
                title,
                year,
                pages,
                "Renamed"
            ])

        except Exception as e:

            log_data.append([
                pdf_file,
                "",
                "",
                "",
                "",
                f"Failed: {str(e)}"
            ])

        progress["value"] = ((index + 1) / total_files) * 100
        root.update_idletasks()

    # ====================================================
    # EXCEL EXPORT
    # ====================================================

    log_df = pd.DataFrame(
        log_data,
        columns=[
            "Original Filename",
            "New Filename",
            "Title",
            "Year",
            "Pages",
            "Status"
        ]
    )

    excel_path = os.path.join(
        destination_folder,
        "pdf_rename_log.xlsx"
    )

    log_df.to_excel(
        excel_path,
        index=False
    )

    messagebox.showinfo(
        "Completed",
        f"Processed {total_files} PDFs\n\n"
        f"Excel Log Saved:\n{excel_path}"
    )


# ============================================================
# BROWSE FUNCTIONS
# ============================================================

def browse_source():

    folder = filedialog.askdirectory()

    if folder:
        source_entry.delete(0, "end")
        source_entry.insert(0, folder)


def browse_destination():

    folder = filedialog.askdirectory()

    if folder:
        destination_entry.delete(0, "end")
        destination_entry.insert(0, folder)


# ============================================================
# GUI
# ============================================================

root = Tk()

root.title("PDF Renamer")
root.geometry("700x250")

Label(
    root,
    text="Source Folder"
).pack(pady=5)

source_entry = Entry(
    root,
    width=80
)

source_entry.pack()

Button(
    root,
    text="Browse",
    command=browse_source
).pack(pady=5)

Label(
    root,
    text="Destination Folder"
).pack(pady=5)

destination_entry = Entry(
    root,
    width=80
)

destination_entry.pack()

Button(
    root,
    text="Browse",
    command=browse_destination
).pack(pady=5)

Button(
    root,
    text="Process PDFs",
    command=process_pdfs,
    height=2,
    width=20
).pack(pady=10)

progress = Progressbar(
    root,
    length=500,
    mode="determinate"
)

progress.pack(pady=10)

root.mainloop()