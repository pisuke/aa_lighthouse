# aa_lighthouse
Code for controlling the light in the 2020 Mark Fisher Scholarship performance event "A Love Letter to the Lighthouse in the Expanded Field" at the Architectural Association, London.

## Installation

1. Get the `ble_xim_pkg` from [Xicato](http://www.xicato.com)
2. `pip install -r requirements.txt`
3. `python lighthouse_xim_cycle.py`

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
Number of XIM LEDs: 3
Enter:
	d to detect and print devices
	b to set individual LED brightness
        a to set all lights to maximum brightness
        o to switch off all lights
	s to start the dimming sequence
	e to end the dimming sequence
	? show commands
	q to quit
>
```


### OSC Messages: via [TouchOSC](https://hexler.net/products/touchosc)
- `/1/push{1,2}`: On / Off for all LEDs
- `/1/push{3,4}`: On / Off for rotational dimming
- `/2/rotary{1-8}`: Set individual LEDs intensity

![](https://user-images.githubusercontent.com/317202/73316701-a35c8d00-422b-11ea-9828-df7412e56ef2.png)
![](https://user-images.githubusercontent.com/317202/73316700-a35c8d00-422b-11ea-98e8-fbd8146597d4.png)