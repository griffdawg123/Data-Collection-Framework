# Data Collection Framework
## Acceptance Criteria
### Managing Workspaces
1. Create a new workspace and then close the window
2. Load the original workspace from a config file and then close the window
3. Assert that a new workspace cannot be created using the same name as the first
workspace
### Managing Devices
1. Add a new device to the workspace and quit
2. Load the workspace and assert that the device is added back into the workspace
3. Remove the device from the workspace and then quit
4. Load the workspace and assert that the device is removed from the workspace
5. Load the device back into the workspace via config
6. Assert that the device does connect to the workspace
### Managing Basic Graphs
1. Add a single graph to the workspace:
    - A sin graph with the function y = sin(x), using the system clock as input
    - 60fps and 100 datapoints
    - y range of (-1,1)
2. Play the graph and observe that it follows the correct curve
3. Close the workspace and then reopen it and play the graph again to assert it 
remains correct
4. Add a new graph to the same row with the same parameters but rather y = cos(x)
5. Assert that both graphs play concurrently
#### Managing BLE Graphs
1. Add a new row with a single graph using a notify characteristic
    - Note: The mQn Fixed Point function can be used to decode bytearrays,
    If not specified, simply leave n as 0 and input the length of the array
    in m as specified by the device's firmware
2. Assert that the graph plays correctly and responds to sensor input


