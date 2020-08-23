# Random-File-Executer
runs random files with default application in specified directories.

## How to use:

Download the latest version of rfe.exe from [Download page.](https://github.com/wompi72/Random-File-Executer/releases) and put it in your preferred directory.

Start the rfe.exe (Your Antivirus software probably won't like it, because this app executes a command to start the file. You have access to the source code, so decide for yourself, if you want to risk trusting me.)

Click on *Add category* to add a directory, from which the app will choose a random file to start.  
![image](https://user-images.githubusercontent.com/70111121/90988062-1cd51780-e590-11ea-8fdf-3122109762e6.png)  
For example the directory, where you store your funny cat videos. If you do the same for your duck videos, your app should look something like this:  
![image](https://user-images.githubusercontent.com/70111121/90988200-68d48c00-e591-11ea-9442-4f54e4c4ee73.png)  
The weight determines the possibility of choosing the category. So if u want to watch double the duck videos than cat videos, you set the ducks weight to 2 and leave the cats at 1.
When you press on *Execute File*, the app chooses a random video to start and closes itself.

### Other options:
I didn't program options to change some configurations from the app yet. So you have to change them in the *config.json* file. For example, you can change:

```
"close_on_execute": true
```
to
```
"close_on_execute": true
```
and the app will stay open, after executing the chosen file.

#### different file types
You can also change the file types that are chosen. If you change
```
"executables": [".mp4",".mov",".wmv",".flv",".avi"],
```
to
```
"executables": [".mp4",".mov",".wmv",".flv",".avi",".txt"],
```
normal text files will also be open. If you remove all file types from this list, any file in the chosen directories can be started:
```
"executables": [],
```
