from mypack.settings import *
from mypack.mylogger import *
from tkinter import *
from tkinter import filedialog, colorchooser
from tkinter.ttk import Combobox, Checkbutton

font_text = ("DejaVu Sans Mono", 10)


class MySettings(Frame):

    def __init__(self, parent, settings):
        Frame.__init__(self, parent)
        self.parent = parent
        self.s = settings
        self.path_settings = self.s['path_settings']
        self.os_name = self.s['os_name']
        self.init_ui()
        self.read_param()

    def init_ui(self):
        self.parent.title("Настройки")

        self.pack(fill=BOTH, expand=1)
        self.var = BooleanVar()

        self.lbl1 = Label(self.parent, text="Каталоги для отображения фалов:", font=font_text)
        self.lbl1.place(x=20, y=10)
        self.lbl10 = Label(self.parent, text="Случайный порядок отображения:", font=font_text)
        self.lbl10.place(x=20, y=130)
        self.lbl2 = Label(self.parent, text="Время отображения изобр.:", font=font_text)
        self.lbl2.place(x=20, y=155)
        self.lbl3 = Label(self.parent, text="Время отобр. видео (0 - всё):", font=font_text)
        self.lbl3.place(x=20, y=180)
        self.lbl3 = Label(self.parent, text="           Случайное время видео:", font=font_text)
        self.lbl3.place(x=20, y=205)
        self.lbl4 = Label(self.parent, text="Что отображать:", font=font_text)
        self.lbl4.place(x=20, y=235)
        self.lbl5 = Label(self.parent, text="Цвет фона:", font=font_text)
        self.lbl5.place(x=20, y=260)
        self.lbl6 = Label(self.parent, text="Выход по мыши и клавиатуре:", font=font_text)
        self.lbl6.place(x=20, y=285)
        self.lbl7 = Label(self.parent, text="Показывать инфо.    (цвет:    )", font=font_text)
        self.lbl7.place(x=20, y=310)
        self.lbl8 = Label(self.parent, text="Команды клавиатуры:", font=font_text)
        self.lbl8.place(x=20, y=340)
        self.lbl9 = Label(self.parent,
                          text="'Enter', 'Пробел' следующий файл \n"
                               "'Backspace' - предыдущий файл    \n"
                               "'Esc' - выход                    \n"
                               "'S' - открыть настройки          \n"
                               "'I' - отобразить следующим изобр.\n"
                               "'V' - отобразить следующим видео ",
                          font=font_text)
        self.lbl9.place(x=20, y=360)

        self.checkMouseMove = IntVar()
        self.chk1 = Checkbutton(self.parent, var=self.checkMouseMove)
        self.checkMouseMove.set(1)
        self.chk1.place(x=280, y=285)

        self.checkInfo = IntVar()
        self.chk2 = Checkbutton(self.parent, var=self.checkInfo)
        self.checkInfo.set(1)
        self.chk2.place(x=280, y=310)

        self.checkRandom = IntVar()
        self.chk3 = Checkbutton(self.parent, var=self.checkRandom)
        self.checkRandom.set(1)
        self.chk3.place(x=280, y=130)

        self.comboBackground = Combobox(self.parent)
        self.comboBackground.configure(values=('Черный фон', 'Белый фон', 'Серый фон', 'Свой цвет...'))
        self.comboBackground.current(1)
        self.comboBackground.bind("<<ComboboxSelected>>", self.ChooseColorBG)
        self.comboBackground.place(x=155, y=260)

        self.comboVideoOrImage = Combobox(self.parent)
        self.comboVideoOrImage.configure(values=('Изображения и видео', 'Только изображения',
                                                 'Только видео', 'Чередовать видео и изобр.'))
        self.comboVideoOrImage.current(1)
        self.comboVideoOrImage.place(x=155, y=235)

        self.spinTimeImage = IntVar()
        self.spinTimeImage.set(5)
        self.spin1 = Spinbox(self.parent, from_=1, to=9999, width=4, textvariable=self.spinTimeImage)
        self.spin1.place(x=260, y=155)

        self.spinTimeVideo = IntVar()
        self.spinTimeVideo.set(5)
        self.spin2 = Spinbox(self.parent, from_=0, to=9999, width=4, textvariable=self.spinTimeVideo)
        self.spin2.place(x=260, y=180)

        self.checkRandomVideo = IntVar()
        self.chk4 = Checkbutton(self.parent, var=self.checkRandomVideo)
        self.checkRandomVideo.set(1)
        self.chk4.place(x=280, y=205)

        self.frame = Frame(self.parent)
        self.frame.place(x=20, y=30, width=280, height=100)

        self.listDirs = Listbox(self.frame, width=33, height=5, font=font_text)

        self.scrollvert = Scrollbar(self.frame, orient="vertical")
        self.scrollvert.config(command=self.listDirs.yview)
        self.scrollvert.pack(side="right", fill="y")

        self.scrollhoriz = Scrollbar(self.frame, orient="horizontal")
        self.scrollhoriz.config(command=self.listDirs.xview)
        self.scrollhoriz.pack(side="bottom", fill="x")

        self.listDirs.pack(side="top")
        self.listDirs.config(xscrollcommand=self.scrollhoriz.set, yscrollcommand=self.scrollvert.set)

        self.btnAddDir = Button(self.parent, text="Добавить", width=10, command=self.btnAddDirClicked)
        self.btnAddDir.place(x=310, y=30, width=80, height=30)

        self.btnDelDir = Button(self.parent, text="Удалить", width=10, command=self.btnDelDirClicked)
        self.btnDelDir.place(x=310, y=70, width=80, height=30)

        pixel = PhotoImage(width=1, height=1)
        # Button(text="...", image=pixel, width=30, height=10, compound="c")

        self.btnOK = Button(self.parent, text="ОК", width=10, height=3, command=self.pushOKClicked)
        self.btnOK.focus_set()
        self.btnOK.place(x=310, y=330, width=80, height=60)

        self.btnCancel = Button(self.parent, text="Отмена", width=10, height=3, command=self.pushCancelClicked)
        self.btnCancel.place(x=310, y=400, width=80, height=60)

        self.btnColorBG = Button(self.parent, width=2, height=1, command=self.ChooseColorBG_click)
        self.btnColorBG.place(x=125, y=257, width=25, height=25)

        self.btnColorInfo = Button(self.parent, width=2, height=1, command=self.ChooseColorInfo)
        self.btnColorInfo.place(x=235, y=305, width=25, height=25)

    def read_param(self):
        self.comboVideoOrImage.current(int(self.s['play_video_or_image']))
        self.spinTimeImage.set(int(self.s['sec_play_img']))
        self.spinTimeVideo.set(int(self.s['sec_play_vid']))
        self.comboBackground.current(int(self.s['type_background']))
        if self.s['type_background'] == 0:
            self.btnColorBG.configure(bg='#000000')
        elif self.s['type_background'] == 1:
            self.btnColorBG.configure(bg='#FFFFFF')
        elif self.s['type_background'] == 2:
            self.btnColorBG.configure(bg='#808080')
        elif self.s['type_background'] == 3:
            try:
                self.btnColorBG.configure(bg=self.s['color_background'][0:7])
            except Exception as exc:
                print(f"EXCEPTION!: {exc}, set color - black (#000000)")
                self.s['color_background'] = '#000000'
                self.btnColorBG.configure(bg=self.s['color_background'])
        else:
            print(f"EXCEPTION!: Parameter 'type_background' out of range")

        try:
            self.btnColorInfo.configure(bg=self.s['color_info'][0:7])
        except Exception as exc:
            print(f"EXCEPTION!: {exc}, set color - yellow (#FFFF00)")
            self.s['color_info'] = '#FFFF00'
            self.btnColorInfo.configure(bg=self.s['color_info'])


        self.checkMouseMove.set(int(self.s['mouse_move_end']))
        self.checkInfo.set(int(self.s['show_info']))
        self.checkRandom.set(int(self.s['show_random']))
        self.checkRandomVideo.set(int(self.s['show_random_video']))
        self.listDirs.delete(0, self.listDirs.size())

        for dir_cur in self.s['directory']:
            self.listDirs.insert(self.listDirs.size(), dir_cur)

    def write_param(self):
        if self.s['os_name'] == 'nt':
            self.sett = RegSettings(r'Software\Screensaver Multimedia\Settings')
            for d in range(1, 10):
                self.sett.del_reg(f'directory{str(d)}')
            for d in range(self.listDirs.size()):
                self.sett.set_reg(f'directory{str(d + 1)}', self.listDirs.get(d))
            self.sett.set_reg('play_video_or_image', str(self.comboVideoOrImage.current()))
            self.sett.set_reg('type_background', str(self.comboBackground.current()))
            self.sett.set_reg('sec_play_img', str(self.spinTimeImage.get()))
            self.sett.set_reg('sec_play_vid', str(self.spinTimeVideo.get()))
            self.sett.set_reg('mouse_move_end', str(self.checkMouseMove.get()))
            self.sett.set_reg('show_info', str(self.checkInfo.get()))
            self.sett.set_reg('show_random', str(self.checkRandom.get()))
            self.sett.set_reg('show_random_video', str(self.checkRandomVideo.get()))
            self.sett.set_reg('color_background', self.s['color_background'])
            self.sett.set_reg('color_info', self.s['color_info'])
        else:
            self.sett = IniSettings(self.path_settings, 'Settings')
            for d in range(1, 10):
                self.sett.del_ini(f'directory{str(d)}')
            for d in range(self.listDirs.size()):
                self.sett.set_ini(f'directory{str(d + 1)}', self.listDirs.get(d))
            self.sett.set_ini('play_video_or_image', str(self.comboVideoOrImage.current()))
            self.sett.set_ini('type_background', str(self.comboBackground.current()))
            self.sett.set_ini('sec_play_img', str(self.spinTimeImage.get()))
            self.sett.set_ini('sec_play_vid', str(self.spinTimeVideo.get()))
            self.sett.set_ini('mouse_move_end', str(self.checkMouseMove.get()))
            self.sett.set_ini('show_info', str(self.checkInfo.get()))
            self.sett.set_ini('show_random', str(self.checkRandom.get()))
            self.sett.set_ini('show_random_video', str(self.checkRandomVideo.get()))
            self.sett.set_ini('color_background', self.s['color_background'])
            self.sett.set_ini('color_info', self.s['color_info'])

    def btnAddDirClicked(self):
        if self.listDirs.size() < 9:
            self.dir_name = filedialog.askdirectory(title='Выберите каталог', initialdir=os.curdir)
        else:
            self.dir_name = ''
        if self.dir_name != '':
            self.dir_name = os.path.abspath(self.dir_name)
            self.list_len = self.listDirs.size()
            # self.listDirs.insert(self.list_len, self.dir_name)
            self.listDirs.insert(END, self.dir_name)
            print(f'Directory added: {self.dir_name}')

    def btnDelDirClicked(self):
        self.cur_sel = self.listDirs.curselection()
        if self.cur_sel:
            self.listDirs.delete(self.cur_sel)
        pass

    def pushOKClicked(self):
        self.write_param()
        print("Settings saved")
        sys.exit()

    def pushCancelClicked(self):
        print("Cancel")
        sys.exit()

    def ChooseColorInfo(self):
        (rgb, hx) = colorchooser.askcolor(self.s['color_info'][0:7])
        if hx is None:
            hx = self.s['color_info'][0:7]
        self.s['color_info'] = hx
        self.btnColorInfo.configure(bg=hx)

    def ChooseColorBG(self, event):
        if self.comboBackground.current() == 0:
            self.btnColorBG.configure(bg='#000000')
        elif self.comboBackground.current() == 1:
            self.btnColorBG.configure(bg='#FFFFFF')
        elif self.comboBackground.current() == 2:
            self.btnColorBG.configure(bg='#808080')
        elif self.comboBackground.current() == 3:
            (rgb, hx) = colorchooser.askcolor(self.s['color_background'][0:7])
            if hx is None:
                hx = self.s['color_background'][0:7]

            self.s['color_background'] = hx
            self.btnColorBG.configure(bg=hx)
        else:
            print(f"EXCEPTION!: Parameter 'type_background' out of range")

    def ChooseColorBG_click(self):
        self.ChooseColorBG(0)

def exitKey(event):
    # print(event.keycode)
    if event.keycode == 27:
        print(event.keycode)
        sys.exit()


def exitMouse(event):
    # print(event.num)
    if event.num == 2:
        print(event.num)
        sys.exit()


def main(settings):
    # my_logger = get_logger("loo", f'{os.path.dirname(settings["path_settings"])}\\mylog.log')
    # my_logger.setLevel(logging.DEBUG)
    # my_logger.info('Окно настроек запущено')
    root = Tk()
    root.geometry('410x480+{}+{}'.format(settings['w_screen'] // 2 - 205, settings['h_screen'] // 2 - 240))
    # root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
    # root.attributes("-fullscreen", True)
    root.resizable(False, False)
    root.bind('<Key>', exitKey)
    root.bind('<Button>', exitMouse)
    root.bind('<Button-2>', lambda press: sys.exit())
    window = MySettings(root, settings)

    window.mainloop()
