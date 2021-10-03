# hass-blueair
A simple BlueAir sensor and fan integration for HomeAssistant.

The basic sensor integration uses the [unofficial BlueAir client](https://github.com/thedjinn/blueair-py) by @thedjinn gather information from the sensors and control the fan with @spikeyGG's implimentation on BlueAir filters 

A note on testing, I only have 280i filters, there is a good chance that other models might change the API response in ways that break this integration.


## Installation
- Copy custom_components/blueair to your HomeAssistant base config directory (the place where configuration.yaml lives)
- Add the "BlueAir" integration in the configuration.

![HASS BlueAir Device](https://github.com/aijayadams/hass-blueair/blob/blueair_device/device.jpg?raw=true)
