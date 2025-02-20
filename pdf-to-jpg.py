import os
import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

class PDFConverterApp:
    def __init__(self, master):
        self.master = master
        master.title("PDF to JPG Converter")
        master.geometry("500x400")

        # Variables
        self.pdf_files = []
        self.output_folder = ""
        self.dpi = 200  # Default DPI
        self.quality = 90  # Default JPG quality

        # Create UI elements
        self.create_widgets()

    def create_widgets(self):
        # File selection button
        self.btn_select_pdf = tk.Button(
            self.master, 
            text="Select PDF Files",
            command=self.select_pdfs,
            width=20,
            height=2
        )
        self.btn_select_pdf.pack(pady=10)

        # Output folder button
        self.btn_select_output = tk.Button(
            self.master,
            text="Select Output Folder",
            command=self.select_output,
            width=20,
            height=2
        )
        self.btn_select_output.pack(pady=10)

        # Settings frame
        settings_frame = tk.Frame(self.master)
        settings_frame.pack(pady=10)

        # DPI control
        tk.Label(settings_frame, text="DPI:").grid(row=0, column=0, padx=5)
        self.dpi_scale = tk.Scale(
            settings_frame, 
            from_=72, 
            to=600, 
            orient=tk.HORIZONTAL,
            length=200
        )
        self.dpi_scale.set(200)
        self.dpi_scale.grid(row=0, column=1, padx=5)

        # Quality control
        tk.Label(settings_frame, text="Quality:").grid(row=1, column=0, padx=5)
        self.quality_scale = tk.Scale(
            settings_frame,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            length=200
        )
        self.quality_scale.set(90)
        self.quality_scale.grid(row=1, column=1, padx=5)

        # Convert button
        self.btn_convert = tk.Button(
            self.master,
            text="Convert to JPG",
            command=self.start_conversion,
            bg="#4CAF50",
            fg="white",
            width=20,
            height=2
        )
        self.btn_convert.pack(pady=20)

        # Status label
        self.status_label = tk.Label(
            self.master,
            text="Ready",
            fg="gray"
        )
        self.status_label.pack()

    def select_pdfs(self):
        self.pdf_files = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if self.pdf_files:
            self.status_label.config(
                text=f"{len(self.pdf_files)} PDF(s) selected",
                fg="blue"
            )

    def select_output(self):
        self.output_folder = filedialog.askdirectory(
            title="Select Output Folder"
        )
        if self.output_folder:
            self.status_label.config(
                text=f"Output: {self.output_folder}",
                fg="blue"
            )

    def start_conversion(self):
        if not self.pdf_files:
            messagebox.showerror("Error", "Please select PDF files first!")
            return
        if not self.output_folder:
            messagebox.showerror("Error", "Please select an output folder!")
            return

        try:
            self.btn_convert.config(state=tk.DISABLED)
            total_pages = 0

            for pdf_path in self.pdf_files:
                try:
                    doc = fitz.open(pdf_path)
                    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
                    output_dir = os.path.join(self.output_folder, base_name)
                    os.makedirs(output_dir, exist_ok=True)

                    for page_num in range(len(doc)):
                        page = doc.load_page(page_num)
                        zoom = self.dpi_scale.get() / 72
                        mat = fitz.Matrix(zoom, zoom)
                        pix = page.get_pixmap(matrix=mat, alpha=False)
                        
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        output_path = os.path.join(
                            output_dir, 
                            f"{base_name}_page_{page_num+1:03d}.jpg"
                        )
                        img.save(
                            output_path,
                            quality=self.quality_scale.get(),
                            optimize=True
                        )
                        total_pages += 1

                    doc.close()
                except Exception as e:
                    messagebox.showerror(
                        "Error",
                        f"Failed to convert {os.path.basename(pdf_path)}:\n{str(e)}"
                    )

            messagebox.showinfo(
                "Success",
                f"Converted {len(self.pdf_files)} files ({total_pages} pages total)"
            )
            self.status_label.config(text="Conversion complete!", fg="green")

        except Exception as e:
            messagebox.showerror("Error", f"Fatal error: {str(e)}")
            self.status_label.config(text="Conversion failed", fg="red")
        finally:
            self.btn_convert.config(state=tk.NORMAL)
            self.master.update()

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFConverterApp(root)
    root.mainloop()
