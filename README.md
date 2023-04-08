# homeassistant-freeds

`homeassistant-freeds` is a [Home Assistant](https://www.home-assistant.io) integration for [FreeDS](https://freeds.es/) devices (power surplus management devices).

## Installation

#### Guided installation

- Enable the [HACS](https://hacs.xyz/) integration in your Home Assistant instance.
- Use the side menu to browse HACS.
- Navigate to "Integrations", then use the overflow menu (three dots at the top-left) to add a Custom Repository.
- Enter the URL for this repository: `https://gitlab.com/IvanSanchez/homeassistant-freeds`

#### Manual installation

Download the files from this repository. Copy the `custom_components/freeds/` directory into the `custom_components` directory of your Home Assistant instance.

e.g. if your configuration file is in `/home/homeassistant/.homeassistant/configuration.yaml`, then the files from this integration should be copied to `/home/homeassistant/.homeassistant/custom_components/freeds/`.

Restart Home Assistant to ensure the integration can be detected.

## Usage

Use the Home Assistant GUI to add a new integration (settings → devices & services → add new integration). You should find the FreeDS integration in the list.

Enter the IP address (or hostname) of your FreeDS device. Note that **no checks are made to ensure that there is a FreeDS device at that IP address**.

Home Assistant should display a new *Device* with a dozen *Sensors*, such as:

![Screenshot of FreeDS sensors in Home Assistant](./screenshot.png)

## License

Licensed under GPLv3. See the `LICENSE` file for details.
