import tkinter as tk
from tkinter import colorchooser

class DoodleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Relaxing Doodle Game")
        self.root.geometry("800x600")
        self.root.configure(bg="#F5F5DC")  # Soft beige background
        
        self.canvas = tk.Canvas(self.root, bg="white", width=700, height=500)
        self.canvas.pack(pady=20)
        
        self.brush_color = "black"
        self.brush_size = 5
        
        self.controls_frame = tk.Frame(self.root, bg="#F5F5DC")
        self.controls_frame.pack()
        
        self.color_button = tk.Button(self.controls_frame, text="Choose Color", command=self.choose_color)
        self.color_button.pack(side=tk.LEFT, padx=10)
        
        self.clear_button = tk.Button(self.controls_frame, text="Clear", command=self.clear_canvas)
        self.clear_button.pack(side=tk.LEFT, padx=10)
        
        self.size_slider = tk.Scale(self.controls_frame, from_=1, to=20, orient=tk.HORIZONTAL, label="Brush Size")
        self.size_slider.set(self.brush_size)
        self.size_slider.pack(side=tk.LEFT, padx=10)
        
        self.canvas.bind("<B1-Motion>", self.paint)
        
    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.brush_color = color
        
    def paint(self, event):
        self.brush_size = self.size_slider.get()
        x1, y1 = (event.x - self.brush_size), (event.y - self.brush_size)
        x2, y2 = (event.x + self.brush_size), (event.y + self.brush_size)
        self.canvas.create_oval(x1, y1, x2, y2, fill=self.brush_color, outline=self.brush_color)
        
    def clear_canvas(self):
        self.canvas.delete("all")

if __name__ == "__main__":
    root = tk.Tk()
    app = DoodleApp(root)
    root.mainloop()
