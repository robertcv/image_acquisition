# image_acquisition

A simple gui to acquire images from the web.
It saves the images as expected for the 1. assignment on the course Image Based
Biometry 2018/19

### Installation & run
Use Python 3.6 and above.

**Change the `BITBUCKET_NAME` variable in the `image_acquisition.py`!**
```bash
pip install -r requirements.txt
python image_acquisition.py
```

### Usage
Copy image url into source. Fill out the data about the subject.
If you want to crop the image just select a region. On save the subject data and
selected part of the image (if no part is selected the whole image is used) are
saved according to the assignment specification.


### Issues
Was tested on Ubuntu 18. Probably won't work in windows due to backslash spiting.
If you have any problems pleas submit a pull request with the fix. I will not
provide any additional support.