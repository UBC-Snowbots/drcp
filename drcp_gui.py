import tkinter as tk
from tkinter import ttk
import threading
from drcp_engine import DRCPEngine

import time

# I FUCCKING HATE UI AAAAAAH (deadfloppy)

# colours
COLOR_BG = "#1e1e1e" # sexy gray
COLOR_FG = "#003366" # intriguing blue
COLOR_BT = "#444" # button gray
COLOR_W = "#FFFFFF" # racist white

# screen sizes
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 400
TOP_FRAME_HEIGHT = SCREEN_HEIGHT * 1 / 6
MIDDLE_FRAME_HEIGHT = SCREEN_HEIGHT * 3 / 5 # to make calcs easier
BOTTOM_FRAME_HEIGHT = SCREEN_HEIGHT * 1 / 5 
RIGHT_SUBFRAME_HEIGHT = (SCREEN_HEIGHT - TOP_FRAME_HEIGHT) * 1 / 4
EMPTY_FRAME_HEIGHT = RIGHT_SUBFRAME_HEIGHT-5*4 # 5px padding on each side
LEFT_FRAME_WIDTH = SCREEN_WIDTH * 2 / 6
DISH_FRAME_HEIGHT = (SCREEN_HEIGHT - TOP_FRAME_HEIGHT)* 3 / 5
LABEL_WIDTH = 10 # for status and mode labels

print("SCREEN_WIDTH:", SCREEN_WIDTH)
print("SCREEN_HEIGHT:", SCREEN_HEIGHT)
print("TOP_FRAME_HEIGHT:", TOP_FRAME_HEIGHT)
print("MIDDLE_FRAME_HEIGHT:", MIDDLE_FRAME_HEIGHT)
print("BOTTOM_FRAME_HEIGHT:", BOTTOM_FRAME_HEIGHT)
print("RIGHT_SUBFRAME_HEIGHT:", RIGHT_SUBFRAME_HEIGHT)
print("LEFT_FRAME_WIDTH:", LEFT_FRAME_WIDTH)

# just to help log n fix shit, can be deleted later
class Debugger():
    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode
        logfile = f"drcp_debug_log.txt"
        try:
            self.f = open(logfile, 'a+')
        except Exception as e:
            print(f"FAIL: Couldn't open logfile: {e}")
        self.f.write(f"--- STARTING DRCP LOG @ {time.strftime('(%d/%m %H:%M:%S) ---', time.localtime())}\n")

    def log(self, message):
        if self.debug_mode:
            print(f"[DEBUG] {message}")
            self.f.write(f"{message}\n")

import tkinter as tk
import math

class DeathRayControlPanel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.debugger = Debugger(debug_mode=True)
        self.engine = DRCPEngine(debugger=self.debugger,
                                 cb_status=self._cb_update_status,
                                 cb_coords=self._cb_update_coords,
                                 cb_heading=self._update_heading)
        self.status = "Status Placeholder"
        self.serial = "/dev/placeholder"
        self.current_heading = 0.0 
        self.requested_heading = 0.0
        self.rover_coords = [0.0000, 0.0000]  # [lat, lon]
        self.deathray_coords = [0.0000, 0.0000]  # [lat, lon]

        self.title("Death Ray Control Panel v0")
        self.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        self.configure(bg = COLOR_BG)

        # custom styling
        style = ttk.Style()
        style.theme_use("clam")

        # control button
        style.configure("Control.TButton", background = COLOR_BT, foreground = COLOR_W, relief = "flat")
        
        # stop button
        style.configure("Stop.TButton", background = "#FF0000", foreground = COLOR_W, relief = "flat")
        style.map("Stop.TButton",
                    background=[('active', "#FF0000")],
                    foreground=[('disabled', "#aaa")])

        # mode selector buttons
        style.map("Mode.TButton",
                    background=[('active', "#00FF08")],
                    foreground=[('disabled', "#FF0000")])

        # text input field

        # label
        self.debugger.log("[GUI] calling _buildStartupUI")
        self._buildStartupUI()

    def _buildStartupUI(self):

        self._root_frame = tk.Frame(self, bg = COLOR_BG)
        self._root_frame.pack(fill = tk.BOTH, expand = True)

        # startup frame is selfed to be destroyed later and i DO NOT CARE :3
        self.startup_frame = tk.Frame(self._root_frame, bg=COLOR_BG)
        self.startup_frame.pack(fill=tk.BOTH, expand=True)

        # left frame
        # has instructional images like how to put your phone to get initial heading
        left_frame = tk.Frame(self.startup_frame, width = LEFT_FRAME_WIDTH, bg = "#A2FF38")
        left_frame.pack(fill = tk.Y, side = tk.LEFT, expand = False)
        left_frame.pack_propagate(False)

        # instruction frame
        instruction_frame = tk.Frame(left_frame, bg = COLOR_BG, height = TOP_FRAME_HEIGHT, width = LEFT_FRAME_WIDTH)
        instruction_frame.pack(side = tk.LEFT, fill = tk.BOTH, expand = False)
        instruction_frame.pack_propagate(False)

        self.instruction_image = tk.PhotoImage(file="src/step2.png") # has to be self or python will garbage collect it

        instruction_label = tk.Label(instruction_frame, bg = COLOR_BG, fg = "#000000", image = self.instruction_image)
        instruction_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        # right frame
        right_frame = tk.Frame(self.startup_frame, bg = "#183394")
        right_frame.pack(fill = tk.BOTH, side = tk.RIGHT, expand = True)
        right_frame.pack_propagate(False)

        # title label
        title_label = tk.Label(right_frame, text = "Startup Procedure",
                               bg = "#38CAFF", fg = COLOR_W,
                               font = ("Helvetica", 18, "bold"))
        title_label.pack(side = tk.TOP, fill = tk.X, expand = True)

        # serial input frame
        serial_frame = tk.Frame(right_frame, bg = "#FF3863", height=RIGHT_SUBFRAME_HEIGHT)
        serial_frame.pack(side=tk.TOP, fill = tk.BOTH, expand = False)
        serial_frame.pack_propagate(False)
        serial_frame_title = tk.Label(serial_frame, text="Step 1: Death Ray serial port", bg = "#FF3863",
                                      fg = COLOR_W, font = ("Helvetica", 12, "bold"))
        serial_frame_title.pack(side = tk.TOP, fill=tk.X, expand=False)
        serial_explanation = tk.Label(serial_frame, text="Enter the serial port for the Death Ray controller (e.g., /dev/serial2)",
                                      bg = "#FF3863", fg = COLOR_W, font = ("Helvetica", 10))
        serial_explanation.pack(fill=tk.X, expand=False)
        serial_input_frame = tk.Frame(serial_frame, bg = "#38FFB9")
        serial_input_frame.pack(fill=tk.BOTH, expand=True)
        serial_input_frame.pack_propagate(False)
        # serial port input field and button
        serial_input = tk.Entry(serial_input_frame, width=20)
        serial_input.insert(0, self.serial)  # default value
        serial_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)
        serial_button = ttk.Button(serial_input_frame, text="Set Serial Port", style="Control.TButton",
                                  command=lambda: self._set_serial(serial_input.get()))
        serial_button.pack(side=tk.RIGHT, fill=tk.X, expand=False, padx=5, pady=5)

        # initial heading input frame
        heading_frame = tk.Frame(right_frame, bg = "#FFB338", height=RIGHT_SUBFRAME_HEIGHT*1.5)
        heading_frame.pack(side=tk.TOP, fill = tk.BOTH, expand = False)
        heading_frame.pack_propagate(False)
        heading_frame_title = tk.Label(heading_frame, text="Step 2: Set Initial Heading", bg = "#FFB338",
                                       justify="left",
                                       fg = COLOR_W, font = ("Helvetica", 12, "bold"))
        heading_frame_title.pack(side = tk.TOP, fill=tk.X, expand=False)
        explanation_text = "Open a compass app on your phone and place it with the charging port flat against the front of the dish, as shown. Enter the magnetic heading shown in the app. (0°-359°)"
        heading_explanation = tk.Label(heading_frame, text=explanation_text, wraplength=int(SCREEN_WIDTH-LEFT_FRAME_WIDTH-7), justify="left",
                                       bg = "#FFB338", fg = COLOR_W, font = ("Helvetica", 10))
        heading_explanation.pack(fill=tk.BOTH, expand=False)
        heading_input_frame = tk.Frame(heading_frame, bg = "#38FFB3")
        heading_input_frame.pack(fill=tk.BOTH, expand=True)
        heading_input_frame.pack_propagate(False)
        # heading input field and button
        heading_input = tk.Entry(heading_input_frame, width=5)
        heading_input.insert(0, "0")  # default value
        heading_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)
        heading_button = ttk.Button(heading_input_frame, text="Set Initial Heading", style="Control.TButton",
                                   command=lambda: self._set_init_heading(float(heading_input.get())))
        heading_button.pack(side=tk.RIGHT, fill=tk.X, expand=False, padx=5, pady=5)

        # initial death ray coordinates input frame
        coords_frame = tk.Frame(right_frame, bg = "#FF38B3", height= RIGHT_SUBFRAME_HEIGHT)
        coords_frame.pack(side=tk.TOP, fill=tk.BOTH, expand = False)
        coords_frame.pack_propagate(False)
        coords_frame_title = tk.Label(coords_frame, text="Step 3: Set Initial Death Ray Coordinates",
                                      bg = "#33886C", fg = COLOR_W, font = ("Helvetica", 12, "bold"))
        coords_frame_title.pack(side = tk.TOP, fill=tk.X, expand=False)
        coords_explanation = tk.Label(coords_frame, text="Enter the initial coordinates of the Death Ray from the Reach RS+.",
                                      bg = "#33886C", fg = COLOR_W, font = ("Helvetica", 10))
        coords_explanation.pack(fill=tk.X, expand=False, padx=5, pady=5)
        coords_input_frame = tk.Frame(coords_frame, bg = "#38FFB3")
        coords_input_frame.pack(fill=tk.BOTH, expand=True)
        coords_input_frame.pack_propagate(False)
        # latitude input field and button
        lat_input = tk.Entry(coords_input_frame, width=10)
        lat_input.insert(0, "52.51858752")  # default value
        lat_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)
        # longitude input field and button
        lon_input = tk.Entry(coords_input_frame, width=10)
        lon_input.insert(0, "13.40462655")  # default value
        lon_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)
        coords_button = ttk.Button(coords_input_frame, text="Set Initial Coordinates", style="Control.TButton",
                                   command=lambda: self._set_init_coords(float(lat_input.get()), float(lon_input.get())))
        coords_button.pack(side=tk.RIGHT, fill=tk.X, expand=False, padx=5, pady=5)

        # buttons frame
        buttons_frame = tk.Frame(right_frame, bg = "#38FFB3", height= EMPTY_FRAME_HEIGHT)
        buttons_frame.pack(side=tk.TOP, fill=tk.BOTH, expand = True)
        buttons_frame.pack_propagate(False)
        # manual only button
        manual_button = ttk.Button(buttons_frame, text="Skip (Manual mode only)", style="Control.TButton",
                                  command=self._startup_skip)
        manual_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        # continue button
        continue_button = ttk.Button(buttons_frame, text="Continue", style="Control.TButton",
                                   command=self._buildMainUI)
        continue_button.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)


    def _buildMainUI(self):
        # root_frame = tk.Frame(self, bg = COLOR_BG)
        # root_frame.pack(fill = tk.BOTH, expand = True)

        # destroy startup frame
        self.startup_frame.destroy()

        # top frame
        # contains UBC Rover logo and program title
        top_frame = tk.Frame(self._root_frame, height = TOP_FRAME_HEIGHT, bg=COLOR_BG)
        top_frame.pack(fill = tk.X, expand = False)
        top_frame.pack_propagate(False)

        # UBC Rover logo image
        logo_frame = tk.Frame(top_frame, bg = COLOR_BG, height = TOP_FRAME_HEIGHT, width = LEFT_FRAME_WIDTH)
        logo_frame.pack(side = tk.LEFT, fill = tk.BOTH, expand = False)
        logo_frame.pack_propagate(False)

        self.logo_image = tk.PhotoImage(file="src/ubcrover.png") # has to be self or python will garbage collect it

        logo_label = tk.Label(logo_frame, bg = COLOR_BG, fg = "#000000", image = self.logo_image)
        logo_label.pack(fill=tk.BOTH, expand=False)

        # title label
        title_label = tk.Label(top_frame, text = "Death Ray Control Panel",
                               bg = COLOR_BG, fg = COLOR_W,
                               font = ("Helvetica", 18, "bold"))
        title_label.pack(side = tk.LEFT, fill = tk.BOTH, expand = True, padx=5, pady=5)

        # middle frame
        middle_frame = tk.Frame(self._root_frame, bg=COLOR_BG)
        middle_frame.pack(fill = tk.BOTH, expand = True)
        middle_frame.pack_propagate(False)

        # left frame
        left_frame = tk.Frame(middle_frame, width = LEFT_FRAME_WIDTH, bg = COLOR_BG)
        left_frame.pack(fill = tk.Y, side = tk.LEFT, expand = False)
        left_frame.pack_propagate(False)

        # heading display
        self._addHeadingDisplay(left_frame)

        # right frame
        right_frame = tk.Frame(middle_frame, bg = COLOR_BG)
        right_frame.pack(fill = tk.BOTH, side = tk.RIGHT, expand = True)

        # status frame
        self._addStatusFrame(right_frame)

        # GNSS frame
        self._addGNSSFrame(right_frame)

        # heading frame
        self._addHeadingFrame(right_frame)


        # empty fucking space frame so this shit LOOKS NICE
        empty_frame = tk.Frame(right_frame, bg = COLOR_BG)
        empty_frame.pack(fill = tk.BOTH, expand = True, padx=5, pady=5)


        # bottom frame
        bottom_frame = tk.Frame(self._root_frame, width = SCREEN_WIDTH, height = BOTTOM_FRAME_HEIGHT, bg = COLOR_BG)
        bottom_frame.pack(fill = tk.BOTH, expand = False)
        bottom_frame.pack_propagate(False)

        # serial frame
        self._addSerialFrame(bottom_frame)

        # controls frame
        self._addControlsFrame(bottom_frame)

    def _addHeadingDisplay(self, parent):
        self.headingCanvas = tk.Canvas(parent, width=LEFT_FRAME_WIDTH, height=LEFT_FRAME_WIDTH, bg="black")
        self.headingCanvas.pack()

        # draw circle
        self.headingCanvas.create_oval(5, 5, LEFT_FRAME_WIDTH-5, LEFT_FRAME_WIDTH-5,
                                       outline="white", width=2)
        
        self.headingDisplayCENTER = (LEFT_FRAME_WIDTH-10)/2 + 5
        self.headingDisplayRADIUS = (LEFT_FRAME_WIDTH-10)/2
        # draw cardinal dirs
        for angle in [0, -90, 90]:
            self._drawHeadingDisplayLine(angle)
        
        self.currentHeadingLine = self._drawHeadingDisplayLine(self.current_heading, "blue")
        self.requestedHeadingLine = self._drawHeadingDisplayLine(self.requested_heading, "red")

    def _addStatusFrame(self, parent):
        frame = tk.LabelFrame(parent, text = "Death Ray Status", height = RIGHT_SUBFRAME_HEIGHT-5,
                              fg = COLOR_W, bg = COLOR_BG,
                              font = ("Helvetica", 10, "bold"), bd = 2)
        frame.pack(fill=tk.BOTH, expand = False, padx=5, pady=5)
        frame.grid_propagate(False) # prevent shrinking
        # make column width be fucking normal
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=3)
        frame.grid_columnconfigure(2, weight=3)

        # Status row
        tk.Label(frame, text="Status", fg=COLOR_W, bg=COLOR_FG).grid(row=0, column=0, sticky="nsew")
        self.StatusLabel = tk.Label(frame, text="Ready", bg="#555", fg=COLOR_W)
        self.StatusLabel.grid(row=0, column=1, columnspan=2, sticky="nsew")
        
        # Mode row
        tk.Label(frame, text="Mode", fg=COLOR_W, bg=COLOR_FG).grid(row=1, column=0, sticky="nsew")
        mode_manual_button = ttk.Button(frame, text="MANUAL", style="Mode.TButton", command=self._start_manual_mode).grid(row=1, column=1, sticky="nsew")
        mode_auto_button = ttk.Button(frame, text="AUTO", style="Mode.TButton", command=self._start_auto_mode).grid(row=1, column=2, sticky="nsew")
        
    def _addGNSSFrame(self, parent):
        frame = tk.LabelFrame(parent, text="GNSS Data", height=RIGHT_SUBFRAME_HEIGHT+5,
                              fg=COLOR_W, bg=COLOR_BG,
                              font=("Helvetica", 10, "bold"), bd=2)
        frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        frame.grid_propagate(False)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=3)
        frame.grid_columnconfigure(2, weight=3)

        # Header
        tk.Label(frame, text="", bg=COLOR_BG).grid(row=0, column=0)
        tk.Label(frame, text="Latitude", bg=COLOR_BG, fg=COLOR_W).grid(row=0, column=1) 
        tk.Label(frame, text="Longitude", bg=COLOR_BG, fg=COLOR_W).grid(row=0, column=2)

        # DR row
        tk.Label(frame, text="DR", bg=COLOR_FG, fg=COLOR_W).grid(row=1, column=0, sticky="nsew")
        self.dr_lat = tk.Label(frame, text=f"{self.deathray_coords[0]:.6f}", bg="#555", fg=COLOR_W)
        self.dr_lat.grid(row=1, column=1, sticky="nsew")
        self.dr_lon = tk.Label(frame, text=f"{self.deathray_coords[1]:.6f}", bg="#555", fg=COLOR_W)
        self.dr_lon.grid(row=1, column=2, sticky="nsew")

        # Rover row
        tk.Label(frame, text="Rover", bg=COLOR_FG, fg=COLOR_W).grid(row=2, column=0, sticky="nsew")
        self.rover_lat = tk.Label(frame, text="N/A", bg="#555", fg=COLOR_W)
        self.rover_lat.grid(row=2, column=1, sticky="nsew")
        self.rover_lon = tk.Label(frame, text="N/A", bg="#555", fg=COLOR_W)
        self.rover_lon.grid(row=2, column=2, sticky="nsew")

    def _addHeadingFrame(self, parent):
        frame = tk.LabelFrame(parent, text="Heading", height=RIGHT_SUBFRAME_HEIGHT,
                              fg=COLOR_W, bg=COLOR_BG,
                              font=("Helvetica", 10, "bold"), bd=2)
        frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        frame.pack_propagate(False)

        current_heading_label = tk.Label(frame, text="Current", bg=COLOR_FG, fg=COLOR_W)
        current_heading_label.pack(side=tk.LEFT, fill=tk.X, expand=False)
        self.current_heading_value_label = tk.Label(frame, text=f"{self.current_heading:.1f}°", bg="#555", fg=COLOR_W)
        self.current_heading_value_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        requested_heading_label = tk.Label(frame, text="Requested", bg=COLOR_FG, fg=COLOR_W)
        requested_heading_label.pack(side=tk.LEFT, fill=tk.X, expand=False)
        self.requested_heading_value_label = tk.Label(frame, text=f"{self.requested_heading:.1f}°", bg="#555", fg=COLOR_W)
        self.requested_heading_value_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _addSerialFrame(self, parent):
        frame = tk.LabelFrame(parent, text="Serial", height=RIGHT_SUBFRAME_HEIGHT,
                              width = LEFT_FRAME_WIDTH-10,
                              fg=COLOR_W, bg=COLOR_BG,
                              font=("Helvetica", 10, "bold"), bd=2)
        frame.pack(side=tk.LEFT, expand = False, padx=5, pady=5)
        frame.pack_propagate(False)

        # serial port text input field
        serial_field = tk.Entry(frame, width = 15)
        serial_field.insert(0, self.serial)
        serial_field.pack(side=tk.LEFT, padx=5, pady=5)

        # set button
        set_button = ttk.Button(frame, text="Set", style="Control.TButton", command=lambda: self._set_serial(serial_field.get()))
        set_button.pack(side=tk.LEFT, padx=5, pady=5)

    def _addControlsFrame(self, parent):
        frame = tk.LabelFrame(parent, text="Controls", height=RIGHT_SUBFRAME_HEIGHT,
                              fg=COLOR_W, bg=COLOR_BG,
                              font=("Helvetica", 10, "bold"), bd=2)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        # frame.pack_propagate(False)

        # home buttom
        self.home_button = ttk.Button(frame, text="Home", style="Control.TButton", command=self.engine.cmd_home)
        self.home_button.pack(side=tk.LEFT, padx=5, pady=5)

        # degree input
        self.degree_entry = tk.Entry(frame, width=5)
        self.degree_entry.pack(side=tk.LEFT, padx=5, pady=5)

        # rotate button
        self.rotate_button = ttk.Button(frame, text="Rotate", style="Control.TButton", command=lambda: self.manualRotate(self.degree_entry.get()))
        self.rotate_button.pack(side=tk.LEFT, padx=5, pady=5)

        # stop button
        self.stop_button = ttk.Button(frame, text="STOP", style="Stop.TButton", command=self.engine.cmd_stop)
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5)



    # callbacks for engine updates
    def _cb_update_status(self, new_status):
        self.debugger.log(f"[GUI] _cb_update_status called with status: {new_status}")
        self.status = new_status
        self.StatusLabel.config(text=self.status)

    def _cb_update_coords(self, rover_coords):
        self.debugger.log(f"[GUI] _cb_update_coords called with coords: {rover_coords}")
        self.rover_coords = rover_coords
        try:
            self.rover_lat.config(text=f"{self.rover_coords[0]:.6f}")
            self.rover_lon.config(text=f"{self.rover_coords[1]:.6f}")
        except AttributeError:
            self.debugger.log("[GUI] Failed to update rover coord labels, probably haven't been loaded yet")

        

    # UI functions
    def _startup_skip(self):
        self.debugger.log("[GUI] Skipping startup procedure, setting manual mode")
        self.engine.set_mode("manual")
        self._buildMainUI()

    def _set_init_coords(self, lat, lon):
        self.debugger.log(f"[GUI] Setting initial coordinates to {lat}, {lon}")
        self.deathray_coords = [lat, lon]
        self.engine._startup_set_init_coords(lat, lon)

    def _set_init_heading(self, heading):
        self.debugger.log(f"[GUI] Setting initial heading to {heading}")
        self.current_heading = heading
        try:
            self.engine._startup_set_init_heading(heading)
        except ValueError as e:
            self.debugger.log(f"[GUI] Error setting initial heading: {e}")
            #tk.messagebox.showerror("Error", f"Invalid heading: {e}")

    def _set_serial(self, serial_port):
        self.debugger.log(f"[GUI] Setting serial port to {serial_port}")
        self.serial = serial_port
        try:
            self.engine._set_serial(self.serial)
        except ValueError as e:
            self.debugger.log(f"[GUI] Error setting serial port: {e}")
            #tk.messagebox.showerror("Error", f"Invalid serial port: {e}")

    def _start_manual_mode(self):
        self.debugger.log("[GUI] Starting manual mode")
        self.engine.set_mode("manual")

    def _start_auto_mode(self):
        self.debugger.log("[GUI] Starting auto mode")
        self.engine.set_mode("auto")
        threading.Thread(target=self.engine.auto, daemon=True).start()

    def _drawHeadingDisplayLine(self, ang, color="white"):
        self.debugger.log(f"[GUI] _drawHeadingDisplayLine called with angle: {ang}, color: {color}")
        angle_rad = math.radians(ang - 90)  # rotate so 0 is up
        x = self.headingDisplayCENTER + self.headingDisplayRADIUS * math.cos(angle_rad)
        y = self.headingDisplayCENTER + self.headingDisplayRADIUS * math.sin(angle_rad)
        return self.headingCanvas.create_line(self.headingDisplayCENTER, self.headingDisplayCENTER, x, y, fill=color, width=2)

    def _updateHeadingDisplayLine(self, ang, line):
        self.debugger.log(f"[GUI] _updateHeadingDisplayLine called with angle {ang}, line {line}")
        angle_rad = math.radians(ang - 90)  # rotate so 0 is up
        x = self.headingDisplayCENTER + self.headingDisplayRADIUS * math.cos(angle_rad)
        y = self.headingDisplayCENTER + self.headingDisplayRADIUS * math.sin(angle_rad)
        self.headingCanvas.coords(line, self.headingDisplayCENTER, self.headingDisplayCENTER, x, y)

    def _update_heading(self, ang):
        self.debugger.log(f"[GUI] _cb_update_heading called with {ang} degrees")
        self.current_heading = ang
        self._updateHeadingDisplayLine(self.current_heading, self.currentHeadingLine)
        self.current_heading_value_label.config(text=self.current_heading)

    def manualRotate(self, ang):
        self.debugger.log(f"[GUI] manualRotate called with angle: {ang}")
        try:
            ang = float(ang)
        except ValueError:
            self.debugger.log("[GUI] Invalid angle input, must be a number")
            return
        
        if not (-360 <= ang <= 360):
            raise ValueError("Angle must be between -360 and 360")
        
        self.current_heading = (self.current_heading + ang) % 360
        self._update_heading(self.current_heading)
        self.engine.rotateBy(ang)

if __name__ == "__main__":
    cp = DeathRayControlPanel()
    cp.mainloop()                                                                                        