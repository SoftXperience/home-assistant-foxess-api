# FoxESSCloud API Integration for Home-Assistant

<a href="https://github.com/hacs/default"><img src="https://img.shields.io/badge/HACS-default-sucess"></a>
<a href="https://github.com/SoftXperience/home-assistant-foxess-api/actions/workflows/hacs.yaml?branch=main"><img src="https://github.com/SoftXperience/home-assistant-foxess-api/actions/workflows/hacs.yaml/badge.svg?branch=main"/></a>
<a href="https://github.com/SoftXperience/home-assistant-foxess-api/actions/workflows/hassfest.yaml"><img src="https://github.com/SoftXperience/home-assistant-foxess-api/actions/workflows/hassfest.yaml/badge.svg"/></a>

This is a custom component for Home Assistant to provide access to the data of your FoxESS photovoltaics inverter data.

It uses a subset of the official API of FoxESSCloud which can
be [found here](https://www.foxesscloud.com/public/i18n/en/OpenApiDocument.html).

## Installation

Use [hacs.xyz](https://hacs.xyz) to install and update it.

Add `https://github.com/SoftXperience/home-assistant-foxess-api` to the user-defined repositories.

Then install this integration.

## Manual installation

Put content of `custom_components` folder into your Home-Assistant `/config/custom_components` folder.

## Configuration

Add the integrations from the integrations dashboard. Enter your API key and the inverter serial number.

You can find these data in the FoxESSCloud portal. The API key can be generated in your user profile.

## API calls rate limit

Each API key is limited to 1440 calls per day. As we need 2 calls per update, the update interval is set to 3 minutes to
be safe.
Also, according to my monitoring, the datalogger seems to only update every 4-6 minutes anyways. 