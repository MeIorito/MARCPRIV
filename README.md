# MARC 3D Scanner Application

## Table of Contents
- [Introduction](#introduction)
- [Software](#software)
  - [Features](#features)
  - [Getting Started](#getting-started)
  - [Class Overview](#class-overview)
    - [`cycleThread`](#cyclethread)
    - [`MainWindow`](#mainwindow)
    - [`NewKeyframeWindow`](#newkeyframewindow)
    - [`EditKeyframeWindow`](#editkeyframewindow)
    - [`KeyframeCalculator`](#keyframecalculator)
  - [Usage](#usage)
  - [Dependencies](#dependencies)
  - [Contributions](#contributions)
- [Hardware](#hardware)
- [License](#license)

## Introduction

The MARC 3D Scanner provides an opertunity for 3D scanning cheaply and easily. It has an interface for controlling a 3D scanning device, MARC (Motorised Rlternate Reality Capture). It allows users to adjust scanning parameters, manage keyframes, and initiate scanning cycles for scanning object to get a  realistic 3D model. This application is built using PyQt5 and integrates with Slack for real-time notifications. 

MARC uses Photogrammetry to scan objects. The object spins on a turntable while the camera makes pictures from different heights and angles. These pictures are then put in software that creates a 3D model. And finaly are cleaned by real people.
Keyframes are the combination of height and angle for a position. There can be an unlimited amount of keyframes, wich can be cycled through for a perfect 360 view of an object.

![MARC picture](../readmePics/marcPic1.jpg)

Click [here](https://we.tl/t-bFW5XTTR4l) for a production video.

# Software

## Features

- **Real-time Control**: Adjust scanner parameters such as height and tilt angle in real-time using a graphical interface.

- **Keyframe Management**: Easily dynamically create, edit and delete keyframes to define scanning positions and settings using a graphical interface.

- **Scanning Cycles**: Initiate scanning cycles with the click of a button, and monitor progress with real-time Slack notifications.

- **Pictures per keyframe**: Edit the amount of pictures taken with each keyframe in real time.

- **Wait times**: Edit the time the scanner waits before and after taking a picture before doing anything else.

- **Zero Position**: Set a new reference position (zero) for the scanner to start scanning cycles from.

- **Keyframe Calculator**: Automatically calculate and add keyframes based on predefined scanning patterns. 

## Getting Started

1. Clone this repository to your Raspberry Pi.
2. Install the required dependencies (see [Dependencies](#dependencies)).
3. Run the application using Python.

## Class Overview

### `cycleThread`

The `cycleThread` class represents a background thread responsible for managing the scanning cycle. It handles moving the scanner to different keyframe positions, capturing images, and sending status updates to a Slack workspace without freezing the GUI. Keyframe data and scanning parameters are loaded from a settings file.

### `MainWindow`

The `MainWindow` class is the central GUI window of the application. It provides the following features:

- Real-time controls for adjusting scanner parameters.
- Initiating scanning cycles with real-time Slack notifications.
- Keyframe management, including adding, editing, and deleting keyframes.
- Wait time management, before and after taking a picture.
- Setting a new reference position (zero) for the tilt position.
- Emergency stop functionality.

### `NewKeyframeWindow`

The `NewKeyframeWindow` class allows users to create and add new keyframes to the scanning process. Users can specify the desired height and tilt angle for each keyframe. Multiple keyframes can be added, and they are stored in a JSON settings file.

### `EditKeyframeWindow`

The `EditKeyframeWindow` class enables users to edit existing keyframes. It provides controls to adjust the height and tilt angle of selected keyframes. Edits are saved to the settings file.

### `KeyframeCalculator`

The `KeyframeCalculator` class is a separate window for calculating and adding keyframes based on predefined scanning patterns. It performs trigonometric calculations to determine keyframe positions based on scanner parameters. The calculated keyframes are stored in the settings file for later use. ![ALT TEXT](../IMAGE_PATH/image.png)

## Usage

1. Launch the application.
2. Make sure that the scanner is at the lowest position and that the camera is perfectly straight.
3. Manage keyframes through the "KEYFRAME MENU" button, allowing you to add, edit, and delete keyframes.
3. Asjust the wait times to your desired time.
4. adjust the pictures per keyframe to your desired amount.
3. Click the "START CYCLE" button to initiate a scanning cycle.
5. Use the "SET NEW ZERO" button to set a new tilt reference position for scanning if it drifted slightly.
6. Try the "Keyframe Calculator" window to automatically calculate and add keyframes based on predefined patterns. (Still in BETA)


## Dependencies

The following dependencies are required to run the application:

- Python 3
- PyQt5
- Slack API (for sending messages to Slack)
- JSON (for storing keyframe data)

## Contributions

Contributions to this codebase are welcome. You can enhance existing features, improve the user interface, fix issues, or add new functionalities. Feel free to open pull requests and contribute to the project's development.

# Hardware

## Being worked on...

## License

This application is provided under the [MIT License](LICENSE).

---

Thank you for using the MARC 3D Scanner Application. Happy scanning!
