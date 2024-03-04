# folder_setup.py

import os


def setup_folders(IMAGES_PATH, LABELIMG_PATH, champion_names_no_1):
    if not os.path.exists(IMAGES_PATH):
        if os.name == "posix":
            os.system("mkdir -p %s" % IMAGES_PATH)
        if os.name == "nt":
            os.system("mkdir %s" % IMAGES_PATH)
    for champion_name in champion_names_no_1:
        CHAMPION_PATH = os.path.join(IMAGES_PATH, champion_name)
        if not os.path.exists(CHAMPION_PATH):
            if os.name == "posix":
                os.system("mkdir -p %s" % CHAMPION_PATH)
            if os.name == "nt":
                os.system("mkdir %s" % CHAMPION_PATH)
        champion_screen_name = champion_name + "_screen"
        CHAMPION_screen_PATH = os.path.join(IMAGES_PATH, champion_screen_name)
        if not os.path.exists(CHAMPION_screen_PATH):
            if os.name == "posix":
                os.system("mkdir -p %s" % CHAMPION_screen_PATH)
            if os.name == "nt":
                os.system("mkdir %s" % CHAMPION_screen_PATH)
    if not os.path.exists(LABELIMG_PATH):
        if os.name == "posix":
            os.system("mkdir -p %s" % LABELIMG_PATH)
        if os.name == "nt":
            os.system("mkdir %s" % LABELIMG_PATH)
    for champion_name in champion_names_no_1:
        champ_screen = champion_name + "_screen"
        LABEL_CHAMPION_PATH = os.path.join(LABELIMG_PATH, champ_screen)
        if not os.path.exists(LABEL_CHAMPION_PATH):
            if os.name == "posix":
                os.system("mkdir -p %s" % LABEL_CHAMPION_PATH)
            if os.name == "nt":
                os.system("mkdir %s" % LABEL_CHAMPION_PATH)
