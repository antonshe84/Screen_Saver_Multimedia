import os
import random
import threading

import pyautogui
import cv2
import numpy

from mypack import *

path_win = [".\settings.ini", f"{os.path.expandvars('%TEMP%')}\\ScreenMultimedia\\settings.ini",
            f"{os.path.expandvars('%APPDATA%')}\\ScreenMultimedia\\settings.ini"]
path_lin = ['./settings.ini', '/etc/ScreenMultimedia/settings.ini', '$HOME/.config/settings.ini']

pictures_suffixes = ('.jpg', '.jpeg', '.tif', '.tiff', '.bmp')  # '.png'
videos_suffixes = ('.mp4', '.avi', '.mpg', '.mpeg', '.mov', '.vob', '.wmv', '.mkv')  # '.gif', '.GIF'
event_flag = 2  # 0 - рабочий режим, 1 - завершение программы, 2 - подготовка на старте
multimedia_files = []
video_files = []
pictures_files = []
list_of_previous = []


# Функция поиска файлов c расширениями suffixes в списке каталогов roots
def files_of_dir(files_suffixes, directory, show_random):
    """  Search function for files with suffixes in the list of root directories

    :return: list of multimedia_files.
    multimedia_files is global because the search takes place in a separate stream
    and you need to access it in the search process.
    Еhe list of directories is taken from the parameter file

    """
    global multimedia_files, pictures_files, video_files
    global event_flag
    t1 = Timer()
    print(f'Поиск мультимедиа файлов запущен!')
    event_flag = 0
    dirs = directory.copy()
    if show_random:
        random.shuffle(dirs)
    for root in dirs:
        if os.path.exists(root):
            rr = os.walk(root)
            for path_n, subdir_n, files_n in rr:
                if event_flag == 1:
                    return 0
                for name in files_n:
                    d = os.path.join(path_n, name)
                    if d.lower().endswith(files_suffixes):
                        multimedia_files.append(d)
                        if d.lower().endswith(videos_suffixes):
                            video_files.append(d)
                        elif d.lower().endswith(pictures_suffixes):
                            pictures_files.append(d)
        else:
            continue

    size_m, size_v, size_i = 0, 0, 0
    for e in multimedia_files:
        size_m += e.__sizeof__()
    for e in pictures_files:
        size_i += e.__sizeof__()
    for e in video_files:
        size_v += e.__sizeof__()

    print(f'Поиск мультимедиа файлов окончен! Прошло: {t1.end_time()}')
    print('Мультимедиа файлов найдено:', len(multimedia_files),
          ', Изображений из них:', len(pictures_files),
          ', Видео из них:', len(video_files), '\n')
    print(f'Занимаемый объем памяти: m {size_m}, i {size_i}, v {size_v}\n')


def main_init():
    se = {"path_settings": os.path.abspath(f'{os.getcwd()}\settings.ini'),
          'os_name': os.name,
          'window_name': 'Screensaver Multimedia'}
    if se['os_name'] == 'nt':
        paths = path_win
    else:
        paths = path_lin
    for path in paths:
        try:
            path = os.path.abspath(path)
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            os.chdir(os.path.dirname(path))
            se["path_settings"] = path
            break
        except OSError:
            print('OSError: Каталог не создан')
            continue
    # se["os_name"] = 'posix'
    # my_logger = get_logger("loo", f'{os.path.dirname(se["path_settings"])}\\mylog.log')
    # my_logger.setLevel(logging.DEBUG)

    # my_logger.info(f'  OS: {se["os_name"]}.  Work path: {os.path.dirname(se["path_settings"])}')
    print(f'  OS: {se["os_name"]}.  Work path: {os.path.dirname(se["path_settings"])}\n')

    if se["os_name"] == 'nt':
        sett = RegSettings(r'Software\Screensaver Multimedia\Settings')
        se['play_video_or_image'] = sett.get_reg_int('play_video_or_image', '0')
        se['sec_play_img'] = sett.get_reg_int('sec_play_img', '5')
        se['sec_play_vid'] = sett.get_reg_int('sec_play_vid', '60')
        se['type_background'] = sett.get_reg_int('type_background', '0')
        se['mouse_move_end'] = sett.get_reg_int('mouse_move_end', '1')
        se['show_info'] = sett.get_reg_int('show_info', '1')
        se['show_random'] = sett.get_reg_int('show_random', '1')
        se['show_random_video'] = sett.get_reg_int('show_random_video', '1')
        se['color_background'] = sett.get_reg('color_background', '#000000')
        se['color_info'] = sett.get_reg('color_info', '#FFFF00')
    else:
        sett = IniSettings(se["path_settings"], 'Settings')
        se['play_video_or_image'] = sett.get_ini_int('play_video_or_image', '0')
        se['sec_play_img'] = sett.get_ini_int('sec_play_img', '5')
        se['sec_play_vid'] = sett.get_ini_int('sec_play_vid', '60')
        se['type_background'] = sett.get_ini_int('type_background', '0')
        se['mouse_move_end'] = sett.get_ini_int('mouse_move_end', '1')
        se['show_info'] = sett.get_ini_int('show_info', '1')
        se['show_random'] = sett.get_ini_int('show_random', '1')
        se['show_random_video'] = sett.get_ini_int('show_random_video', '1')
        se['color_background'] = sett.get_ini('color_background', '#000000')
        se['color_info'] = sett.get_ini('color_info', '#FFFF00')

    # Приведение переменных к диапозонам
    if se['play_video_or_image'] > 3: se['play_video_or_image'] = 3
    if se['play_video_or_image'] < 0: se['play_video_or_image'] = 0
    if se['type_background'] > 3: se['type_background'] = 3
    if se['type_background'] < 0: se['type_background'] = 0
    if se['sec_play_img'] > 9999: se['sec_play_img'] = 9999
    if se['sec_play_img'] < 1: se['sec_play_img'] = 1
    if se['sec_play_vid'] > 9999: se['sec_play_vid'] = 9999
    if se['sec_play_vid'] < 0: se['sec_play_vid'] = 0
    if se['mouse_move_end'] > 1: se['mouse_move_end'] = 1
    if se['mouse_move_end'] < 0: se['mouse_move_end'] = 0
    if se['show_info'] > 1: se['show_info'] = 1
    if se['show_info'] < 0: se['show_info'] = 0
    se['show_info_and_s'] = se['show_info'] + 0b10000000
    if se['show_random'] > 1: se['show_random'] = 1
    if se['show_random'] < 0: se['show_random'] = 0
    if se['show_random_video'] > 1: se['show_random_video'] = 1
    if se['show_random_video'] < 0: se['show_random_video'] = 0

    if se['play_video_or_image'] == 1:
        se['files_suffixes'] = pictures_suffixes
    elif se['play_video_or_image'] == 2:
        se['files_suffixes'] = videos_suffixes
    else:
        se['files_suffixes'] = pictures_suffixes + videos_suffixes
    directory = []
    for d in range(1, 10):
        if se["os_name"] == 'nt':
            sett = RegSettings(r'Software\Screensaver Multimedia\Settings')
            search_folder = sett.get_reg(f'directory{str(d)}', None)
        else:
            sett = IniSettings(se["path_settings"], 'Settings')
            search_folder = sett.get_ini(f'directory{str(d)}', None)
        if search_folder is None:  # or not os.path.exists(search_folder):
            continue
        else:
            directory.append(search_folder)

    if not directory:
        if se["os_name"] == 'nt' and os.path.exists(f"{os.path.expandvars('%USERPROFILE%')}\\Pictures"):
            directory.append(f"{os.path.expandvars('%USERPROFILE%')}\\Pictures")
        else:
            directory.append(os.getcwd())
    se['directory'] = directory
    # my_logger.info(f'Каталоги мультимедиа файлов: {directory}')
    print(f'Каталоги мультимедиа файлов: {directory}\n')

    se['w_screen'], se['h_screen'] = pyautogui.size()
    se['background'] = cv2.cvtColor(numpy.array(numpy.zeros((se['h_screen'], se['w_screen'], 3),
                                                            dtype='uint8')), cv2.COLOR_RGB2BGR)

    color_background = (0, 0, 0)
    try:
        col = se['color_background']
        R_col = int(f"0x{col[1:3]}", base=16)
        G_col = int(f"0x{col[3:5]}", base=16)
        B_col = int(f"0x{col[5:7]}", base=16)
    except ValueError:
        se['color_background'] = '#000000'
        R_col, G_col, B_col = 0, 0, 0
    if se['type_background'] == 0:
        color_background = (0, 0, 0)
    elif se['type_background'] == 1:
        color_background = (255, 255, 255)
    elif se['type_background'] == 2:
        color_background = (150, 150, 150)
    elif se['type_background'] == 3:
        color_background = (B_col, G_col, R_col)
    else:
        print(f"EXCEPTION!: Parameter 'type_background' out of range")

    se['background'][::] = color_background

    arg = sys.argv
    if se["os_name"] == 'nt':
        sett = RegSettings(r'Software\Screensaver Multimedia\Settings')
        for d in range(1, 10):
            sett.del_reg(f'arg{str(d)}')
        i = 0
        for d in arg:
            sett.set_reg(f'arg{str(i)}', d)
            i += 1

    if len(arg) > 1:
        # аргумент '/p' - предпросмотр
        if arg[1].lower().startswith('/p'):
            print('Preview start')
            sys.exit()
        # аргумент '/c' - параметры
        elif arg[1].lower().startswith('/c'):
            print('Settings start')
            se_GUI.main(se)
            sys.exit()
        # аргумент '/s' - запуск основной программы
        elif arg[1].lower().startswith('/s'):
            print('Main program start')
            scr_file = True

    return se


def main():
    global multimedia_files, pictures_files, video_files
    global event_flag
    print('==========Start!==========')
    play_end, errors_count, next_image_file, next_video_file, current_file_index = 0, 0, 0, 0, 0
    exception = ''
    s = main_init()

    thread1 = threading.Thread(target=files_of_dir, args=[s['files_suffixes'], s['directory'], s['show_random']])
    thread1.start()
    time.sleep(0.1)

    cv2.namedWindow(s['window_name'], cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(s['window_name'], cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    # cv2.imshow(s['window_name'], s['background'])

    while True:
        if not (len(multimedia_files) == 0):
            t2 = Timer()
            if play_end == 8 and len(list_of_previous) > 1:
                current_file = list_of_previous[len(list_of_previous) - 2]
                del (list_of_previous[len(list_of_previous) - 1])
            else:
                if s['show_random']:
                    current_file = random.choice(multimedia_files)
                    if next_video_file and len(video_files):
                        current_file = random.choice(video_files)
                    if next_image_file and len(pictures_files):
                        current_file = random.choice(pictures_files)
                else:
                    current_file_index += 1
                    if current_file_index > len(multimedia_files) - 1:
                        current_file_index = 0
                    current_file = multimedia_files[current_file_index]
                if s['play_video_or_image'] == 3:
                    next_video_file = not next_video_file
                    next_image_file = not next_video_file
                else:
                    next_image_file, next_video_file = 0, 0
                list_of_previous.append(current_file)
            s['current_file'] = current_file
            print(current_file)
            if current_file.lower().endswith(videos_suffixes):
                vid = VideoFile(s)
                play_end, exception = vid.play()
                del vid
            elif current_file.lower().endswith(pictures_suffixes):
                img = ImageFile(s)
                play_end, exception = img.play()
                del img
            else:
                play_end, exception = 1, 'Not a media file'
            print(t2.end_time(), end=' ')
        else:
            s['current_file'] = '0'
            s_play_temp = s['sec_play_img']
            s['sec_play_img'] = 0.9
            img = ImageFile(s)
            play_end, exception = img.play()
            del img
            s['sec_play_img'] = s_play_temp
        s['show_info_and_s'] = s['show_info']
        if play_end == 3:
            continue
        if play_end == 13:
            print("Enter pressed. Play OK!")
        elif play_end == 27:
            print("Keyboard exit. See you!")
            print(f"Errors: {errors_count}")
            break
        elif play_end == 0:
            print("Play OK!")
        elif play_end == 2:
            print("End of video. Play OK!")
        elif play_end == 1:
            errors_count += 1
            del (multimedia_files[current_file_index])
            del (list_of_previous[len(list_of_previous) - 1])
            print("File not available!")
            print(f"EXCEPTION!: {exception}")
        elif play_end == 8:
            print("Previous file!")
        elif play_end == 73:
            print("Next image file pressed. Play OK!")
            next_image_file, next_video_file = 1, 0
        elif play_end == 86:
            print("Next video file pressed. Play OK!")
            next_image_file, next_video_file = 0, 1
        elif play_end == 83:
            print(f"Errors: {errors_count}")
            print("Opening settings")
            print('==========Stop!==========')
            cv2.destroyAllWindows()
            event_flag = 1
            se_GUI.main(s)

            break

        print('\n', end='')

    cv2.destroyAllWindows()
    event_flag = 1
    print('==========Стоп!==========')
    return 0


if __name__ == '__main__':
    main()

# cx_Freeze:
# setup.py build
# setup.py bdist_msi

# python -m py_compile main.py
# python -m compileall
