import math
import serial
import threading
from requests import post
import time
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix

PI_IP="192.168.1.249"
#PI_IP="localhost"
PI_PORT="5001"

class DRCPEngine:
    def __init__(self, debugger, cb_status, cb_coords, cb_heading, cb_rvrHeading, cb_manual):

        version = "0.1.3"

        # debug
        self.debugger = debugger

        self.debugger.log("version", f"[engine] Running DRCP Engine v{version}")

        self.status = "Initializing"
        self.mode = "manual"

        self.updateStatus = cb_status # callback to update status in GUI
        self.updateCoords = cb_coords # callback to update coordinates in GUI
        self.updateHeading = cb_heading
        self.updateRoverHeading = cb_rvrHeading
        self.GUIsetManual = cb_manual

        self.dr_coords = [0.0000, 0.0000]  # [lat, lon]
        self.rover_coords = [0.0000, 0.0000] # [lat, lon]
        self.current_heading = 0.0  # in degrees
        self.previous_heading = 0.0  # in degrees

        rclpy.init()
        # drcpros = DRCPROS(self.debugger, self._ros_callback)
        # threading.Thread(target=rclpy.spin(drcpros))
        threading.Thread(target=rclpy.spin, args=(DRCPROS(self.debugger, self._ros_callback),)).start()


    # internal funcs
    def _set_serial(self, serial_port):
        # self.debugger.log(f"[engine] _startup_set_serial called with port: {serial_port}")
        # if not serial_port:
        #     raise ValueError("[engine] Serial port cannot be empty")
        # try:
        #     self.debugger.log("[engine] Closing existing serial connection")
        #     self.serial.close()
        # except AttributeError:
        #     self.debugger.log("[engine] No existing serial connection to close")
        # except serial.SerialException as e:
        #     self.debugger.log(f"[engine] Error closing serial connection: {e}")
        # self.debugger.log("[engine] Opening new serial connection")
        self.serial = DRCPSerial(self.debugger, serial_port)
        

    def _startup_set_init_heading(self, heading):
        self.debugger.log(f"[engine] _startup_set_init_heading called with heading: {heading}")
        try:
            heading = float(heading)
            if not (0 <= heading < 360):
                raise ValueError("Heading must be between 0 and 360 degrees")
            self.current_heading = heading

        except ValueError as e:
            raise ValueError(f"[engine] Invalid initial heading: {e}")
    
    # set initial coords for the death ray
    def _startup_set_init_coords(self, lat, lon):
        self.debugger.log(f"[engine] _startup_set_init_coords called with coords: {lat}, {lon}")
        self.dr_coords = [lat, lon]

    def _ros_callback(self, coords):
        self.rover_coords = [coords[0], coords[1]]
        self.updateCoords(self.rover_coords)
        if self.dr_coords[0] != 0.0000:
            rover_bearing = self.calculate_bearing(self.dr_coords[0], self.dr_coords[1], self.rover_coords[0], self.rover_coords[1])
            self.updateRoverHeading(rover_bearing)


    def calculate_bearing(self, lat1, lon1, lat2, lon2):
        self.debugger.log(f"[engine] calculate_bearing called with coords: {lat1}, {lon1}, {lat2}, {lon2}")
        """
        Calculate bearing from point 1 (lat1, lon1) to point 2 (lat2, lon2)
        Returns bearing in degrees from North (0° to 360°)
        """
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        diff_lon_rad = math.radians(lon2 - lon1)

        x = math.sin(diff_lon_rad) * math.cos(lat2_rad)
        y = math.cos(lat1_rad) * math.sin(lat2_rad) - \
            math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(diff_lon_rad)

        initial_bearing = math.atan2(x, y)
        bearing_deg = int((math.degrees(initial_bearing) + 360) % 360)
        return bearing_deg
    
    def set_mode(self, mode):
        self.debugger.log(f"[engine] set_mode called with mode: {mode}")
        if mode not in ["manual", "auto"]:
            raise ValueError("Invalid mode. Use 'manual' or 'auto'.")
        self.mode = mode
        
    def auto(self):
        self.debugger.log("[engine] auto mode started")
        if self.mode != "auto":
            raise RuntimeError("Engine is not in auto mode")

        while self.mode == "auto":
            # don't go until we got both coordinates
            if self.dr_coords[0] == 0.0000 or self.rover_coords[0] == 0.0000:
                self.debugger.log(f"[engine] don't have full coords yet, not rotating")
            else:    
                # Calculate bearing to the antenna
                bearing = self.calculate_bearing(
                    self.dr_coords[0], self.dr_coords[1],
                    self.rover_coords[0], self.rover_coords[1]
                )

                if bearing != self.current_heading:
                    degrees_to_rotate = (bearing - self.current_heading) % 360 # calculate difference between current heading and new one
                    if degrees_to_rotate > 180:
                        degrees_to_rotate -= 360 # if have to turn more than half-way, then we should be turning backwards
                    if abs(degrees_to_rotate) > 2:
                        self.updateRoverHeading(bearing) # set requested heading to new rover heading
                        self.debugger.log("auto", f"Rotating by {degrees_to_rotate} degrees")
                        self.updateStatus(f"Auto: Rotating by {degrees_to_rotate} degrees...")
                        feedback = self.rotateBy(degrees_to_rotate, True) # rotate by difference
                        if feedback.startswith("#done$rotate("):
                            self.debugger.log("Auto: Done rotating")
                            self.updateStatus(feedback)
                            self.updateHeading(bearing)
                            self.current_heading = bearing
                    else:
                        self.debugger.log("auto", "Bearing difference not enough")
            time.sleep(0.5)




                # if bearing != self.current_heading:
                #     degrees_to_rotate = (bearing - self.current_heading) % 360
                #     if degrees_to_rotate > 180:
                #         degrees_to_rotate -= 360
                #     if abs(degrees_to_rotate) > 1:  # Allow a small tolerance
                #         self.debugger.log(f"[engine] Auto mode: rotating by {degrees_to_rotate} degrees")
                #         self.updateHeading(degrees_to_rotate)
                #         feedback = self.rotateBy(degrees_to_rotate)
                #         self.debugger.log(f'[engine] received feedback {feedback}')
                #         self.updateStatus("Finished rotating")
                #     else:
                #         #self.debugger.log("[engine] Auto mode: no significant rotation needed")
                #         #self.debugger.log(f"[engine] heading change {degrees_to_rotate}")
                #         pass
            #time.sleep(0.5)
            

    def rotateBy(self, degrees, auto=False):
        if not auto:
            self.debugger.log(f"[engine] rotateBy called with degrees: {degrees}")
            if not isinstance(degrees, (int, float)):
                raise ValueError("Degrees must be a number")
            if not (-360 <= degrees <= 360):
                raise ValueError("Degrees must be between -360 and 360")
            
            self.current_heading = (self.current_heading + degrees) % 360
            self.updateStatus(f"Rotating by {degrees} degrees")
            response = self.cmd_rotate(degrees) # feedback from the death ray
            return response
        else:
            response = self.cmd_rotate(degrees)
            return response

    def cmd_home(self):
        self.debugger.log("[engine] cmd_home called")
        self.status = "Home doesn't do anything"
        self.updateStatus(self.status)
        #self.serial.send_command("$hone")

    def cmd_rotate(self, degrees):
        self.debugger.log(f"[engine] cmd_rotate called with degrees: {degrees}")
        #self.status = f"Rotating by {int(degrees)} degrees"
        #self.updateStatus(self.status)
        try:
            if degrees < 0:
                response = self.serial.send_command(f"$rotate({abs(int(degrees))},0)")
            else:
                response = self.serial.send_command(f"$rotate({int(degrees)},1)")
            return response
        except ConnectionError:
            self.debugger.log(f"[engine] !!! COULDN'T CONNECT TO Pi's WEBSERVER, CHECK IP and IF WEBSERVER IS RUNNING !!!")

    def cmd_stop(self):
        self.debugger.log("[engine] cmd_stop called")
        self.serial.send_command("$stop")
        self.set_mode("manual")
        self.GUIsetManual()
        self.updateStatus("Stopped, mode forced to manual")

class DRCPSerial():
    def __init__(self, debugger, serial_port):
        self.debugger = debugger
        self.debugger.log(f"[Serial] Initializing with port: {serial_port}")

        self.serial_port = serial_port
        self.baudrate = 9600 
        self.timeout = 1

        #self._open()

    def _open(self):
        self.debugger.log(f"[Serial] Opening serial port: {self.serial_port}")
        try:
            self.ser = serial.Serial(self.serial_port, self.baudrate, timeout=self.timeout)
            self.ser.flushInput()
            self.ser.flushOutput()
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            print(f"Serial port {self.serial_port} opened successfully.")
        except serial.SerialException as e:
            print(f"Error opening serial port {self.serial_port}: {e}")
            raise

    def close(self):
        self.debugger.log(f"[Serial] Closing serial port: {self.serial_port}")
        if self.ser.is_open:
            self.ser.close()
            print(f"Serial port {self.serial_port} closed.")
        else:
            print(f"Serial port {self.serial_port} is not open.")
        del self.ser

    def send_command(self, command):
        # self.debugger.log(f"[Serial] Sending command: {command}")
        # if not self.ser.is_open:
        #     raise serial.SerialException("Serial port is not open.")
        # try:
        #     self.ser.write(command.encode('utf-8'))
        #     self.debugger.log(f"Command sent: {command}")
        # except serial.SerialTimeoutException as e:
        #     self.debugger.log(f"Timeout while sending command: {e}")
        # except serial.SerialException as e:
        #     self.debugger.log(f"Error sending command: {e}")
        response = post(f"http://{PI_IP}:{PI_PORT}/send", json={"command":f"{command}"}, timeout=70)
        print(f"[DBG] {response.json()['feedback']}")
        return response.json()['feedback']
    def read_response(self):
        self.debugger.log("[Serial] Reading response")
        # Read response from the Death Ray controller
        pass

# a node to receive rover's GNSS data from the nmea_reader node
class DRCPROS(Node):
    def __init__(self, debugger, callback):
        super().__init__('drcp_gnss_receiver')
        self.debugger = debugger
        self.debugger.log("[ROS] ROS node started")
        self.callback = callback
        self.subscription = self.create_subscription(NavSatFix, 'gnss_fix', self._updateCoords, 10)
        self.subscription

    def _updateCoords(self, natfixobj):
        self.debugger.log(f"[ROS] Updating coordinates {natfixobj.latitude}, {natfixobj.longitude}")
        coords = [natfixobj.latitude, natfixobj.longitude]
        self.callback(coords)






if __name__ == "__main__":
    print("Engine cannot run headless yet, run `python3 drcp_gui.py`")
