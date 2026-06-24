# A-Level AQA NEA project Alpha Bracelet Generator
import pygame as pg
pg.init()
import pygame.gfxdraw as gfx
import os
import sys


surface = pg.display.set_mode((0, 0), pg.RESIZABLE)  # window

defaultColor = (56, 56, 56)

clock = pg.time.Clock()

knotMap = None


# the button class creates a green button wherever the position is set, and will return whether it has been pressed
# when isPressed is called
class button:
    # set button variables and display button with the label text, eg: showTxt=“Apply”
    def __init__(self, screen, x, y, w, h, showTxt=""):
        self.screen = screen
        self.txtInput = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y

        self.medTxt = pg.font.Font(None, 20)
        self.text = self.medTxt.render(showTxt, True, (0, 0, 0))

        pg.draw.rect(screen, (0, 204, 102), self.txtInput, border_radius=5)
        screen.blit(self.text, (self.x + 15, self.y + 9))

    # return True if mouse is clicked over button area, if not return false
    def isPressed(self, event):
        if self.txtInput.collidepoint(event.pos):
            return True
        else:
            return False

# the color picker creates a slider that goes through a rectangle that displays all colors in RGB or greyscale, if the
# user drags the mouse over the rectangle’s surface, the circle that represents the current color moves to that
# vertical position and updates the color to whatever color the rect was under the circle.
class ColorPicker:
    # set color slider variables and display rect with the full RGB or greyscale spectrum
    def __init__(self, x, y, l, size, screen, isGreyScale):
        self.rect = pg.Rect(x, y, size, l)
        self.image = pg.Surface((size, l))
        self.image.fill((255, 255, 255))
        self.rad = size // 2
        self.screen = screen
        if isGreyScale:
            self.color = (0, 0, 0)
        else:
            self.color = (255, 0, 0)
        self.pwidth = l - self.rad * 2
        self.isGreyScale = isGreyScale

        for i in range(self.pwidth):
            color = pg.Color(0)
            if not self.isGreyScale:
                color.hsla = (int(360 * i / self.pwidth), 100, 50, 100)
            else:
                value = int(255 * i / self.pwidth)
                color = (value, value, value)

            pg.draw.rect(self.image, color, (size // 3, i + self.rad, size - 2 * size // 3, 1))
            screen.blit(self.image, self.rect)
        self.p = 0

    # check if the mouse is over the rectangle surface and if so update the circle to the mouses’s y position
    # and update the current color
    def update(self):
        mouse_buttons = pg.mouse.get_pressed()
        mouse_pos = pg.mouse.get_pos()
        if mouse_buttons[0] and self.rect.collidepoint(mouse_pos):
            self.p = (mouse_pos[1] - self.rect.top - self.rad) / self.pwidth
            self.p = (max(0, min(self.p, 1)))

            getColor = pg.Color(0)
            if not self.isGreyScale:
                getColor.hsla = (int(self.p * 360), 100, 50, 100)
            else:
                value = int(255 * self.p)
                getColor = (value, value, value)
            self.color = getColor

        self.screen.blit(self.image, self.rect)
        center = self.rect.centerx, self.rect.top + self.rad + self.p * self.pwidth
        pg.draw.circle(self.screen, self.color, center, self.rect.width // 2.5)

        # if the mouse is over the rectangle’s surface then the color has been changed and the new color is returned
        if mouse_buttons[0] and self.rect.collidepoint(mouse_pos):
            return self.color

# the text box is updated to check if the mouse has been clicked on it, if so the label text eg: showTxt=“Strings”
# is turned red to show that the user can type, and the code starts checking for keystrokes
class txtInputBox:
    # set variables
    def __init__(self, screen, x, y, w, h, label="", txt=""):
        self.txtInput = pg.Rect(x, y, w, h)
        self.txt = txt
        self.enterTxt = False
        self.largeTxt = pg.font.Font(None, 32)
        self.medTxt = pg.font.Font(None, 20)
        self.txt_surface = self.largeTxt.render(self.txt, True, (0, 255, 0))
        self.label = label
        self.text = self.medTxt.render(label, True, (0, 0, 0))
        self.w = w
        self.screen = screen
        self.color = (92, 93, 95)
        self.x = x
        self.y = y

    # if no characters have been entered display the label text, if not display the characters being entered
    def displayTxt(self):
        if self.txt == "":
            self.screen.blit(self.text, (self.x + 5, self.y + 5))
        else:
            #render the text and calculate the area on the left to hide if there are more letters than space
            self.txt_surface = self.largeTxt.render(self.txt, True, (0, 0, 0))
            offset = max(0, self.txt_surface.get_width() - self.w + 6)
            crop = (offset, 0, self.w, self.txt_surface.get_height())
            self.screen.blit(self.txt_surface, (self.txtInput.x + 5, self.txtInput.y + 3), crop)


    # if a new character is entered or removed the whole text is removed and redrawn by filling the area with a white
    # rectangle, this makes sure the current text is always displayed
    def update(self):
        inner = self.txtInput.inflate(-2, -2)
        self.screen.fill((255, 255, 255), inner)
        self.txtInput.w = self.w
        pg.draw.rect(self.screen, self.color, self.txtInput, 2, border_radius=5)

    # event is called to check if the mouse has clicked over the text box, if so a boolean is set to true so if text
    # is entered it adds them to text string, this stops characters being saved even when the user is
    # entering characters into the other text box
    def event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.txtInput.collidepoint(event.pos):
                self.text = self.medTxt.render(self.label, True, (255, 0, 0))
                self.screen.blit(self.text, (self.x + 5, self.y + 5))
                self.enterTxt = True
                self.txt = ""
            else:
                self.enterTxt = False

        # if key pressed is the backspace then delete the last character in the text string, if not add the character to the string
        if event.type == pg.KEYDOWN:
            if self.enterTxt:
                if event.key == pg.K_BACKSPACE:
                    self.txt = self.txt[:-1]
                    self.displayTxt()
                else:
                    self.txt += event.unicode
                    self.displayTxt()

                # if the character being entered is not an integer the text box turns red to show that the user
                # has entered an illegal character
                if not self.txt.isdigit():
                    self.color = (255, 0, 0)
                else:
                    self.color = (92, 93, 95)

# knotList is the class used to create the bitmap containing all the information for the pattern, width, length,
# position, and a list containing every knot and storing it by its color. The x and y position is needed for
# editBitmap so the grid can be recreated exactly where it is visually, if not the knot added would not match the
# visual position of the knot.
class knotList:
    def __init__(self, width, length):
        self.width = width
        self.length = length
        self.braceletKnots = []
        self.x = 0
        self.y = 0

    class knotInfo:
        def __init__(self, color):
            self.color = color


# this takes the users mouse position and loops through knotMap, checking the position of each cube in the grid to see
# if its position matches the mouse's position
def editBitmap(screen, pos, bitmap, size, color=0):
    spacing = size + 1
    if not bitmap is None:
        found = False

        knotCount = 0
        # run until a knot with the same position is found or loop reaches the end of knotMap
        while found == False:
            for yRow in range(bitmap.length):
                for xRow in range(bitmap.width):
                    testKnot = pg.Rect(xRow * spacing + bitmap.x, yRow * spacing + bitmap.y, size, size)
                    if testKnot.collidepoint(pos):
                        bitmap.braceletKnots[knotCount].color = color
                        pg.draw.rect(screen, bitmap.braceletKnots[knotCount].color,
                                     (xRow * spacing + bitmap.x, yRow * spacing + bitmap.y, size, size))
                        found = True
                    elif xRow >= bitmap.width - 1:
                        found = True
                    knotCount = knotCount + 1

# this creates a bitmap and stores it in knotMap, sets the bitmap to the default color or simply displays the existing bitmap
def createBitmap(screen, x, y, size, bitmap, defaultColor, create=False, width=0, length=0):
    spacing = size + 1

    # if user wants to create a new bitmap or change the size of the current one.
    if create == True:
        # if the knotMap has not yet been created or the current bitmap is still the same size as before set the width
        # and length and set all knots (pixels) to the default color (gray) and draw the pattern
        if bitmap == None or bitmap.width == width and bitmap.length == length:
            bitmap = knotList(width, length)
            bitmap.x = x
            bitmap.y = y
            bitmap.braceletKnots.clear()

            for knot in range(bitmap.width * bitmap.length):
                bitmap.braceletKnots.append(bitmap.knotInfo(defaultColor))

        # else if the bitmap already exists and the user entered a new width or length, change the size of the bitmap by
        # adding or removing the difference of size in width or height, this allows the user to change their size
        # without losing what they were previously working on, if the new size is smaller than any knot that have been
        # created in that area will be removed.
        else:
            for runDownList in range(bitmap.length - 1, - 1, - 1):
                for difference in range(abs(bitmap.width - width)):
                    if bitmap.width < width:  # if new width is bigger
                        bitmap.braceletKnots.insert(runDownList * bitmap.width + bitmap.width,
                                                    bitmap.knotInfo(defaultColor))
                    else:  # if new width is smaller
                        bitmap.braceletKnots.pop(runDownList * bitmap.width + width)
            bitmap.width = width

            for difference in range(abs(bitmap.length - length)):
                for runUpList in range(bitmap.width):
                    if bitmap.length < length:  # if new width is bigger
                        bitmap.braceletKnots.append(bitmap.knotInfo(defaultColor))
                    else:  # if new width is smaller
                        bitmap.braceletKnots.pop()
            bitmap.length = length

    # display the current knotMap, or display the updated version if it has been modified
    knotCount = 0
    for yRow in range(bitmap.length):
        for xRow in range(bitmap.width):
            pg.draw.rect(screen, bitmap.braceletKnots[knotCount].color,
                         (xRow * spacing + x, yRow * spacing + y, size, size))
            knotCount = knotCount + 1

    # if the user wanted to modify the bitmap it is sent back to update the knotMap
    if create == True:
        return bitmap

# this function creates a surface to draw on and creates the pattern on to it before returning the surface
def visualPattern(surface, knotMap, y, saveImage=False):
    # initialize variables
    size = 18
    knotCount = 0
    enterStringOffset = 70

    gridMargin = 225

    # various variables to dynamically control the size and position of each shape
    spacing = (size * 3)
    gridWidth = knotMap.width * spacing + (knotMap.width - 1) + enterStringOffset
    txt = pg.font.Font(None, size)

    # internal class where the position of each of the most recently used colors are kept in a list
    class colorPoints:
        def __init__(self):
            self.braceletKnots = []

        class knotInfo:
            def __init__(self, color, x, y):
                self.color = color
                self.x = x
                self.y = y

    lineCords = colorPoints()

    # pattern surface is defined with the correct size and variables for arrow polygon are defined
    scrollWindow = pg.Surface((gridWidth + 35, y + knotMap.length * spacing + 100), pg.SRCALPHA)
    scrollWindow.fill((255, 255, 255))

    # info for dynamically loaded polygon arrow:
    w = size * 0.9  # total width
    h = size * 0.4  # total height

    head = w * 0.4
    body = w - head

    # this for loop runs through the pattern twice so the shapes are displayed correctly, not overlapping over each other.
    for run in range(0, 2):

        # for loop runs first down the length of the loop
        for yRow in range(knotMap.length):
            posY = y + yRow * spacing

            # the code goes in a zigzag code down the list, if the current value of yRow gives an integer when divided
            # then it will go to the right, if not the reverse
            if yRow % 2 == 0:
                x_range = range(knotMap.width)
                direction = True
                knotCount = knotCount - knotMap.width
            else:
                x_range = range(knotMap.width - 1, -1, -1)
                direction = False
                knotCount = knotCount + knotMap.width

            # for loop runs first down the length of the loop
            for xRow in x_range:
                posX = enterStringOffset + xRow * spacing
                knotCount = yRow * knotMap.width + xRow

                if run == 0:
                    dynamicSize = round(size * 0.5)

                    # if yRow is at the top, place lines to mark what to tie the strings to.
                    if yRow == 0:
                        # center empty rectangle through circles
                        pg.draw.rect(scrollWindow, (0, 0, 0),
                                     pg.Rect(posX - dynamicSize * -1.5 // 2,  posY - spacing * 0.8, dynamicSize * -1.5,
                                             knotMap.length * spacing + 30), 1, border_radius=15)

                        # draw gray line in between
                        pg.draw.rect(scrollWindow, (214, 214, 214),
                                     pg.Rect(posX - dynamicSize * -0.4 // 2, posY - spacing * 0.6, dynamicSize * -0.4,
                                             knotMap.length * spacing + 15), border_radius=15)

                    # display on both the right and left edge of the pattern which vertical row it is on
                    text = txt.render(str(yRow + 1), True, (128, 128, 128))
                    scrollWindow.blit(text, (posX + ((knotMap.width - 1 - xRow) * spacing) + 60,
                                             posY - size // 4))  # right side
                    scrollWindow.blit(text, ((posX - xRow * spacing) - 70, posY - size // 4))  # left side

                    # adding gray lines pointing to the position so it is clear, useful for the user to keep track of
                    # where they are, connected to the gray text above
                    if direction:  # ->
                        if xRow == knotMap.width - 1:
                            pg.draw.line(scrollWindow, (199, 199, 199), (posX, posY),
                                         (posX + ((knotMap.width - 1 - xRow) * spacing) + 50, posY), 1)
                        elif xRow == 0:
                            pg.draw.line(scrollWindow, (199, 199, 199), (posX, posY),
                                         ((posX - xRow * spacing) - 50, posY), 1)
                    else:  # <-
                        if xRow == 0:
                            pg.draw.line(scrollWindow, (199, 199, 199), (posX, posY),
                                         ((posX - xRow * spacing) - 50, posY), 1)
                        elif xRow == knotMap.width - 1:
                            pg.draw.line(scrollWindow, (199, 199, 199), (posX, posY),
                                         (posX + ((knotMap.width - 1 - xRow) * spacing) + 50, posY), 1)

                    # if the current knot is not the same color as the previous knot draw a line between with the
                    # previous knot's color anyway to show that the string continues
                    if knotMap.braceletKnots[knotCount].color != knotMap.braceletKnots[
                        knotCount - 1].color and xRow != 0:
                        pg.draw.line(scrollWindow, (0, 0, 0), (enterStringOffset + (xRow - 1) * spacing, posY + 1),
                                     (posX, posY + 1), dynamicSize + 4)
                        # use the color of the previous knot to create a line to the current one, depending on direction
                        if direction:  # ->
                            # use the color of the previous knot to create a line to the current one
                            pg.draw.line(scrollWindow, knotMap.braceletKnots[knotCount].color,
                                         (enterStringOffset + (xRow - 1) * spacing, posY), (posX, posY), dynamicSize)
                        else:
                            pg.draw.line(scrollWindow, knotMap.braceletKnots[knotCount - 1].color,
                                         (enterStringOffset + (xRow - 1) * spacing, posY), (posX, posY), dynamicSize)

                    # this while draws the lines between the knots that shows where the strings are supposed to go next
                    # by checking what the current knot color is, and looping through the lineCords list to check if an
                    # older one is there, if there is, a line that is created between the current and previous of the same color
                    lining = True
                    i = 0
                    while lining:

                        # if at the start or finish of the width draw a line and there is a new color is that horizontal
                        # row add a line going into the pattern to show that a new string is being added
                        if len(lineCords.braceletKnots) == 0 or i == len(lineCords.braceletKnots):
                            lineCords.braceletKnots.append(
                                lineCords.knotInfo(knotMap.braceletKnots[knotCount].color, posX, posY))

                            if direction == False:  # <-
                                pg.draw.rect(scrollWindow, (0, 0, 0),
                                             (min(posX, posX + ((knotMap.width - 1 - xRow) * spacing) + 50) + 1,
                                              (posY - dynamicSize // 2) - 1,
                                              abs(posX + ((knotMap.width - 1 - xRow) * spacing) + 50 - posX),
                                              dynamicSize + 2), border_radius=15)
                                pg.draw.rect(scrollWindow, lineCords.braceletKnots[i].color,
                                             (min(posX, posX + ((knotMap.width - 1 - xRow) * spacing) + 50),
                                              (posY - dynamicSize // 2),
                                              abs(posX + ((knotMap.width - 1 - xRow) * spacing) + 50 - posX),
                                              dynamicSize), border_radius=15)
                            else:
                                pg.draw.rect(scrollWindow, (0, 0, 0), (min(posX, posX - (xRow * spacing) - 50) - 1,
                                                                       (posY - dynamicSize // 2) - 1,
                                                                       abs((posX - (xRow * spacing) - 50) - posX),
                                                                       dynamicSize + 2), border_radius=15)
                                pg.draw.rect(scrollWindow, lineCords.braceletKnots[i].color,
                                             (min(posX, posX - (xRow * spacing) - 50), (posY - dynamicSize // 2),
                                              abs((posX - (xRow * spacing) - 50) - posX), dynamicSize),
                                             border_radius=15)
                            lining = False

                        # if the color in the lineCords list is not the same as the current knot color then check the
                        # next color in the lineCords list is not, else if it is found draw the line and update the
                        # color’s position in lineCords
                        elif lineCords.braceletKnots[i].color != knotMap.braceletKnots[knotCount].color:
                            i += 1
                        else:  # ->
                            pg.draw.line(scrollWindow, (0, 0, 0), (posX, posY + 1),
                                         (lineCords.braceletKnots[i].x, lineCords.braceletKnots[i].y + 1),
                                         dynamicSize + 4)
                            pg.draw.line(scrollWindow, lineCords.braceletKnots[i].color, (posX, posY),
                                         (lineCords.braceletKnots[i].x, lineCords.braceletKnots[i].y), dynamicSize)
                            lineCords.braceletKnots[i].x = posX
                            lineCords.braceletKnots[i].y = posY
                            lining = False
                # if it’s on the second loop, loop through knotMap again, adding circles with the color of the knots to
                # represent what to tie, as well as adding the arrow to show direction
                else:
                    gfx.filled_circle(scrollWindow, posX, posY, size + 2, (0, 0, 0))  # border
                    gfx.filled_circle(scrollWindow, posX, posY, size, knotMap.braceletKnots[knotCount].color)

                    left = posX - w / 2
                    right = posX + w / 2
                    top = posY - h / 2
                    bottom = posY + h / 2
                    mid = posY

                    # check which direction the row is going and add the arrow polygon inside the circle facing that direction
                    if direction:  # facing right ->
                        points = [
                            (left, posY - h * 0.25),
                            (left + body, posY - h * 0.25),
                            (left + body, top),
                            (right, mid),
                            (left + body, bottom),
                            (left + body, posY + h * 0.25),
                            (left, posY + h * 0.25),
                        ]

                    else:  # facing left <-
                        points = [
                            (right, posY - h * 0.25),
                            (right - body, posY - h * 0.25),
                            (right - body, top),
                            (left, mid),
                            (right - body, bottom),
                            (right - body, posY + h * 0.25),
                            (right, posY + h * 0.25),
                        ]

                    r, g, b = knotMap.braceletKnots[knotCount].color[:3]
                    if r // 2 <= 127 and g // 2 <= 127 and b // 2 <= 127:
                        inside = (255, 255, 255)
                        outside = (0, 0, 0)
                    else:
                        inside = (0, 0, 0)
                        outside = (255, 255, 255)

                    pg.draw.polygon(scrollWindow, inside, points)
                    # border
                    pg.draw.polygon(scrollWindow, outside, points, 1)

    # if the pattern is being created to save it externally return the scrollWindow in the original size (full resolution)
    # if not, check if the scrollWindow surface is bigger then the main screen, if so resize it so it's smaller
    if saveImage == True:
        return scrollWindow
    else:
        # if the width of the grid is closer than 112.5 pixels to the right hand edge of the screen
        # make the surface smaller so it takes up less space
        if knotMap.width * spacing > surface.get_width() - gridMargin:
            lengthScale = (knotMap.width * spacing) / (surface.get_width() - gridMargin)
            scrollWindow = pg.transform.smoothscale(scrollWindow,(surface.get_width() - gridMargin, (knotMap.length * spacing)/lengthScale+y))

            #add text to show that this is low resolution
            smallTxt = pg.font.Font(None, 20)
            text = smallTxt.render("Low resolution preview, save pattern to view fully", True, (0, 0, 0))
            scrollWindow.blit(text, (0, 0))
        # return the surface with the pattern on it and is total width
        return scrollWindow, scrollWindow.get_width()


def instructionScreen():
    pg.display.set_caption("Bracelet instructions")
    # initialize buttons and variables
    surface.fill((255, 255, 255))
    back = button(surface, 30, 50, 60, 30, "Back")
    save = button(surface, 30, 100, 60, 30, "Save")

    # this is where the pattern will appear on the screen
    scrollWindow, gridWidth = visualPattern(surface, knotMap, 100)

    # use the total width of the pattern in the center to put it in the middle of the screen
    x = (surface.get_width() - gridWidth) // 2

    yScroll = 0
    # once the pattern has been fully created this loop runs until the user presses the “back” button to return to the
    # first page, it checks where the mouse has been clicked, and moves the pattern as an image if the scroll wheel is moved
    while True:
        for event in pg.event.get():

            # end the program if the user closes the window
            if event.type == pg.QUIT:
                #pg.quit()
                sys.exit()

            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # left click

                    # exit the function and return to the main loop
                    if back.isPressed(event):
                        return
                    # if the save button is pressed check if this program is an exe file or running in an IDE, then
                    # creating a png of the pattern in scrollWindow in the same directory as the program.
                    if save.isPressed(event):
                        if getattr(sys, 'frozen', False):
                            application_path = os.path.dirname(sys.executable)
                        elif __file__:
                            application_path = os.path.dirname(__file__)

                        config_path = os.path.join(application_path, "bracelet.png")

                        # before saving the file, first check if a file with the same name already exists, if so, add a
                        # digit and check if that file also exists, it continues until an unused filename is found.
                        i = 0
                        while True:
                            if os.path.exists(config_path):
                                i = i + 1
                            else:
                                # this saves the high resolution grid
                                pg.image.save(visualPattern(surface, knotMap, 100, True), config_path)
                                break
                            config_path = os.path.join(application_path, "bracelet" + str(i) + ".png")

            # change vertical pattern location using the scroll wheel input, * 30.5 makes it more responsive
            elif event.type == pg.MOUSEWHEEL:
                pg.draw.rect(surface, (255, 255, 255),
                             (x, -yScroll, scrollWindow.get_width(), scrollWindow.get_height()))
                yScroll -= event.y * 30.5

        # display and update the pattern window for any position change
        surface.blit(scrollWindow, (x, 0), area=pg.Rect(0, yScroll, surface.get_width(), surface.get_height()))
        pg.display.flip()
        clock.tick(60)

def main(knotMap):
    pg.display.set_caption("Create bracelet pattern")
    # begin by initializing the structures, text boxes buttons and sliders
    largeTxt = pg.font.Font(None, 32)
    dynamicSettingsPos = surface.get_width()

    surface.fill((255, 255, 255))

    xStringInput = txtInputBox(surface, dynamicSettingsPos - 80, 200, 60, 30, "Strings")
    yStringInput = txtInputBox(surface, dynamicSettingsPos - 80, 250, 60, 30, "Length")
    # make the text boxes visible with the text label
    xStringInput.update()
    xStringInput.displayTxt()
    yStringInput.update()
    yStringInput.displayTxt()

    cp = ColorPicker(dynamicSettingsPos - 80, 450, 200, 40, surface, False)
    cpGreyscale = ColorPicker(dynamicSettingsPos - 40, 450, 200, 40, surface, True)
    cp.update()
    cpGreyscale.update()
    currentColor = cp.color

    editGridSize = 25
    gridMargin = 190
    editScreenSpacing = 25

    displayEditGrid = button(surface, dynamicSettingsPos - 80, 300, 60, 30, "Load")
    displayInstruction = button(surface, dynamicSettingsPos - 80, 100, 60, 30, "Apply")
    clearGrid = button(surface, dynamicSettingsPos - 80, 160, 60, 30, "Clear")
    hasCreatedBitmap = False
    firstGridUse = True

    yScroll = 0
    scrollWindow = pg.Surface((1, 1))
    # check if a pattern has already been created and if so displays it, useful when returning
    # from instructionsScreen
    if not knotMap is None:
        y = 100
        x = 2
        # if the width of the grid is closer than 95 pixels to the right hand edge of the screen
        # make the squares smaller so they take up less space
        if knotMap.width * editScreenSpacing > surface.get_width() - gridMargin:
            # calculate the max amount of knots by seeing how  many can fit in the width of the screen with a margin
            maxKnots = (surface.get_width() - gridMargin) // (editScreenSpacing)
            editGridSize = ((maxKnots * editGridSize + (maxKnots - 1)) - (knotMap.width - 1)) // knotMap.width

        gridWidth = knotMap.width * editGridSize + (knotMap.width - 1)
        scrollWindow = pg.Surface((gridWidth, y + knotMap.length * editScreenSpacing + 5))
        scrollWindow.fill((255, 255, 255))

        createBitmap(scrollWindow, x, y, editGridSize, knotMap, False)
        x = (surface.get_width() - gridWidth) // 2

        hasCreatedBitmap = True
        firstGridUse = False

    # keep the display updating until the program returns
    while True:
        for event in pg.event.get():

            #end the program if the user closes the window
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            # if the left click is being held down get mouse position and check if it is on a knot, updating it if so.
            if pg.mouse.get_pressed()[0]:

                # sets the current color to whichever color was selected last
                if cp.update() != None:
                    currentColor = cp.color
                elif cpGreyscale.update() != None:
                    currentColor = cpGreyscale.color
                if hasCreatedBitmap == True:
                    xScrollWindow, y = pg.mouse.get_pos()
                    editBitmap(scrollWindow, (xScrollWindow - x, y + yScroll), knotMap, editGridSize, currentColor)

                # if the left click is click check if the mouse is over any buttons
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # left click
                    # if an integer value is entered into “Strings” and “Length” and the “Load” button
                    # is pressed create and display a new grid
                    if xStringInput.txt.isdigit() and yStringInput.txt.isdigit() and displayEditGrid.isPressed(event):
                        if not int(xStringInput.txt) < 1 and not int(yStringInput.txt) < 1:
                            x = 2
                            y = 100
                            editGridSize = 25

                            if firstGridUse == False:  # removes previous grid by setting scrollWindow to white
                                scrollWindow.fill((255, 255, 255))
                                x = (surface.get_width() - gridWidth) // 2
                                surface.blit(scrollWindow, (x, 0),
                                             area=pg.Rect(0, yScroll, surface.get_width(), surface.get_height()))
                                x = 2


                            # if the width of the grid is closer than 95 pixels to the right hand edge of the screen
                            # make the squares smaller so they take up less space
                            if int(xStringInput.txt) * editScreenSpacing > surface.get_width() - gridMargin:
                                # calculate the max amount of knots by seeing how  many can fit in the width of the screen with a margin
                                maxKnots = (surface.get_width() - gridMargin) // (editScreenSpacing)
                                editGridSize = ((maxKnots * editGridSize + (maxKnots - 1)) - (int(xStringInput.txt) - 1)) // int(xStringInput.txt)

                            if not editGridSize < 1:
                                # center, save, and display the new grid
                                gridWidth = int(xStringInput.txt) * editGridSize + (int(xStringInput.txt) - 1)
                                scrollWindow = pg.Surface((gridWidth, y + int(yStringInput.txt) * editScreenSpacing+5))
                                scrollWindow.fill((255, 255, 255))
                                knotMap = createBitmap(scrollWindow, x, y, editGridSize, knotMap, defaultColor, True,
                                                       int(xStringInput.txt), int(yStringInput.txt))
                                x = (surface.get_width() - gridWidth) // 2
                                firstGridUse = False

                            # if the grid is 1 or less or the grid is too big, display a warning
                            if not knotMap is None and knotMap.width <= 1:
                                text = largeTxt.render("Pattern too small", True, (255, 0, 0))
                                surface.blit(text, (surface.get_width() // 2 + 20, 20))
                            elif editGridSize < 1:
                                text = largeTxt.render("Pattern too big", True, (255, 0, 0))
                                surface.blit(text, (surface.get_width() // 2 + 20, 20))
                            else:
                                pg.draw.rect(surface, (255, 255, 255), (surface.get_width() // 2 + 20, 20, 200, 25))

                            pg.display.flip()


                            hasCreatedBitmap = True


                    # if “Apply” has been pressed return, the master loop will open instructionScreen() (second screen)
                    if displayInstruction.isPressed(event) and hasCreatedBitmap:
                        if not knotMap.width <= 1:
                            return knotMap

                    # if there is already a grid loop through the color and set everything to gray
                    if clearGrid.isPressed(event) and hasCreatedBitmap:
                        y = 100
                        x = 2
                        knotMap = createBitmap(scrollWindow, x, y, editGridSize, knotMap, defaultColor, True, knotMap.width, knotMap.length)
                        x = (surface.get_width() - gridWidth) // 2

                # if the mouse is right-clicked set the currentColor to whatever the color is at the position of the
                # mouse and the RGB color picker's circle is updated to show that. (Basically copy-paste)
                elif event.button == 3:  # right click
                    currentColor = surface.get_at(pg.mouse.get_pos())
                    cp.color = currentColor
                    cp.update()

            # if the scroll wheel moves then redraw scrollWindow and that y position
            elif event.type == pg.MOUSEWHEEL and hasCreatedBitmap:
                pg.draw.rect(surface, (255, 255, 255), (x, -yScroll, scrollWindow.get_width(), scrollWindow.get_height()))
                yScroll -= event.y * 30.5

            xStringInput.event(event)
            xStringInput.update()
            xStringInput.displayTxt()
            yStringInput.event(event)
            yStringInput.update()
            yStringInput.displayTxt()


        # if grid pattern exists update the screen with it
        if not knotMap is None:
            surface.blit(scrollWindow, (x, 0), area=pg.Rect(0, yScroll, surface.get_width(), surface.get_height()))

        pg.display.flip()
        clock.tick(60)

# keep the program looping infinitely until the user closes it.
while True:
    knotMap = main(knotMap)
    instructionScreen()