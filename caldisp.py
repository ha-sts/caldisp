#!/usr/bin/local/python

# caldisp.py
# A calendar display using pygame for the HA-STS project.
# Daniel Williams <dwilliams@port8080.net>

### IMPORTS ############################################################################################################
# For the GUI display:
import pygame

# For the weather forecast:
import requests
import json

### GLOBALS ############################################################################################################
# Define some color tuples
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
ltRed = (255, 189, 189)
ltGreen = (189, 255, 189)
ltBlue = (189, 189, 255)

# Define some fonts
font = None

# Define some weather information (I'm using a free developer account from Weather Underground)
weatherURL = "https://api.wunderground.com/api/"
weatherAPIkey = ""
weatherExampleHourly = "%s%s/hourly/q/80504.json" % (weatherURL, weatherAPIkey)
# This can use "CO/Longmont" instead of "80504" for the location information.
# See: http://www.wunderground.com/weather/api/d/docs?d=data/index
degreeSymbol = u'\N{DEGREE SIGN}'

### FUNCTIONS ##########################################################################################################
# Draw a rectangle with rounded corners (borrowed from http://www.pygame.org/project-AAfilledRoundedRect-2349-.html)
def AAfilledRoundedRect(surface,rect,color,radius=5):
    """
    AAfilledRoundedRect(surface,rect,color,radius=5)

    surface : destination
    rect    : rectangle
    color   : rgb or rgba
    radius  : number of pixels (must be less than half the rectangle's shortest dimention)
    """
    rect = pygame.Rect(rect)
    color = pygame.Color(*color)
    alpha = color.a
    color.a = 0
    pos = rect.topleft
    rect.topleft = 0,0
    rectangle = pygame.Surface(rect.size, pygame.SRCALPHA)
    circle = pygame.Surface([min(rect.size) * 3] * 2, pygame.SRCALPHA)
    pygame.draw.ellipse(circle, (0, 0, 0), circle.get_rect(), 0)
    circle = pygame.transform.smoothscale(circle, [int(radius)] * 2)
    radius = rectangle.blit(circle,(0,0))
    radius.bottomright = rect.bottomright
    rectangle.blit(circle,radius)
    radius.topright = rect.topright
    rectangle.blit(circle,radius)
    radius.bottomleft = rect.bottomleft
    rectangle.blit(circle,radius)
    rectangle.fill((0,0,0),rect.inflate(-radius.w,0))
    rectangle.fill((0,0,0),rect.inflate(0,-radius.h))
    rectangle.fill(color,special_flags=pygame.BLEND_RGBA_MAX)
    rectangle.fill((255,255,255,alpha),special_flags=pygame.BLEND_RGBA_MIN)
    return surface.blit(rectangle,pos)



### CLASSES ############################################################################################################

### MAIN ###############################################################################################################
def main():
    pygame.init()

    # Set the window size.
    #width = 640
    #height = 480
    width = 800
    height = 600
    size = (width, height)

    # Initialize the fonts
    font = pygame.font.Font(None, 25)

    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Calendar Display")

    # Used to manage how fast the screen updates.
    fpsClock = pygame.time.Clock()

    # Loop until the user clicks the close button.
    done = False

    # Grab example weather data.  This will need to be put into a loop that checks it once an hour (on a second thread
    # maybe) and updates based on that.
    weatherRequest = requests.get(weatherExampleHourly).json()

    try:
        while not done:
            ### This is the event handling part of the loop.  All event handling happens here.
            for event in pygame.event.get():
                # Close / Quit event
                if event.type == pygame.QUIT:
                    done = True
            ### This is the logic part of the loop.
            ### This is the screen drawing part of the loop.
            screen.fill(white)
            # Draw some rectangles for laying out the areas.  Coordinates are [from left, from top, width, height].
            # Currently have a notification bar, a weather forecast, and a schedule display.  Should probably add a clock to the top right corner.
            AAfilledRoundedRect(screen, [width / 100, height / 100, width - ((width / 100) * 2), (height / 100) * 12], ltRed, (width / 100) * 2)
            AAfilledRoundedRect(screen, [width / 100, (height / 100) * 14, (width / 100) * 30, height - ((height / 100) * 15)], ltBlue, (width / 100) * 2)
            AAfilledRoundedRect(screen, [(width / 100) * 32, (height / 100) * 14, width - ((width / 100) * 33), height - ((height / 100) * 15)], ltGreen, (width / 100) * 2)
            # Draw  some text in the rectangles
            screen.blit(font.render("Today is trash and recycling day!", True, black), ((width / 100) * 2, (height / 100) * 2))
            screen.blit(font.render("Today's weather:", True, black), ((width / 100) * 2, (height / 100) * 15))
            screen.blit(font.render("What are you up to today?", True, black), ((width / 100) * 34, (height / 100) * 15))

            # Draw weather info
            # Add a calculation to figure out how many boxes we can display based on the height.
            weatherPanelHeight = height - ((height / 100) * 15)
            weatherTitleHeight = 30
            weatherEntryHeight = 80
            weatherEntryCount = ((weatherPanelHeight - weatherTitleHeight) // weatherEntryHeight) - 1 # Use integer (floor) division
            weather_yOffset = weatherTitleHeight
            for i in range(weatherEntryCount):
                tmpHour = int(weatherRequest['hourly_forecast'][i]['FCTTIME']['hour'])
                tmpMin = int(weatherRequest['hourly_forecast'][i]['FCTTIME']['min'])
                tmpTemp = int(weatherRequest['hourly_forecast'][i]['temp']['english'])
                tmpPoP = int(weatherRequest['hourly_forecast'][i]['pop'])
                tmpCond = weatherRequest['hourly_forecast'][i]['condition']
                AAfilledRoundedRect(screen, [(width / 100) + 5, ((height / 100) * 14) + weather_yOffset, ((width / 100) * 30) - 10, weatherEntryHeight], blue, (width / 100) * 2)
                pygame.draw.rect(screen, black, [(width / 100) + 5 + 2, ((height / 100) * 14) + weather_yOffset + 2, 77, 77], 0) # Replace this with the condition icon
                screen.blit(font.render("%02d:%02d" % (tmpHour, tmpMin), True, white), ((width / 100) + 5 + 85, ((height / 100) * 14) + weather_yOffset + 2))
                screen.blit(font.render("%d%sF    %d%%" % (tmpTemp, degreeSymbol, tmpPoP), True, white), ((width / 100) + 5 + 105, ((height / 100) * 14) + weather_yOffset + 27))
                screen.blit(font.render("%s" % (tmpCond), True, white), ((width / 100) + 5 + 105, ((height / 100) * 14) + weather_yOffset + 52))
                weather_yOffset += weatherEntryHeight + 5

            ### This is required to push to the screen
            pygame.display.flip()
            fpsClock.tick(30)
    except KeyboardInterrupt:
        # Hide the CTRL-C traceback.
        pass
    finally:
        pygame.quit()

if __name__ == '__main__':
    main()
