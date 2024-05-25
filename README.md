# Dropbox files downloader
------

A simple script to download your files from dropbox. Dropbox has made so difficult to download your own data
if you have hundreds or thousands of files in their system.


## Usage

* Install dropbox python library `pip install dropbox`
* Clone this repo, then execute next command inside of repo folder.
  * `./src/downloader.py <ACCESS_TOKEN> -p <local_path_to_save_files> -d <dropbox_path>`

If `-p` option is not used files are going to be saved in the path where the script is executed.
If `-d` option is not used then all files are going to be downloaded.

To get the `ACCESS_TOKEN` login to dropbox and then got to https://www.dropbox.com/developers/,
click in "Application console" then click button "Create App".
Add reading and writing permissions to your app and press button "Generate access token", copy generated token.

**Note**: Access token is temporal it may expire in the middle of a download, so you could need to execute
the script many times.
 