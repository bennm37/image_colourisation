# Case Study in Scientific Computing
This was a group project for the Mathematical Modelling and Scientific Computing MSc in which we created a GUI for recolorising black and white images with limited colour information. The underlying algorithm relies on reproducing kernel hilbert spaces. We also investigated optimising the parameters of the model using bayesian optimisation.

## Installation
Clone the repository:\
```git clone https://github.com/bennm37/image_colourisation.git```\
Change directory to the repository:\
```cd image_colourisation```\
Create a virtual environment:\
```python -m venv venv```\
NOTE python>=3.10 is required for ```match``` statements.
Activate the virtual environment:\
```source venv/bin/activate```\
Install the requirements:\
```pip install -r requirements.txt```\
Good to go! Try running gui/main.py


## Working Updates

### GUI
- `main.py` seems to be largely functional as of 02-01.
- `main.py` needs to be ran from within the /gui/ folder at the moment ~~and will only work on linux or mac unless the file paths within the script are changed to windows format.~~ UPDATE 30-01: should work on windows, need to test. 

### Optimisation
Going to work on narrowing this down but so far we have:
- delta = 0.0200503376714422,
- sigma_1 = 96
- sigma_2 = 87.09553004603107,
- rho = 0.5644138192495579.

### Images
Within `trainingImages` there are 4 subdirectories:
1. 256px square cartoon images
1. 256px square 'real life' images
1. 512px square cartoon images
1. 512px square 'real life' images
