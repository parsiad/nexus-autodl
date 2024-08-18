# Nexus AutoDL

<p align="center">
  <img alt="Nexus AutoDL" src="https://raw.githubusercontent.com/parsiad/nexus-autodl/master/assets/img/logo.png">
</p>

When downloading mods from [Nexus Mods](https://nexusmods.com), you have to manually click on a download button every time a new mod is added to the queue.
Since modlists supported by tools like [Wabbajack](https://www.wabbajack.org) and [Portmod](https://gitlab.com/portmod/portmod) often have tens or hundreds of mods, this can be very time consuming.
Nexus AutoDL is an autoclicker (a.k.a., autodownloader, bot) that helps automate this process for you.
Specifically, while Nexus AutoDL is running, any time a [mod](https://raw.githubusercontent.com/parsiad/nexus-autodl/master/assets/mod_download_page.jpg) or [collection](https://raw.githubusercontent.com/parsiad/nexus-autodl/master/assets/vortex_download_page.jpg) download page is visible on your screen, Nexus AutoDL will attempt to click the download button.

If you like Nexus AutoDL, please leave a star on GitHub to help others find it.

## Download

A Windows binary is available on the [releases page](https://github.com/parsiad/nexus-autodl/releases).
Download it and double-click on it to start Nexus AutoDL.
The first time you run the application, you will be presented with some instructions.
Follow the instructions and relaunch it.
This spawns a terminal window which you can close when you are done downloading mods.

Users on other platforms can download the source code on GitHub.

## Usage

```text
nexus_autodl.py [OPTIONS]

Options:
  --confidence FLOAT              Specifies the accuracy with which the script 
                                  should find the screenshot button [default:0.7]
  --grayscale / --color           Try to locate button using only desaturated
                                  images, can speed up the locating action
                                  [default: grayscale]
  --min-sleep-interval INTEGER    Minumal amount of time to wait between every
                                  click attempt  [default: 1]
  --max-sleep-interval INTEGER    Minumal amount of time to wait between every
                                  click attempt  [default: 5]
  --retries-before-scroll INTEGER
                                  Amount of failed attemps before trying to
                                  scroll down  [default: 3]
  --disable-transparent-ads-fix BOOLEAN
                                  Disable the functionality that can
                                  potentially locate transparent ads which
                                  prevent clicking  [default: False]
  --templates-path TEXT           Set a path to the folder with button screenshots
                                  [default: <current dir>\templates]
  --help                          Show this message and exit.
```

## Caution

Using a bot to download from Nexus is in direct violation of their TOS:

> Attempting to download files or otherwise record data offered through our services (including but not limited to the Nexus Mods website and the Nexus Mods API) in a fashion that drastically exceeds the expected average, through the use of software automation or otherwise, is prohibited without expressed permission.
> Users found in violation of this policy will have their account suspended.

Use this at your own risk.
