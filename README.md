# hass-blueair
A simple BlueAir sensor integration for HomeAssistant.

The basic sensor integration uses the [unofficial BlueAir client](https://github.com/thedjinn/blueair-py) by @thedjinn gather information from the sensors on BlueAir filters.

Currently the client is embeded with this [pull request](https://github.com/thedjinn/blueair-py/pull/1) applied to support my units. If this (or a better) fix is merged we can remove the client and just add the PIP blueair requirement.

## Installation
- Copy custom_components/blueair to your HomeAssistant base config directory (the play where configuration.yaml lives)
- Configure the blueair sensor with your credentials
```yaml
sensor:
  - platform: blueair
    user: "<you>@gmail.com"
    password: "1337p@szw0Rd"
```
