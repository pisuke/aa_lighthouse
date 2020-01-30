# aa_lighthouse
Code for controlling the light in the 2020 Mark Fisher Scholarship performance event "A Love Letter to the Lighthouse in the Expanded Field" at the Architectural Association, London.

## Hardware Configuration

1. Set up the XIM LEDs with incremental ID number, for instance from 1 to n, where n is the total number of XID LEDs.
2. Set up a group with all the XIM LEDs. The default group number is 10.

## Software installation

1. (Optional) `conda create -n lighthouse python=2.7.16`
2. Get the `ble_xim_pkg` from [Xicato](http://www.xicato.com)
3. `pip install -r requirements.txt`
4. `python lighthouse_xim_cycle.py`

The output is something like this

```
   _            _         _
\_|_)  o       | |       | |
  |        __, | |   _|_ | |     __          ,   _
 _|    |  /  | |/ \   |  |/ \   /  \_|   |  / \_|/
(/\___/|_/\_/|/|   |_/|_/|   |_/\__/  \_/|_/ \/ |__/
            /|
            \|

 _ _      _   _   _                        _           _
| (_)__ _| |_| |_(_)_ _  __ _   __ ___ _ _| |_ _ _ ___| |
| | / _` | ' \  _| | ' \/ _` | / _/ _ \ ' \  _| '_/ _ \ |
|_|_\__, |_||_\__|_|_||_\__, | \__\___/_||_\__|_| \___/_|
    |___/               |___/

Detecting XIM LEDs, please wait ...
 Number of XIM LEDs: 1
Enter:
	d to detect and print devices
	b to set individual LED brightness
	f to set fading time
	g to set the active group number
	a to set all lights to maximum brightness
	o to switch off all lights
	s to start the rotating dimming sequence
	e to end the rotating dimming sequence
	0 to start the breathing sequence
	1 to end the breathing sequence
	2 to start the breathing fading sequence
	3 to end the breathing fading sequence
	? show commands
	q to quit
```


### OSC Messages: via [TouchOSC](https://hexler.net/products/touchosc)

When running the OSC server using `python lighthouse_xim_cycle.py -osc`, the following end points are usable

- `/1/push{1,2}`: On / Off for all LEDs
- `/1/push{3,4}`: On / Off for rotational dimming
- `/2/rotary{1-8}`: Set individual LEDs intensity

![](https://user-images.githubusercontent.com/317202/73316701-a35c8d00-422b-11ea-9828-df7412e56ef2.png)
![](https://user-images.githubusercontent.com/317202/73316700-a35c8d00-422b-11ea-98e8-fbd8146597d4.png)
