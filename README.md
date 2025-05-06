#Video Streaming Site

Features:
- Multiple video support
- Multiple simultaneous user support
- Upload function
- GUI with play/pause, skip forward/backwards

##To Use:
1. Download file and unzip
**ON A PRIVATE NETWORK:**
2. One machine runs server.py, note this machines IP address
3. A secone machine runs client.py, using the first machines IP to connect.
4. The client machine can then see all available videos on the server using the "List Available Videos" button
5. Type a video name into the box next to "Select Video" and press "Select"
6. Use playback buttons to control video playback
7. Click X on the window to quit the application

##To Upload:
1. Type the path on your machine to the video you'd like to upload
2. Click Upload
3. To check if this worked correctly, list the available videos and ensure your video appears


##Notes:
- Video files are split into mp4 video and wav audio files when they are uploaded, and both are stored on the server
- Maximum buffer size is 1 minute forward and backward - trying to go back further than this may require more buffer time