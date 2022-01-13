import sys

import cv2
import numpy

from mypack.translit import *
from mypack.timer import *


class MultiFile:
    def __init__(self, kwargs):
        self.f_name = kwargs['current_file']
        self.f_name_translit = transliterate(self.f_name)
        self.background = kwargs['background'].copy()
        self.color_info = kwargs['color_info']
        try:
            col = kwargs['color_info']
            R_col = int(f"0x{col[1:3]}", base=16)
            G_col = int(f"0x{col[3:5]}", base=16)
            B_col = int(f"0x{col[5:7]}", base=16)
        except ValueError:
            R_col, G_col, B_col = 255, 255, 0
        self.color_info = (B_col, G_col, R_col)

        self.mouse_move_end = kwargs['mouse_move_end']
        self.window_name = kwargs['window_name']
        self.show_info = kwargs['show_info_and_s']
        self.w_screen = kwargs['w_screen']
        self.h_screen = kwargs['h_screen']
        self.show_random_video = kwargs['show_random_video']
        self.event_mouse = 0
        self.ix, self.iy = 0, 0
        self.start_flag = 0
        # self.image_total = self.background.copy()

    def date_time_convert(self, date_time, time_zone):
        import datetime
        import pytz
        import os
        if date_time:
            if time_zone > 0:
                time_zone_str = 'Etc/GMT-' + str(abs(time_zone))
            else:
                time_zone_str = 'Etc/GMT+' + str(abs(time_zone))
            local = pytz.timezone(time_zone_str)
            if date_time.startswith('UTC'):
                date_time = date_time[4::]
            naive = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
            local_dt = local.localize(naive, is_dst=None)
            utc_dt = local_dt.astimezone(pytz.utc)
            utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
            return utc_dt
        else:
            return datetime.datetime.fromtimestamp(int(os.path.getmtime(self.f_name)))

    def rotate_frame(self, image, angle, center=None, scale=1.0):
        (h, w) = image.shape[:2]
        if abs(angle) == 90 or abs(angle) == 270:
            source = (h, w)
        else:
            source = (w, h)
        if w > h:
            t = w
        else:
            t = h
        rotated = cv2.resize(image, (t, t))
        if center is None:
            center = (t / 2, t / 2)

        # Perform the rotation
        m = cv2.getRotationMatrix2D(center, angle, scale)
        rotated = cv2.warpAffine(rotated, m, (t, t))
        rotated = cv2.resize(rotated, source)
        return rotated

    def fit_to_background(self, image_to_fit):
        # from screeninfo import get_monitors
        # m = get_monitors()
        w_image = image_to_fit.shape[1]  # Ширина картинки
        h_image = image_to_fit.shape[0]  # Высота картинки

        final_width = self.w_screen
        r = float(final_width) / w_image  # соотношение ширины картинок
        final_height = int(h_image * r)
        if final_height >= self.h_screen:
            final_height = self.h_screen
            r = float(final_height) / h_image  # соотношение высоты картинок
            final_width = int(w_image * r)

        # уменьшаем изображение до подготовленных размеров
        if (len(image_to_fit.shape) < 3):
            image_to_fit = cv2.cvtColor(numpy.array(image_to_fit), cv2.COLOR_BGRA2BGR)
        elif not (image_to_fit.shape[2] == 3):
            image_to_fit = cv2.cvtColor(numpy.array(image_to_fit), cv2.COLOR_BGRA2BGR)
        return cv2.resize(image_to_fit, (final_width, final_height))

    def image_to_image(self, image_on_top):
        w_image = image_on_top.shape[1]  # Ширина картинки
        h_image = image_on_top.shape[0]  # Высота картинки

        w_center = int(self.w_screen / 2 - w_image / 2)
        h_center = int(self.h_screen / 2 - h_image / 2)
        image_total = self.background[:]
        image_total[h_center:(h_center + h_image), w_center:(w_center + w_image)] = image_on_top[:]
        return image_total

    def insert_text(self, image_for_text, text, pos):
        return cv2.putText(image_for_text, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.color_info, 2)

    def key_event(self, keys):
        if keys & 0xFF != 0xFF:
            print(f"'{keys}' key pressed")
        if keys & 0x7F == 27:  # Нажата клавиша 'Esc' завершения работы программы
            return 27
        elif keys & 0x7F == 13 or keys & 0x7F == 32:  # Нажата клавиша 'Enter' или 'Пробел' воспроизвести следующий файл
            return 13
        elif keys & 0x7F == 8:  # Нажата клавиша 'Backspace' вернуться к предыдущему файлу
            return 8
        elif keys & 0x7F == 73 or keys & 0x7F == 105 \
                or keys == 216 or keys == 248:  # Нажата клавиша 'i' воспроизвести следующим файл изображения
            return 73
        elif keys & 0x7F == 86 or keys & 0x7F == 118 \
                or keys == 204 or keys == 236:  # Нажата клавиша 'v' воспроизвести следующим файл видео
            return 86
        elif keys & 0x7F == 83 or keys & 0x7F == 115 \
                or keys == 219 or keys == 251:  # Нажата клавиша 's' открыть окно настроек
            return 83
        elif keys & 0xFF != 0xFF and self.mouse_move_end:   # Нажата любая другая клавиша
            return 27
        return None

    def mouse_event(self, event, x, y, flags, param):
        # print(f'Движ мыши: {x}, {y}')
        if self.start_flag == 0:
            self.ix = x
            self.iy = y
            self.start_flag = 1
        elif (abs(x - self.ix) > 4) or (abs(y - self.iy) > 4) \
                or event == cv2.EVENT_LBUTTONDOWN or event == cv2.EVENT_RBUTTONDOWN:
            self.event_mouse = 27





class VideoFile(MultiFile):
    def __init__(self, kwargs):
        self.s_play = kwargs['sec_play_vid']
        MultiFile.__init__(self, kwargs)
        self.media_info = self.GetMediaInfo()

    def GetMediaInfo(self):
        if 'posix' in sys.builtin_module_names:
            pass
        if 'nt' in sys.builtin_module_names:
            from pymediainfo import MediaInfo
            import MediaInfo as mi
            import exifread

        media_info = {}
        try:
            info = mi.MediaInfo(filename=self.f_name)
            infoData = info.getInfo()
            media_data = MediaInfo.parse(self.f_name)
            time_zone = int(time.timezone / 3600)
            if media_data.tracks[1].encoded_date:
                media_info['date_time'] = self.date_time_convert(media_data.tracks[1].encoded_date, time_zone)
            else:
                media_info['date_time'] = self.date_time_convert(None, time_zone)
            if media_data.tracks[1].duration:
                media_info['duration'] = float(media_data.tracks[1].duration / 1000)
            else:
                media_info['duration'] = 0
            if media_data.tracks[1].frame_rate:
                media_info['frame_rate'] = float(media_data.tracks[1].frame_rate)
            else:
                media_info['frame_rate'] = 30
            if media_data.tracks[1].rotation:
                media_info['rotation'] = float(media_data.tracks[1].rotation)
            else:
                media_info['rotation'] = 0
            media_info['exception'] = None
            return media_info
        except Exception as exc:
            media_info['date_time'] = '0000-00-00 00:00:00'
            media_info['duration'] = 0
            media_info['frame_rate'] = 30
            media_info['rotation'] = 0
            media_info['exception'] = exc
            return media_info




    def play(self):
        # if self.media_info['exception']:
        #     return 1, self.media_info['exception']
        import random
        high_processor_load = 0
        t_v = Timer()
        try:
            cap = cv2.VideoCapture(self.f_name)

            self.media_info['frame_rate'] = cap.get(cv2.CAP_PROP_FPS)
            frame_count_video = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            self.media_info['duration'] = round(frame_count_video/self.media_info['frame_rate'], 3)

            if (self.media_info['duration'] - self.s_play) > 0 and self.show_random_video:
                self.rand_msec = random.randint(0, int(1000*(self.media_info['duration'] - self.s_play)))
                flag1 = cap.set(cv2.CAP_PROP_POS_MSEC, self.rand_msec)
                text_for_show = f'{str(self.media_info["date_time"])}   ' \
                                f'{str(round(self.media_info["duration"], 1))}s  ' \
                                f'Play with {str(round(self.rand_msec / 1000, 1))}s'
            else:
                self.rand_msec = 0
                text_for_show = f'{str(self.media_info["date_time"])}   ' \
                                f'{str(round(self.media_info["duration"], 1))}s  '

            # flag = cap.set(cv2.CAP_PROP_POS_FRAMES, 60)
            flag2 = cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            if self.mouse_move_end:
                cv2.setMouseCallback(self.window_name, self.mouse_event)

            while True:
                t_f = Timer()
                if high_processor_load > 0:
                    ret = cap.grab()
                    # if high_processor_load == 2:
                    #     ret = cap.grab()
                    # pos = cap.get(cv2.CAP_PROP_POS_FRAMES)
                    # ret = cap.set(cv2.CAP_PROP_POS_FRAMES, pos + 1)
                    # pos = cap.get(cv2.CAP_PROP_POS_FRAMES)
                    # ret, frame = cap.read()
                ret, frame = cap.read()
                if not ret:
                    return 2, ''
                if self.media_info['rotation']:
                    frame = self.rotate_frame(frame, int(-self.media_info['rotation']))
                frame = self.fit_to_background(frame)
                frame = self.image_to_image(frame)
                if self.show_info & 0x80 >= 128:
                    frame = self.insert_text(frame, "Press 'S' to open settings, 'Esc' to exit",
                                             (30, self.h_screen - 150))
                if self.show_info & 0x7F:
                    frame = self.insert_text(frame, self.f_name_translit, (30, self.h_screen - 50))
                    frame = self.insert_text(frame, text_for_show, (30, self.h_screen - 100))
                cv2.imshow(self.window_name, frame)

                frame_wait_ms = int(1000 * (1 / self.media_info['frame_rate'] * (1 + high_processor_load) - t_f.end_time()))
                if frame_wait_ms < 1:
                    # if high_processor_load == 1:
                    #     high_processor_load = 2
                    if high_processor_load == 0:
                        high_processor_load = 1
                    frame_wait_ms = 1
                keys = cv2.waitKey(frame_wait_ms)
                if keys != -1:
                    event = self.key_event(keys)
                else:
                    event = 0
                if self.event_mouse:
                    event = self.event_mouse
                if event:
                    return event, ''
                elif self.s_play == 0:
                    pass
                elif (t_v.elapsed_time()) >= self.s_play:
                    return 0, ''
        except Exception as exc:
            return 1, exc


class ImageFile(MultiFile):

    def __init__(self, kwargs):
        self.s_play = kwargs['sec_play_img']
        MultiFile.__init__(self, kwargs)
        if not (self.f_name == '0'):
            self.media_info = self.GetExif()
        else:
            self.media_info = {}
            self.media_info['date_time'] = '0000-00-00 00:00:00'
            self.media_info['rotation'] = 0
            self.media_info['exception'] = ''

    def GetExif(self):
        import exifread
        import datetime
        import os
        media_info = {}
        try:
            if self.f_name.lower().endswith(('.jpg', '.jpeg', '.tif', '.tiff')):
                f = open(self.f_name, 'rb')
                tags = exifread.process_file(f)
                f.close()
            else:
                tags = 0

            date_time = datetime.datetime.fromtimestamp(int(os.path.getmtime(self.f_name)))
            rotation = 0
            if tags:
                if 'Image Orientation' in tags:
                    orientation = tags['Image Orientation'].values[0]
                else:
                    orientation = 0

                if orientation == 3:
                    rotation = 180
                elif orientation == 6:
                    rotation = -90
                elif orientation == 8:
                    rotation = 90
                else:
                    rotation = 0

                if 'Image DateTime' in tags:
                    date_time = tags['Image DateTime'].values
                    date_s, time_s = date_time.split(' ')
                    date_s = '-'.join(date_s.split(':'))
                    date_time = ' '.join([date_s, time_s])

            media_info['date_time'] = date_time
            media_info['rotation'] = rotation
            media_info['exception'] = ''
            return media_info

        except Exception as exc:
            media_info['date_time'] = '0000-00-00 00:00:00'
            media_info['rotation'] = 0
            media_info['exception'] = exc
            return media_info


    def play(self):
        import datetime
        t_i = Timer()
        try:
            if not (self.f_name == '0'):
                if self.media_info['exception']:
                    return 1, self.media_info['exception']
                image = cv2.imdecode(numpy.fromfile(self.f_name, dtype=numpy.uint8), cv2.IMREAD_UNCHANGED)

                if self.media_info['rotation']:
                    image = self.rotate_frame(image, self.media_info['rotation'])
                image = self.fit_to_background(image)
                image = self.image_to_image(image)
                if self.show_info & 0x80 >= 128:
                    image = self.insert_text(image, "Press 'S' to open settings, 'Esc' to exit",
                                             (30, self.h_screen - 150))
                if self.show_info & 0x7F:
                    image = self.insert_text(image, self.f_name_translit, (30, self.h_screen - 50))
                    image = self.insert_text(image, str(self.media_info['date_time']), (30, self.h_screen - 100))

            else:
                image = self.background
                if self.show_info & 0x80 >= 128:
                    image = self.insert_text(image, "Press 'S' to open settings, 'Esc' to exit",
                                             (30, self.h_screen - 150))
                image = self.insert_text(image, 'No media files found!',
                                         (int(self.w_screen / 2 - 100), int(self.h_screen / 2)))
                image = self.insert_text(image, str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")),
                                         (int(self.w_screen / 2 - 100), int(self.h_screen / 2) + 100))
            cv2.imshow(self.window_name, image)
        except Exception as exc:
            return 1, exc
        if self.mouse_move_end:
            cv2.setMouseCallback(self.window_name, self.mouse_event)
        while True:
            keys = cv2.waitKey(50)
            if keys != -1:
                event = self.key_event(keys)
            else:
                event = 0
            if self.event_mouse:
                event = self.event_mouse
            if event:
                return event, ''
            elif self.f_name == '0' and t_i.elapsed_time() >= self.s_play:
                return 3, ''
            if t_i.elapsed_time() >= self.s_play:
                return 0, ''

