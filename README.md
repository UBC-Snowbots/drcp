# Death Ray Control Panel

Death Ray Control Panel (DRCP) is the GUI tool for full control of the Death Ray (aka Comms Station). DRCP allows for both manual adjustments and GPS-based autosteer. It is built with Python and Tkinter. 

It is split into two files: `drcp-gui.py` and `drcp-engine.py`. The first only contains the GUI and methods to make it run, the second one contains all of actual logic. However, for now, the engine does not work without the GUI. Run `python3 drcp-gui.py` to run the software.

To run it, you will need:
- The Death Ray
- Emlid Reach RS+ AND M+ GNSS transcievers
- A phone with a compass app installed (pre-installed on iPhones)
- `nmea_reader` (`rover_gnss` package) running

DRCP also saves all of it's actions to the `drcp-debug-log.txt` file. Please send it to Max (@deadfloppy) with feedback, for bugfixes.

Cameron, I know where you live >:3
