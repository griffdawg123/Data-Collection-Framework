# DCF Todo List
## Done
- [x] Graph wrapper with title, axis labels, remove, edit buttons
- [x] add New plot button to control buttons
- [x] Individual plot widget - Implement with coroutine method & new bit parsing
- [x] Rewrite Data Collection using coroutines
- [x] Graph Displaying
- [x] Allow for in application rewriting of plot config 
- [x] Construct rewriting plot config editing from input config
- [x] Implement characteristic scanning for BLE devices
- [x] Add start stop controls
- [x] Reimplement restart function
- [x] Implemented Device manager - Better handling and signals
- [x] Start notify jobs when start is clicked so the actual start of the graph is after all successful
- [ ] Ensure if Fixed point is chosen, the chunk chooser is shown
- [ ] Ensure that if Existing config is ble, show source/characteristic combobox
- [ ] Make it so that By default, args is shown as BLE source is also the default
- [ ] Add disconnected callback to show in status tray
- [ ] Graph form needs to fully reform itself correctly - So that it resaves correctly
- [ ] Why aren't multiple notify characteristics working?
- [ ] Change Source form to allow for choice of which Bytearray chunk to be used
- [ ] Share sources across graphs
- [x] Individual plot widget - Implement with coroutine method & new bit parsing
## In Progress
- [ ] can construct workspace from empty file or json with missing tags
## Backlog
- [ ] Remove plotline from combobox when removed from plot
- [ ] Change label on chunk choose spinbox to "index"
- [ ] Ensure only my logging is used 
- [ ] JSON Schema implementation for validation 
- [ ] Set source name from device + characteristic when creating new 
- [ ] Have references to devices be by address rather than name (in case name changeS)
- [ ] Have default func be identity
- [ ] Add new source to all plotline spin boxes when created
- [ ] Have chunk chooser spin box pull number from config
## Major Features (To Be Split into Tasks)
- [ ] Multiple Device Locking - check bleak docs
- [ ] Read Functionality for BLE
- [ ] Data Saving
- [ ] Data Replaying
## Continuous Integration
- [ ] Testing
- [ ] Logging
