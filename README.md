# hass-blueair
A simple BlueAir sensor and fan integration for HomeAssistant.

The basic sensor integration uses the [unofficial BlueAir client](https://github.com/thedjinn/blueair-py) by @thedjinn gather information from the sensors and control the fan with @spikeyGG's implimentation on BlueAir filters 

## Compatibility 
A note on compatibility and testing, I only have 280i filters. The API response from blueair is different for other series of filters, and these differences may break the integration. Several people have contributed patches to make this integration work with other BlueAir models, and I'm really grateful for that help.

## Installation
- Copy custom_components/blueair to your HomeAssistant base config directory (the place where configuration.yaml lives)
- Add the "BlueAir" integration in the configuration.

![HASS BlueAir Device](https://github.com/aijayadams/hass-blueair/blob/main/device.png)
