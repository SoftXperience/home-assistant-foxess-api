# FoxESSCloud API Integration for Home-Assistant

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