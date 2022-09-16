import pygame as pg
from pygame.locals import *
import pgkinter as pgk
import os
import shutil
import time
from win32api import GetSystemMetrics

from datetime import datetime

from ctypes import windll

SetWindowPos = windll.user32.SetWindowPos

pgkRoot = pgk.Pgk()

# noinspection SpellCheckingInspection
NOSIZE = 1
# noinspection SpellCheckingInspection
NOMOVE = 2
TOPMOST = -1
NOT_TOPMOST = -2

updateDropdown = False


def alwaysOnTop(yesOrNo):
    zOrder = (NOT_TOPMOST, TOPMOST)[yesOrNo]  # choose a flag according to bool
    hwnd = pg.display.get_wm_info()['window']  # handle to the window
    SetWindowPos(hwnd, zOrder, 0, 0, 0, 0, NOMOVE | NOSIZE)


SCREEN_WIDTH_MINIMISED = 100
SCREEN_HEIGHT_MINIMISED = 25

SCREEN_WIDTH_EXPANDED = int(GetSystemMetrics(0) / 2)
if SCREEN_WIDTH_EXPANDED < 800:
    SCREEN_WIDTH_EXPANDED = 800
elif SCREEN_WIDTH_EXPANDED > 1500:
    SCREEN_WIDTH_EXPANDED = 1500

SCREEN_HEIGHT_EXPANDED = 200
wScale = SCREEN_WIDTH_EXPANDED / 1035
BG_COLOUR = (255, 255, 255)

BACKUP_FOLDER = "File Manager Backups"


def copyFile(path, filename, extension, newName=None, backup=True):
    global updateDropdown
    for widget in pgkRoot.getWidgets():
        if widget.getPos() == (int(5 * wScale), 175):
            widget.delete()

    currentTime = datetime.now()
    timestamp = currentTime.strftime("%Y-%m-%d T-%H%M%S")
    if newName is None:
        newName = filename + " - " + timestamp

    source = path + "\\" + filename + extension

    destination = path + "\\" + BACKUP_FOLDER + "\\" + newName + extension

    if not backup:
        shutil.copy(source, path + "\\" + filename + "_old" + extension)
        source, destination = destination, source

    try:
        shutil.copy(source, destination)
        pgk.Label(pgkRoot, screen, topleft=(int(5 * wScale), 175),
                  font=("Helvetica", 18),
                  text=f'Backup successfully {"made" if backup else "restored"}.'
                       f' Timestamp: {timestamp}')
    except (UnicodeEncodeError, OSError):
        pgk.Label(pgkRoot, screen, topleft=(int(5 * wScale), 175),
                  font=("Helvetica", int(18 * wScale)),
                  text="Invalid characters detected in file name. Try again.")

    updateDropdown = True

    return

def returnAction():
    global screen
    global expandTo
    global autoBackup
    expandTo = fileSelect
    autoBackup = False
    fileSelect()


def fileManagement(inputList=None):
    global screen
    global restoreBackupSelect
    global autoBackupDelay
    global autoCheck
    global autoTimer
    global frameTimer
    global previousFrame
    global autoBackup
    global filePath
    global fileName
    global fileExt
    global expandTo
    global updateDropdown

    for widget in pgkRoot.getWidgets():
        if widget.getPos == (0, 0):
            widget.delete()

    if expandTo != fileManagement:
        filePath = inputList[0].get()
        numLetters = 0
        for i in inputList[1].get()[::-1]:
            numLetters += 1
            if i == ".":
                fileExt = inputList[1].get()[::-1][:numLetters][::-1]
                fileName = inputList[1].get()[:len(inputList[1].get()) - \
                                               numLetters]

        try:
            if not os.path.isfile(filePath + "\\" + fileName + fileExt):
                for widget in pgkRoot.getWidgets():
                    if widget.getPos() == (int(5 * wScale), 130):
                        widget.delete()
                pgk.Label(pgkRoot, screen, topleft=(int(5 * wScale), 130),
                          font=("Helvetica", int(18 * wScale)),
                          text="Invalid file path/name! Please try again.")
                return
        except UnboundLocalError:
            for widget in pgkRoot.getWidgets():
                if widget.getPos() == (int(5 * wScale), 130):
                    widget.delete()
            pgk.Label(pgkRoot, screen, topleft=(int(5 * wScale), 130),
                      font=("Helvetica", int(18 * wScale)),
                      text="Invalid file path/name! Please try again.")
            return

        autoBackup = False
        autoTimer = 0
        frameTimer = 0
        previousFrame = time.time()

        # Create backup directory if one doesn't exist
        if not os.path.exists(filePath + "\\" + BACKUP_FOLDER):
            os.mkdir(filePath + "\\" + BACKUP_FOLDER)

        for widget in pgkRoot.getWidgets():
            widget.delete()

        pgk.Label(pgkRoot, screen, topleft=(int(210 * wScale), 0),
                  font=("Helvetica", int(12 * wScale)),
                  text="Selected File: " + filePath + "\\" + fileName + fileExt)

        pgk.Label(pgkRoot, screen, topright=(int(205 * wScale), 50),
                  font=("Helvetica", int(18 * wScale)),
                  text="Enter backup file name:",
                  textalignment="right")

        pgk.Label(pgkRoot, screen, topleft=(int(628 * wScale), 50),
                  font=("Helvetica", int(18 * wScale)),
                  text=fileExt)

        pgk.Label(pgkRoot, screen, topright=(int(210 * wScale), 130),
                  font=("Helvetica", int(18 * wScale)),
                  text="AutoBackup Delay (seconds): ",
                  textalignment="right")

        backupName = pgk.InputBox(pgkRoot, screen, int(210 * wScale), 50,
                                  font=("Helvetica", int(18 * wScale)),
                                  bgColour=(222, 222, 222), width=int(416 *
                                                                      wScale))

        create = pgk.Button(pgkRoot, screen, int(210 * wScale), 90,
                            font=("Helvetica", int(18 * wScale)),
                            bgColour=(33, 33, 33), text="Create Backup",
                            action=lambda: copyFile(filePath, fileName, fileExt,
                                                    newName=backupName.get()))

        autoBackupDelay = pgk.InputBox(pgkRoot, screen, int(210 * wScale), 130,
                                       font=("Helvetica", int(18 * wScale)),
                                       bgColour=(222, 222, 222),
                                       width=create.getWidth(),
                                       allowLetters=False, allowSpecial=False,
                                       allowSpace=False, charLimit=6)

        autoCheck = pgk.Checkbox(pgkRoot, screen, int(500 * wScale), 130,
                                 font=("Helvetica", int(18 * wScale)),
                                 bgColour=(222, 222, 222),
                                 inlineText="Activate AutoBackup:",
                                 height=backupName.getHeight())

        pgk.Button(pgkRoot, screen, SCREEN_WIDTH_EXPANDED - SCREEN_WIDTH_MINIMISED * 2,
                   0, bgColour=(33, 33, 33),
                   font=("Helvetica", int(18 * wScale)),
                   height=SCREEN_HEIGHT_MINIMISED,
                   width=SCREEN_WIDTH_MINIMISED * 2,
                   text="Select Another File", action=returnAction)

        existingBackupsList = [i.replace(fileExt, "") for i in os.listdir(filePath + "\\" + BACKUP_FOLDER) if i.endswith(fileExt)]

        if len(existingBackupsList) == 0:
            existingBackupsList = [""]

        restoreBackupSelect = pgk.Dropdown(pgkRoot, screen, int(700 * wScale),
                                           70, existingBackupsList,
                                           width=(int(300 * wScale)),
                                           bgColour=(222, 222, 222),
                                           font=("Helvetica", int(18 * wScale)))

        pgk.Button(pgkRoot, screen, int(700 * wScale), 30,
                   width=(int(200 * wScale)),
                   font=("Helvetica", int(18 * wScale)),
                   bgColour=(33, 33, 33), text="Restore Backup (select below)",
                   action=lambda: copyFile(filePath, fileName, fileExt,
                                           newName=restoreBackupSelect.get(),
                                           backup=False))



    pgk.Button(pgkRoot, screen, 0, 0, bgColour=(33, 33, 33), font=("Helvetica", 18),
               height=SCREEN_HEIGHT_MINIMISED, width=SCREEN_WIDTH_MINIMISED,
               text="Minimise", action=minimised)

    expandTo = fileManagement
    running = True
    while running:
        for event in pg.event.get():
            pgkRoot.eventHandler(event)

            if event.type == QUIT:
                running = False
                pg.quit()
                quit()

        frameTimer += time.time() - previousFrame
        previousFrame = time.time()

        if autoBackup:
            if autoTimer == 0:
                if autoBackupDelay.get() == "" or int(autoBackupDelay.get()) < \
                        30:
                    for widget in pgkRoot.getWidgets():
                        if widget.getPos() == (int(5 * wScale), 175):
                            widget.delete()
                    pgk.Label(pgkRoot, screen, topleft=(int(5 * wScale), 175),
                              font=("Helvetica", int(18 * wScale)),
                              text="Minimum time for auto delay is 30 seconds! "
                                   "Please try again.")
                    autoCheck.click()

                else:
                    frameTimer = 0
                    autoTimer = int(autoBackupDelay.get())
                    previousFrame = time.time()
                    copyFile(filePath, fileName, fileExt)

            elif frameTimer >= autoTimer:
                frameTimer = 0
                previousFrame = time.time()
                copyFile(filePath, fileName, fileExt)

        else:
            autoTimer = 0

        if updateDropdown:

            existingBackupsList = [i.replace(fileExt, "") for i in os.listdir(filePath + "\\" + BACKUP_FOLDER) if i.endswith(fileExt)]

            if len(existingBackupsList) == 0:
                existingBackupsList = [""]

            restoreBackupSelect.config(options=existingBackupsList)

            updateDropdown = False

        autoBackup = autoCheck.get()

        alwaysOnTop(True)

        screen.fill(BG_COLOUR)

        pgkRoot.update()

        pg.display.update()

        clock.tick()


def fileSelect():
    global screen
    running = True
    for widget in pgkRoot.getWidgets():
        widget.delete()

    pgk.Label(pgkRoot, screen, topright=(int(157 * wScale), 30),
              font=("Helvetica", int(18 * wScale)),
              text="Enter containing folder: ",
              textalignment="right")

    pgk.Label(pgkRoot, screen, topright=(int(157 * wScale), 80),
              font=("Helvetica", int(18 * wScale)),
              text="Enter file name: ",
              textalignment="right")

    inputList = [
        pgk.InputBox(pgkRoot, screen, int(157 * wScale), 30,
                     font=("Helvetica", int(18 * wScale)),
                     bgColour=(222, 222, 222),
                     width=int(842 * wScale)),
        pgk.InputBox(pgkRoot, screen, int(157 * wScale), 80,
                     font=("Helvetica", int(18 * wScale)),
                     bgColour=(222, 222, 222),
                     width=int(416 * wScale))
    ]

    pgk.Button(pgkRoot, screen, int(583 * wScale), 80, font=("Helvetica", int(18 *
                                                                     wScale)),
               bgColour=(33, 33, 33), text="Select File",
               height=inputList[1].getHeight(), width=int(416 * wScale),
               action=lambda: fileManagement(inputList=inputList))

    pgk.Button(pgkRoot, screen, 0, 0, bgColour=(33, 33, 33), font=("Helvetica", 18),
               height=SCREEN_HEIGHT_MINIMISED, width=SCREEN_WIDTH_MINIMISED,
               text="Minimise", action=minimised)

    while running:
        for event in pg.event.get():
            pgkRoot.eventHandler(event)

            if event.type == QUIT:
                running = False
                pg.quit()
                quit()

        alwaysOnTop(True)

        screen.fill(BG_COLOUR)

        pgkRoot.update()

        pg.display.update()

        clock.tick()


def expandHandle():
    global screen
    global expandTo
    for widget in pgkRoot.getWidgets():
        if widget.getPos() == (0, 0):
            widget.delete()

    screen = pg.display.set_mode((SCREEN_WIDTH_EXPANDED,
                                  SCREEN_HEIGHT_EXPANDED))

    expandTo()


# noinspection PyUnboundLocalVariable
def minimised():
    global screen
    global autoTimer
    global frameTimer
    global previousFrame
    global autoBackup
    global filePath
    global fileName
    global fileExt

    for widget in pgkRoot.getWidgets():
        if widget.getPos() == (0, 0):
            widget.delete()

    screen = pg.display.set_mode((SCREEN_WIDTH_MINIMISED,
                                  SCREEN_HEIGHT_MINIMISED))

    running = True

    pgk.Button(pgkRoot, screen, 0, 0, bgColour=(33, 33, 33),
               font=("Helvetica", 18), height=SCREEN_HEIGHT_MINIMISED,
               width=SCREEN_WIDTH_MINIMISED, text="Expand",
               action=expandHandle)

    while running:
        for event in pg.event.get():
            pgkRoot.eventHandler(event)

            if event.type == QUIT:
                running = False
                pg.quit()
                quit()

        frameTimer += time.time() - previousFrame
        previousFrame = time.time()

        if autoBackup:
            if frameTimer >= autoTimer:
                frameTimer = 0
                previousFrame = time.time()
                copyFile(filePath, fileName, fileExt)

        alwaysOnTop(True)

        screen.fill(BG_COLOUR)

        pgkRoot.update()

        pg.display.update()

        clock.tick()


if __name__ == "__main__":  # If program is run as a script, this will run
    pg.init()
    pg.font.init()
    screen = pg.display.set_mode((SCREEN_WIDTH_MINIMISED,
                                  SCREEN_HEIGHT_MINIMISED))
    # noinspection SpellCheckingInspection
    pg.display.set_caption('JS File Backup Utility V1.0.0')
    icon = pg.image.load("resources\\icons\\ICO32.png")
    pg.display.set_icon(icon)
    clock = pg.time.Clock()
    autoTimer = 0
    frameTimer = 0
    previousFrame = time.time()
    autoBackup = False
    filePath = ""
    fileName = ""
    fileExt = ""
    expandTo = fileSelect
    minimised()
