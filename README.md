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

The MARC 3D Scanner provides an opportunity for affordable and accessible 3D scanning. It interfaces with MARC (Motorised Alternate Reality Capture), a 3D scanning device, allowing users to adjust scanning parameters, manage keyframes, and initiate scanning cycles to create realistic 3D models. Built with PyQt5, it integrates with Slack for real-time notifications.

MARC employs Photogrammetry, where objects rotate on a turntable while the camera captures images from varying heights and angles. These images are processed through software to create 3D models, which are refined by human touch. Keyframes, representing height and angle combinations, facilitate a 360-degree view of objects.

![MARC picture](../readmePics/kfcExplenation.png)

Watch our [production video](https://we.tl/t-bFW5XTTR4l) for a detailed demonstration.

# Software

## Features

- **Real-time Control**: Adjust scanner parameters like height and tilt angle in real-time using a user-friendly graphical interface.

- **Keyframe Management**: Dynamically create, edit, and delete keyframes with ease to define scanning positions and settings, all via an intuitive interface.

- **Scanning Cycles**: Initiate scanning cycles with a single click, monitoring progress through real-time Slack notifications.

- **Pictures per Keyframe**: Edit the number of pictures taken with each keyframe in real time.

- **Wait Times**: Customize the time the scanner waits before and after capturing pictures.

- **Zero Position**: Set a new reference position (zero) for the scanner to start scanning cycles from.

- **Keyframe Calculator**: Automatically calculate and add keyframes based on predefined scanning patterns, enhancing efficiency.

## Getting Started

1. Clone this repository to your Raspberry Pi.
2. Install the required dependencies (see [Dependencies](#dependencies)).
3. Run the application using Python.

## Class Overview

### `cycleThread`

The `cycleThread` class manages scanning cycles, handling scanner movement, image capture, and Slack status updates without freezing the GUI. Keyframe data and scanning parameters are loaded from a settings file.

### `MainWindow`

The `MainWindow` class is the core GUI window, offering:

- Real-time controls for adjusting scanner parameters.
- Initiating scanning cycles with real-time Slack notifications.
- Keyframe management: add, edit, delete keyframes.
- Wait time management, pre and post-picture capture.
- Setting a new reference position (zero) for tilt.
- Emergency stop functionality.

### `NewKeyframeWindow`

The `NewKeyframeWindow` allows users to create and add new keyframes. Specify height and tilt angles for each keyframe, storing multiple keyframes in a JSON settings file.

### `EditKeyframeWindow`

The `EditKeyframeWindow` enables users to edit existing keyframes, adjusting height and tilt angles. Edits are saved to the settings file.

### `KeyframeCalculator`

The `KeyframeCalculator` calculates and adds keyframes based on predefined patterns, enhancing efficiency. Calculated keyframes are stored for later use.

## Usage

1. Launch the application.
2. Ensure the scanner is at its lowest position and the camera is level.
3. Manage keyframes via the "KEYFRAME MENU" button: add, edit, delete.
4. Adjust wait times and pictures per keyframe as needed.
5. Click "START CYCLE" to initiate a scanning cycle.
6. Use "SET NEW ZERO" to set a new tilt reference position if needed.
7. Explore "Keyframe Calculator" to auto-calculate and add keyframes based on patterns (BETA).

## Dependencies

To run the application, install these dependencies:

- Python 3
- PyQt5
- Slack API (for Slack notifications)
- JSON (for keyframe data storage)

## Contributions

We welcome contributions! Enhance features, improve the UI, fix bugs, or add new functionalities. Feel free to open pull requests and contribute to the project's development.

# Hardware

Work in progress...

## License

This application is licensed under the [MIT License](LICENSE).

---

Thank you for choosing the MARC 3D Scanner Application. Happy scanning!