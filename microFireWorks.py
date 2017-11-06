from microbit import *
import neopixel
from random import uniform
from random import randint
import math

# Setup the Neopixel strip on pin0 with a length of 60 pixels
np = neopixel.NeoPixel(pin0, 60)
np.clear()

# From colorsys.py - HLS colour system is used to dim exploded fragments without changing colour (hue) but neopixel module uses RGB so need to convert between the two.
ONE_THIRD = 1.0/3.0
ONE_SIXTH = 1.0/6.0
TWO_THIRD = 2.0/3.0

def _v(m1, m2, hue):
    hue = hue % 1.0
    if hue < ONE_SIXTH:
        return m1 + (m2-m1)*hue*6.0
    if hue < 0.5:
        return m2
    if hue < TWO_THIRD:
        return m1 + (m2-m1)*(TWO_THIRD-hue)*6.0
    return m1

def rgb_to_hls(r, g, b):
    maxc = max(r, g, b)
    minc = min(r, g, b)
    # XXX Can optimize (maxc+minc) and (maxc-minc)
    l = (minc+maxc)/2.0
    if minc == maxc:
        return 0.0, l, 0.0
    if l <= 0.5:
        s = (maxc-minc) / (maxc+minc)
    else:
        s = (maxc-minc) / (2.0-maxc-minc)
    rc = (maxc-r) / (maxc-minc)
    gc = (maxc-g) / (maxc-minc)
    bc = (maxc-b) / (maxc-minc)
    if r == maxc:
        h = bc-gc
    elif g == maxc:
        h = 2.0+rc-bc
    else:
        h = 4.0+gc-rc
    h = (h/6.0) % 1.0
    return h, l, s
    
def hls_to_rgb(h, l, s):
    if s == 0.0:
        return l, l, l
    if l <= 0.5:
        m2 = l * (1.0+s)
    else:
        m2 = l+s-(l*s)
    m1 = 2.0*l - m2
    return (_v(m1, m2, h+ONE_THIRD), _v(m1, m2, h), _v(m1, m2, h-ONE_THIRD))
    
while True:
    
    g = 50 #acceleration due to "gravity"
    XL = randint(30,45) #pixel of zenith
    PX = XL - randint(0,10) #pixel at which explosion occurs
    T = math.sqrt(2*XL/g) #time to reach zenith
    v0 = 2*XL/T #initial velocity of firework
    halfnfrags = randint(2,6) #actually one less than half the number of explosion fragments
    nfragments = halfnfrags * 2 + 1 #random (odd) number of explosion fragments
    vfrag = randint(4*halfnfrags,6*halfnfrags) #maximum initial speed of explosion fragments - used to randomly generate speed of individual fragments
    
    t = 0 #time
    C1 = (randint(0,255),randint(0,255),randint(0,255)) #explosion colour 1
    C2 = (randint(0,255),randint(0,255),randint(0,255)) #explosion colour 2
    
    C1HLS = rgb_to_hls(C1[0]/255.0, C1[1]/255.0, C1[2]/255.0) #explosion fragment colour 1 as HLS
    C2HLS = rgb_to_hls(C2[0]/255.0, C2[1]/255.0, C2[2]/255.0) #explosion fragment colour 2 as HLS
    
#LAUNCH FIREWORK
#Effect of gravity during ascent is simulated by calculating time steps between pixel increments
    for i in range(0, PX):
        np[i] = (20,10,0) #show firework at pixel i
        np.show()
        dt = 1 / (v0 - g * t) #time it will take for firework to pass to next pixel (in seconds)
        sleep(dt * 1000) #wait
        t = t + dt #keep track of time
        np[i] = (0,0,0) #turn off pixel i ready to move firework to next pixel

#FLASH FIREWORK AT POINT OF EXPLOSION
    for j in range(0,halfnfrags+1): 
        for i in range(PX-j, PX+j+1):
            np[i] = (255,255,255)
        np.show()
        sleep(10)
    sleep(40)
    for i in range(PX-halfnfrags, PX+halfnfrags+1):
        np[i] = (0,0,0)
    np.show()
    
#EXPLODE FIREWORK
#Firework breaks into nfragments lit fragments (technically nfragments+1 - this last is black. Energy and momentum are usually only conserved if it is assumed to exist ;-))
    exploding = True #Firework is "exploding" as long as at least one fragment still hasn't reached the ground
    Et = 0 #Time explosion has been going on for
    dEt = 15 / 1000 #Incremental time step for explosion. Where firework launch incremented through pixels, explosion increments through time.
			#Best if the value of this is approx the amount of time it takes for one step through fragment animation 
			#See commented out call to sleep function below
    v = v0 - g * t
    
#Initial velocity for fragments (relative to velocity of firework at point of explosion)     
    vm = []
    for i in range(0,nfragments):
        vm.append(uniform(-vfrag,vfrag)+v)
        
    vm.sort()

#Create and initialse initial position, current position and previous position vectors for fragments      
    x = [] #position vector
    x0 = [] #initial position vector
    xp = [] #previous position vector
    for i in range(0, nfragments):
        x0.append(PX - halfnfrags + i)
        x.append(0)
        xp.append(0)

#Luminosity value of explosion fragment colours
    C1L = C1HLS[1]
    C2L = C2HLS[1]
   
#Explosion animation
    while exploding:
        
        #Dim colours
        LC1 = C1L - Et/2.0
        if (LC1 < 0):
            LC1 = 0
        LC2 = C2L - Et/2.0
        if (LC2 < 0):
            LC2 = 0
            
        C1D = hls_to_rgb(C1HLS[0], LC1, C1HLS[2])
        C2D = hls_to_rgb(C2HLS[0], LC2, C2HLS[2])
        
        C1D = (int(C1D[0]*255), int(C1D[1]*255), int(C1D[2]*255))
        C2D = (int(C2D[0]*255), int(C2D[1]*255), int(C2D[2]*255))

        #Calculate position of fragments
        for i in range(0,nfragments):
            #next position of fragments
            x[i] = int(round(x0[i] + (vm[i] * Et) - (g * Et *Et / 2)))
            #turn off current fragments ready to move to next pixel - if next pixel is not the same and current pixel is in range            
            if ((xp[i] < len(np)) and (xp[i] >= 0) and (x[i] != xp[i])):
                np[xp[i]] = (0,0,0)
            #move fragments to next pixel
            if ((x[i] < len(np)) and (x[i] >= 0)):
                np[x[i]] = C1D
                if (i == 2 * int(i / 2.0)): #if i is even use colour 2
                    np[x[i]] = C2D
    
        np.show() #show fragments
        #sleep(dEt * 1000) #wait - not needed since introduction of dimming which in itself takes time. Note Et still needs to increment though.
        
        for i in range(0, nfragments):
            xp[i] = int(x[i])

        Et = Et + dEt #increment time by dEt
        
        #Check to see if any fragments are still in the air
        exploding = False 
        for i in range(0,nfragments):
            if (x[i]>0):
                exploding = True

        
    

        
    
