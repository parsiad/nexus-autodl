# Nexus AutoDL

<p align="center">
  <img alt="Nexus AutoDL" src="https://raw.githubusercontent.com/parsiad/nexus-autodl/master/assets/img/logo.png">
</p>

When downloading mods from [Nexus Mods](https://nexusmods.com), you have to manually click on a download button every time a new mod is added to the queue.
Since modlists supported by tools like [Wabbajack](https://www.wabbajack.org) and [Portmod](https://gitlab.com/portmod/portmod) often have tens or hundreds of mods, this can be very time consuming.
Nexus AutoDL is an autoclicker (a.k.a., autodownloader, bot) that helps automate this process for you.
Specifically, while Nexus AutoDL is running, any time a [mod download page](https://raw.githubusercontent.com/parsiad/nexus-autodl/master/assets/mod_download_page.jpg) is visible on your screen, Nexus AutoDL will attempt to click the download button. 

Nexus AutoDL will can also helo with installing Nexus Collections, as with a free account you must manually click the [download button in the client](assets/vortex-dl.png) for each mod. As with the Nexus site, when this download button is visible on your screen, Nexus AutoDL will attempt to click it.

## Download

👉 [Visit the website](https://parsiad.github.io/nexus-autodl) 👈 to download

## Python Requirements
In order to run the Python script, the following packages are required to be installed:
- opencv-python
- Pillow
- click
- PyAutoGUI
- numpy
- typing*

**included as part of the standard library as of Python 3.5+*