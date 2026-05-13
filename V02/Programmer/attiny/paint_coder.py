import tkinter as tk
from tkinter import colorchooser, scrolledtext, messagebox
import random
import colorsys

class MatrixAnimator:
    def __init__(self, root):
        self.root = root
        self.root.title("4x4 encoder")
        self.root.geometry("650x850")

        self.current_color = "#ff0000"
        self.grid_colors = ["#000000"] * 16
        self.frames = []

        control_frame = tk.Frame(root)
        control_frame.pack(pady=10)

        brush_frame = tk.LabelFrame(control_frame, text="Brush", padx=10, pady=5)
        brush_frame.grid(row=0, column=0, padx=10, sticky="n")

        self.brush_mode = tk.StringVar(value="solid")
        tk.Radiobutton(brush_frame, text="Solid", variable=self.brush_mode, value="solid").pack(anchor="w")
        
        self.color_btn = tk.Button(brush_frame, text="Pick Color", bg=self.current_color, fg="white", command=self.choose_color, width=15)
        self.color_btn.pack(pady=5)

        tk.Radiobutton(brush_frame, text="Random", variable=self.brush_mode, value="random").pack(anchor="w", pady=(5,0))

        output_frame = tk.LabelFrame(control_frame, text="Settings", padx=10, pady=5)
        output_frame.grid(row=0, column=1, padx=10, sticky="n")

        tk.Label(output_frame, text="Delay (ms):").grid(row=0, column=0, sticky="e", pady=5)
        self.delay_entry = tk.Entry(output_frame, width=8)
        self.delay_entry.insert(0, "500")
        self.delay_entry.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(output_frame, text="Brightness (0-255):").grid(row=1, column=0, sticky="e", pady=5)
        self.brightness_scale = tk.Scale(output_frame, from_=0, to=255, orient=tk.HORIZONTAL, length=120)
        self.brightness_scale.set(38)
        self.brightness_scale.grid(row=1, column=1, pady=5, padx=5)

        map_frame = tk.LabelFrame(control_frame, text="Wiring", padx=10, pady=5)
        map_frame.grid(row=0, column=2, padx=10, sticky="n")

        self.mapping_var = tk.StringVar(value="sequential")
        tk.Radiobutton(map_frame, text="Sequential", variable=self.mapping_var, value="sequential").pack(anchor="w")
        tk.Radiobutton(map_frame, text="Serpentine", variable=self.mapping_var, value="serpentine").pack(anchor="w")

        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(pady=15)
        self.cells = []
        
        for i in range(16):
            row = i // 4
            col = i % 4
            canvas = tk.Canvas(self.canvas_frame, width=60, height=60, bg="black", highlightthickness=1, highlightbackground="gray")
            canvas.grid(row=row, column=col, padx=2, pady=2)
            
            canvas.bind("<Button-1>", lambda event, idx=i: self.paint_cell(idx))
            canvas.bind("<Button-3>", lambda event, idx=i: self.erase_cell(idx))
            self.cells.append(canvas)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Save Frame", command=self.save_frame, width=15, bg="lightblue", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Clear Grid", command=self.clear_grid, width=12).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Clear ALL", command=self.clear_all_frames, width=15, bg="lightcoral").grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Randomize", command=self.randomize_filled, width=30, bg="#ffdd57", font=("Arial", 10, "bold")).grid(row=1, column=0, columnspan=3, pady=10)

        self.status_label = tk.Label(root, text="Frames: 0", font=("Arial", 12, "bold"), fg="blue")
        self.status_label.pack(pady=5)

        tk.Button(root, text="GENERATE CODE", command=self.generate_code, width=35, height=2, bg="lightgreen", font=("Arial", 12, "bold")).pack(pady=10)

        self.output_text = scrolledtext.ScrolledText(root, width=75, height=15, font=("Consolas", 9))
        self.output_text.pack(pady=5)

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Choose color")[1]
        if color_code:
            self.current_color = color_code
            self.color_btn.config(bg=self.current_color)
            self.brush_mode.set("solid")

    def paint_cell(self, idx):
        if self.brush_mode.get() == "random":
            h = random.random()
            s = random.uniform(0.8, 1.0)
            v = random.uniform(0.8, 1.0)
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        else:
            color = self.current_color
            
        self.grid_colors[idx] = color
        self.cells[idx].config(bg=color)

    def erase_cell(self, idx):
        self.grid_colors[idx] = "#000000"
        self.cells[idx].config(bg="black")

    def clear_grid(self):
        self.grid_colors = ["#000000"] * 16
        for canvas in self.cells:
            canvas.config(bg="black")

    def randomize_filled(self):
        for i in range(16):
            if self.grid_colors[i] != "#000000":
                h = random.random() 
                s = random.uniform(0.85, 1.0) 
                v = random.uniform(0.85, 1.0) 
                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                hex_color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
                self.grid_colors[i] = hex_color
                self.cells[i].config(bg=hex_color)

    def save_frame(self):
        self.frames.append(list(self.grid_colors))
        self.status_label.config(text=f"Frames: {len(self.frames)}")

    def clear_all_frames(self):
        self.frames = []
        self.status_label.config(text="Frames: 0")
        self.clear_grid()

    def generate_code(self):
        if not self.frames:
            messagebox.showwarning("No Frames", "Save at least one frame first!")
            return

        mapping = self.mapping_var.get()
        delay = self.delay_entry.get()
        brightness = self.brightness_scale.get()

        cpp_code = f"""#include <tinyNeoPixel.h>

#define LED_PIN   PIN_PA4
#define NUM_LEDS  16

tinyNeoPixel strip(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

const uint8_t NUM_FRAMES = {len(self.frames)};
const uint16_t FRAME_DELAY = {delay}; 

const uint32_t animation[{len(self.frames)}][NUM_LEDS] = {{\n"""

        for f_idx, frame in enumerate(self.frames):
            cpp_code += "  { // F" + str(f_idx + 1) + "\n    "
            
            mapped_frame = ["0x000000"] * 16
            for i in range(16):
                hex_val = "0x" + frame[i][1:].upper() 
                
                if mapping == "sequential":
                    mapped_frame[i] = hex_val
                else: 
                    row = i // 4
                    col = i % 4
                    if row % 2 == 1: 
                        mapped_idx = (row * 4) + (3 - col)
                    else:
                        mapped_idx = i
                    mapped_frame[mapped_idx] = hex_val

            row1 = ", ".join(mapped_frame[0:4])
            row2 = ", ".join(mapped_frame[4:8])
            row3 = ", ".join(mapped_frame[8:12])
            row4 = ", ".join(mapped_frame[12:16])
            
            cpp_code += f"{row1},\n    {row2},\n    {row3},\n    {row4}\n  }}"
            if f_idx < len(self.frames) - 1:
                cpp_code += ","
            cpp_code += "\n"

        cpp_code += f"""}};

void setup() {{
  strip.begin();
  strip.setBrightness({brightness}); 
  strip.show();
}}

void loop() {{
  for(uint8_t f = 0; f < NUM_FRAMES; f++) {{
    for(uint8_t i = 0; i < NUM_LEDS; i++) {{
      strip.setPixelColor(i, animation[f][i]);
    }}
    strip.show();
    delay(FRAME_DELAY);
  }}
}}
"""
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, cpp_code)

if __name__ == "__main__":
    root = tk.Tk()
    app = MatrixAnimator(root)
    root.mainloop()