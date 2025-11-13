"""
HOSPITAL PATIENT DASHBOARD (Tkinter Version)
--------------------------------------------
Single-file hospital dashboard using Tkinter & CSV for local storage.

Features:
- Add, view, edit, delete patients
- Search/filter
- Auto ID generation
- Data stored in 'patients.csv'
"""

import tkinter as tk
from tkinter import ttk, messagebox
import csv, os
from datetime import datetime

# ----------------------------
# CSV File Setup
# ----------------------------
FILE_NAME = "patients.csv"
FIELDS = ["PatientID", "Name", "Age", "Gender", "Phone", "AdmissionDate", "Ward", "Doctor", "Diagnosis", "Status"]

def load_patients():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
        return []
    with open(FILE_NAME, newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_patients(data):
    with open(FILE_NAME, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(data)

# ----------------------------
# App Class
# ----------------------------
class HospitalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🏥 Hospital Patient Dashboard")
        self.root.geometry("1100x600")
        self.root.config(bg="#f7f7f7")

        # Data
        self.patients = load_patients()
        self.selected_patient = None

        # Title
        title = tk.Label(root, text="🏥 HOSPITAL PATIENT DASHBOARD", font=("Arial", 20, "bold"), bg="#004c91", fg="white", pady=10)
        title.pack(fill="x")

        # Search bar
        self.search_var = tk.StringVar()
        search_frame = tk.Frame(root, bg="#f7f7f7")
        search_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(search_frame, text="Search:", font=("Arial", 12), bg="#f7f7f7").pack(side="left")
        tk.Entry(search_frame, textvariable=self.search_var, width=40).pack(side="left", padx=5)
        tk.Button(search_frame, text="Search", command=self.search_patient, bg="#4caf50", fg="white").pack(side="left", padx=5)
        tk.Button(search_frame, text="Show All", command=self.show_all, bg="#1976d2", fg="white").pack(side="left", padx=5)

        # Form
        form_frame = tk.LabelFrame(root, text="Patient Information", font=("Arial", 12, "bold"), padx=10, pady=10, bg="#f7f7f7")
        form_frame.pack(fill="x", padx=10, pady=5)

        self.entries = {}
        labels = ["Name", "Age", "Gender", "Phone", "Admission Date", "Ward", "Doctor", "Diagnosis", "Status"]
        defaults = ["", "", "Male", "", datetime.today().strftime("%Y-%m-%d"), "", "", "", "Admitted"]
        for i, (lbl, val) in enumerate(zip(labels, defaults)):
            tk.Label(form_frame, text=lbl + ":", font=("Arial", 11), bg="#f7f7f7").grid(row=i//3, column=(i%3)*2, sticky="w", pady=3, padx=5)
            ent = ttk.Entry(form_frame, width=25)
            ent.insert(0, val)
            ent.grid(row=i//3, column=(i%3)*2 + 1, pady=3, padx=5)
            self.entries[lbl] = ent

        # Gender & Status dropdowns
        self.entries["Gender"].destroy()
        self.gender_var = tk.StringVar(value="Male")
        ttk.Combobox(form_frame, textvariable=self.gender_var, values=["Male", "Female", "Other"], width=23, state="readonly").grid(row=0, column=3, pady=3, padx=5)

        self.entries["Status"].destroy()
        self.status_var = tk.StringVar(value="Admitted")
        ttk.Combobox(form_frame, textvariable=self.status_var, values=["Admitted", "Discharged"], width=23, state="readonly").grid(row=2, column=3, pady=3, padx=5)

        # Buttons
        btn_frame = tk.Frame(root, bg="#f7f7f7")
        btn_frame.pack(fill="x", padx=10, pady=5)
        tk.Button(btn_frame, text="Add Patient", command=self.add_patient, bg="#388e3c", fg="white", width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Edit Selected", command=self.edit_patient, bg="#f57c00", fg="white", width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_patient, bg="#d32f2f", fg="white", width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Save Changes", command=self.save_all, bg="#1976d2", fg="white", width=15).pack(side="left", padx=5)

        # Table
        table_frame = tk.Frame(root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = FIELDS
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Summary
        self.summary_label = tk.Label(root, text="", font=("Arial", 11, "bold"), bg="#e8eaf6", pady=8)
        self.summary_label.pack(fill="x")

        self.refresh_table()

    # ----------------- CRUD FUNCTIONS -----------------
    def new_patient_id(self):
        existing_ids = [int(p["PatientID"][1:]) for p in self.patients if p["PatientID"].startswith("P")]
        new_id = max(existing_ids, default=1000) + 1
        return f"P{new_id}"

    def add_patient(self):
        data = {
            "PatientID": self.new_patient_id(),
            "Name": self.entries["Name"].get(),
            "Age": self.entries["Age"].get(),
            "Gender": self.gender_var.get(),
            "Phone": self.entries["Phone"].get(),
            "AdmissionDate": self.entries["Admission Date"].get(),
            "Ward": self.entries["Ward"].get(),
            "Doctor": self.entries["Doctor"].get(),
            "Diagnosis": self.entries["Diagnosis"].get(),
            "Status": self.status_var.get()
        }
        if not data["Name"]:
            messagebox.showwarning("Warning", "Patient name is required.")
            return
        self.patients.append(data)
        self.refresh_table()
        messagebox.showinfo("Success", f"Added patient {data['PatientID']}")

    def on_select(self, event):
        selected = self.tree.focus()
        if not selected: return
        values = self.tree.item(selected, "values")
        pid = values[0]
        for p in self.patients:
            if p["PatientID"] == pid:
                self.selected_patient = p
                break

    def edit_patient(self):
        if not self.selected_patient:
            messagebox.showwarning("Select", "Select a patient first.")
            return
        for field in FIELDS:
            if field == "PatientID": continue
            if field == "Gender":
                self.selected_patient[field] = self.gender_var.get()
            elif field == "Status":
                self.selected_patient[field] = self.status_var.get()
            else:
                val = self.entries.get(field) or None
                if val:
                    self.selected_patient[field] = val.get()
        self.refresh_table()
        messagebox.showinfo("Updated", "Patient record updated.")

    def delete_patient(self):
        if not self.selected_patient:
            messagebox.showwarning("Select", "Select a patient first.")
            return
        pid = self.selected_patient["PatientID"]
        self.patients = [p for p in self.patients if p["PatientID"] != pid]
        self.selected_patient = None
        self.refresh_table()
        messagebox.showinfo("Deleted", f"Deleted patient {pid}")

    def search_patient(self):
        q = self.search_var.get().strip().lower()
        if not q:
            self.refresh_table()
            return
        filtered = [p for p in self.patients if any(q in str(v).lower() for v in p.values())]
        self.show_table(filtered)

    def show_all(self):
        self.refresh_table()

    def refresh_table(self):
        self.show_table(self.patients)
        self.update_summary()

    def show_table(self, data):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for p in data:
            self.tree.insert("", "end", values=[p[f] for f in FIELDS])

    def save_all(self):
        save_patients(self.patients)
        messagebox.showinfo("Saved", "All changes saved to patients.csv")

    def update_summary(self):
        total = len(self.patients)
        admitted = sum(1 for p in self.patients if p["Status"] == "Admitted")
        discharged = total - admitted
        self.summary_label.config(text=f"Total Patients: {total} | Admitted: {admitted} | Discharged: {discharged}")

# ----------------------------
# Main Run
# ----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = HospitalApp(root)
    root.mainloop()
