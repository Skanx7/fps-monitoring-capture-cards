# live-fps-monitoring-capture-cards
Stream-compatible external overlay that will display FPS metrics and the resolution.

Currently displays:
- Current Resolution
- Current FPS
- Average FPS (in a 5 minute window)
- 1% Low FPS (in a 5 minute window)
- FPS Graph (in a 200 seconds window) 

It also comes with a device selector to choose which capture card to use.

Current limitations:
- Will not detect duplicate frames for games that fake a higher framerate (typically occurs on some fidelity modes with locked framerates)
- Will be displayed on the PC as well

Tested with an El Gato 4K 60 Pro MK.2, can't guarantee compatibility with non PCIE capture cards.

# IMPORTANT READ
Requirements:
- Install ffmpeg and add it to the PATH of your Windows
- Install the dependencies from requirements.txt with the command "pip install -r requirements.txt"

# Instructions

- Run the device_selector and choose your device and save it, it will be saved to your config.json
- Run the main.py an overlay will appear
- You can then add the overlay to OBS by adding a Window Capture with the overlay window

If the device_selector.py didn't work: 
- Run this command "ffmpeg -list_devices true -f dshow -i dummy" and find the name of the device between the " "
- In the monitoring.py file replace the input_device value with this:
"video="+ "Insert the device name of your capture card that you found with the command"


# Captures of the tool:

![448886881_494641542944506_2243017613757868914_n](https://github.com/Skanx7/fps-monitoring-capture-cards/assets/147698559/653ec938-5c3e-46ca-8baa-452b2049e034)
![448860341_494630702945590_5966649950157780015_n](https://github.com/Skanx7/fps-monitoring-capture-cards/assets/147698559/f83d01f7-4641-4ebc-b017-4de59ec1e602)
![448820290_494624549612872_1234103738682547222_n](https://github.com/Skanx7/fps-monitoring-capture-cards/assets/147698559/1e306d17-5e0d-41f2-bf79-d2d817e6179f)
![448812216_494612739614053_1129532347611291785_n](https://github.com/Skanx7/fps-monitoring-capture-cards/assets/147698559/d2a6f5be-7504-4ba9-a7cb-895209ef71f3)
![449130605_494637029611624_4918753957169995540_n](https://github.com/Skanx7/fps-monitoring-capture-cards/assets/147698559/f1a8c309-9972-4960-9d0d-63ef0c933969)
