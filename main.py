import binascii
import threading
import numpy as np
from PIL import Image
import os
import math
import customtkinter as tk
import tkinter.filedialog as tf
import tkinter.messagebox as tm


def read_and_print_hex(file_path):
    with open(file_path, 'rb') as file:
        binary_data = file.read()
        hex_data = binascii.hexlify(binary_data).decode('ascii')
        return hex_data


def hex_string_to_binary_file(hex_string, file_path):
    binary_data = bytes.fromhex(hex_string)
    with open(file_path, 'wb') as file:
        file.write(binary_data)


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return (int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16))


def get_dimensions(num_points):
    for h in range(math.isqrt(num_points), 0, -1):
        w = math.ceil(num_points / h)
        if w * (h - 1) < num_points:
            return w, h
    return None, None


def rgb_to_hex(rgb_color):
    return '{:02x}{:02x}{:02x}'.format(rgb_color[0], rgb_color[1], rgb_color[2])


arr = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'] * 6
arr_index = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']


def print_img_with_hex(file_path, in_f, key, labels: (tk.CTkLabel,), pro: tk.CTkProgressBar):
    """
    file_path: 输出到
    in_f: 输入文件
    """
    name = os.path.basename(in_f)
    file_hex = read_and_print_hex(in_f)
    color_len = len(file_hex) // 6 + 1
    width, height = get_dimensions(color_len)
    image = np.zeros((height, width, 3), dtype=np.uint8)
    lens = 0
    key_index = 0
    zero_have = 0
    for x in range(height):
        for y in range(width):
            if len(file_hex[lens:lens + 6]) != 6:
                file_hex += '0' * (6 - len(file_hex[lens:lens + 6]))
                zero_have = 6 - len(file_hex[lens:lens + 6])
            if file_hex[lens:lens + 6]:
                map_list = list(file_hex[lens:lens + 6])
                for i in range(len(map_list)):
                    map_list[i] = str(map_list[i])
                    map_list[i] = arr[
                        arr_index.index(map_list[i]) + ord(key[key_index]) % 30]  # 模的是30！！！
                image[x, y, :] = hex_to_rgb(''.join(map_list))
                lens += 6
                key_index += 1
                key_index = key_index % len(key)
            else:
                break
    file_path += str(zero_have) + ";" + name + '.png'
    image = Image.fromarray(image, 'RGB')
    image.save(file_path)
    pro.configure(mode='determinate')
    pro['maximum'] = 1000
    pro['value'] = 100
    pro.set(100)
    pro.stop()
    for label in labels:
        label.configure(text='已完成')
        label.update()


def jieme(path, out_path, key, labels: (tk.CTkLabel,), pro: tk.CTkProgressBar):
    img = Image.open(path)
    img = np.array(img)
    file_hex = ''
    for x in range(img.shape[0]):
        for y in range(img.shape[1]):
            file_hex += rgb_to_hex(img[x, y, :])

    content = ''
    key_index = 0
    for i in range(0, len(file_hex), 6):
        text_list = list(file_hex[i:i + 6])
        for j in range(len(text_list)):
            text_list[j] = str(text_list[j])
            text_list[j] = arr[
                arr_index.index(text_list[j]) + 32 - ord(key[key_index]) % 30]  # 模的是30！！！
        content += ''.join(text_list)
        key_index += 1
        key_index = key_index % len(key)
    content = content.rstrip('0') + '0' * int(os.path.basename(path).split(';')[0])
    hex_string_to_binary_file(content, out_path + ''.join(os.path.basename(path).split(';')[1:])[:-4])
    pro.configure(mode='determinate')
    pro['maximum'] = 1000
    pro['value'] = 100
    pro.set(100)
    pro.stop()
    for label in labels:
        label.configure(text='已完成')
        label.update()


class OneJiaMiGUI:
    def __init__(self, root, path, key, jiamipath):
        self.root = root
        self.frame = tk.CTkFrame(root, corner_radius=10, fg_color="#2B2B2C")
        self.path = path
        self.base = key
        self.jiamipath = jiamipath + '/' + os.path.basename(self.path)
        self.file_info = os.stat(self.path)
        self.name = os.path.basename(self.path)
        if len(self.name) >= 10:
            self.name = self.name[:7] + '...'
        self.frame2 = tk.CTkFrame(self.frame)
        self.frame2.grid(row=0, column=0, padx=3, pady=3)
        self.label = tk.CTkLabel(self.frame2, text=self.name, font=("黑体", 50))
        self.label.pack(padx=3, pady=3)
        self.label2 = tk.CTkLabel(self.frame2,
                                  text=f'文件大小：{self.file_info.st_size / 1024 / 1024:.2f}MB，'
                                       f'文件类型:{os.path.basename(self.path).split(".")[-1]}',
                                  font=("黑体", 10), text_color='grey')
        self.label2.pack(padx=3, pady=3)
        self.label3 = tk.CTkLabel(self.frame, text=f'加密到：{self.jiamipath}', wraplength=350, font=("黑体", 15),
                                  text_color='grey')
        self.label3.grid(row=0, column=1, padx=3, pady=3)
        self.frame3 = tk.CTkFrame(self.frame)
        self.label4 = tk.CTkLabel(self.frame3, text='加密中', font=("黑体", 15))
        self.label4.pack(padx=3, pady=3)
        self.progressbar = tk.CTkProgressBar(self.frame3, mode='indeterminate', width=300)
        self.progressbar.pack(side=tk.TOP, padx=3, pady=3)
        self.progressbar.start()
        self.frame3.grid(row=0, column=2, padx=3, pady=3)

    def start(self):
        try:
            os.mkdir(self.jiamipath)
        except FileExistsError:
            pass
        threading.Thread(
            target=lambda: print_img_with_hex(self.jiamipath + '/', self.path, self.base, (self.label, self.label4),
                                              self.progressbar)).start()

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def place(self, **kwargs):
        self.frame.place(**kwargs)


class AddAJiaMi:
    def __init__(self, root):
        self._root = root
        self.root = tk.CTkToplevel()
        self.root.title("添加加密")
        self.frame = tk.CTkFrame(self.root, corner_radius=10, fg_color="#2B2B2C")
        self.frame_a = tk.CTkFrame(self.frame, corner_radius=10, fg_color="#2B2B2C")
        self.input_yuan_score = tk.StringVar()
        self.label1 = tk.CTkLabel(self.frame_a, text='源文件:', font=("黑体", 20))
        self.input_yuan = tk.CTkEntry(self.frame_a, font=("黑体", 20), width=200,
                                      textvariable=self.input_yuan_score)
        self.input_blowse_btn = tk.CTkButton(self.frame_a, text='浏览', font=("黑体", 20), width=0,
                                             command=self.select_file)
        self.label1.pack(side=tk.LEFT, padx=3, pady=3)
        self.input_yuan.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=3, pady=3)
        self.input_blowse_btn.pack(side=tk.LEFT, padx=3, pady=3)
        self.frame_a.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.frame_b = tk.CTkFrame(self.frame, corner_radius=10, fg_color="#2B2B2C")
        self.label2 = tk.CTkLabel(self.frame_b, text='储存到:', font=("黑体", 20))
        self.input_jiami_score = tk.StringVar()
        self.input_jiami = tk.CTkEntry(self.frame_b, font=("黑体", 20), width=200,
                                       textvariable=self.input_jiami_score)
        self.input_b_btn2 = tk.CTkButton(self.frame_b, text='浏览', font=("黑体", 20), width=0,
                                         command=self.select_save_where)
        self.label2.pack(side=tk.LEFT, padx=3, pady=3)
        self.input_jiami.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=3, pady=3)
        self.input_b_btn2.pack(side=tk.LEFT, padx=3, pady=3)
        self.frame_b.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.key_var = tk.BooleanVar()
        self.key_var.set(True)
        self.select = tk.CTkRadioButton(self.frame, text='加密方式：使用秘钥', font=("黑体", 20), value=True,
                                        variable=self.key_var)
        self.select.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.frame2 = tk.CTkFrame(self.frame, corner_radius=10, fg_color="#2B2B2C")
        self.label3 = tk.CTkLabel(self.frame2, text='秘钥:', font=("黑体", 20))
        self.key = tk.StringVar()
        self.input_key_show = tk.CTkEntry(self.frame2, font=("黑体", 20), show='·',
                                          textvariable=self.key)
        self.label3.pack(side=tk.LEFT, padx=3, pady=3)
        self.input_key_show.pack(side=tk.LEFT, padx=3, pady=3, fill=tk.BOTH, expand=True, )
        self.frame2.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.startBtn = tk.CTkButton(self.root, text='现在加密!', font=("黑体", 90), command=self.jiami)
        self.startBtn.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.root.resizable(False, False)

    def jiami(self):
        yuan = self.input_yuan_score.get()
        input_jiami_score = self.input_jiami_score.get()
        if yuan and input_jiami_score:
            base = self.key.get()
            if base:
                new_dl = OneJiaMiGUI(self._root, yuan, base, input_jiami_score)
                new_dl.pack(padx=10, pady=10, side=tk.BOTTOM)
                new_dl.start()
                self.root.destroy()
        else:
            tm.showerror("错误", "您只有填写完所有信息之后，才能进行加密！")

    def select_file(self):
        name = tf.askopenfilename(
            title='选择加密文件',
            filetypes=[('所有文件', '*.*')],
        )
        if name:
            self.input_yuan_score.set(name)

    def select_save_where(self):
        out_dir = tf.askdirectory(
            title='选择保存位置',
        )
        if out_dir:
            self.input_jiami_score.set(out_dir)

    def mainloop(self):
        self.root.mainloop()


class OneJieMiGUI:
    def __init__(self, root, path, jiemipath, key, fg="green"):
        self.root = root
        self.frame = tk.CTkFrame(root, corner_radius=10, fg_color="#2B2B2C")
        self.path = path
        self.jiemipath = jiemipath + '/'
        self.file_info = os.stat(self.path)
        self.name = os.path.basename(self.path)
        if len(self.name) >= 10:
            self.name = self.name[:7] + '...'
        self.frame2 = tk.CTkFrame(self.frame)
        self.frame2.grid(row=0, column=0, padx=3, pady=3)
        self.label = tk.CTkLabel(self.frame2, text=self.name, font=("黑体", 50), text_color=fg)
        self.label.pack(padx=3, pady=3)
        self.label2 = tk.CTkLabel(self.frame2,
                                  text=f'文件大小：{self.file_info.st_size / 1024 / 1024:.2f}MB，'
                                       f'文件类型:{os.path.basename(self.path).split(".")[-1]}',
                                  font=("黑体", 10), text_color='grey')
        self.label2.pack(padx=3, pady=3)
        self.label3 = tk.CTkLabel(self.frame, text=f'解密到：{self.jiemipath}', wraplength=350, font=("黑体", 15),
                                  text_color='grey')
        self.label3.grid(row=0, column=1, padx=3, pady=3)
        self.frame3 = tk.CTkFrame(self.frame)
        self.label4 = tk.CTkLabel(self.frame3, text='解密中', font=("黑体", 15), text_color=fg)
        self.label4.pack(padx=3, pady=3)
        self.progressbar = tk.CTkProgressBar(self.frame3, mode='indeterminate', width=300, progress_color=fg)
        self.progressbar.pack(side=tk.TOP, padx=3, pady=3)
        self.progressbar.start()
        self.frame3.grid(row=0, column=2, padx=3, pady=3)
        self.key = key

    def start(self):
        try:
            os.mkdir(self.jiemipath)
        except (FileExistsError, FileNotFoundError):
            pass
        threading.Thread(
            target=lambda: jieme(self.path, self.jiemipath, self.key, (self.label, self.label4),
                                 self.progressbar)).start()

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def place(self, **kwargs):
        self.frame.place(**kwargs)


class AddAJieMi:
    def __init__(self, root):
        self._root = root
        self.root = tk.CTkToplevel()
        self.root.title("添加加密")
        self.frame = tk.CTkFrame(self.root, corner_radius=10, fg_color="#2B2B2C")
        self.frame_a = tk.CTkFrame(self.frame, corner_radius=10, fg_color="#2B2B2C")
        self.input_yuan_score = tk.StringVar()
        self.label1 = tk.CTkLabel(self.frame_a, text='源文件:', font=("黑体", 20))
        self.input_yuan = tk.CTkEntry(self.frame_a, font=("黑体", 20), width=200,
                                      textvariable=self.input_yuan_score)
        self.input_blowse_btn = tk.CTkButton(self.frame_a, text='浏览', font=("黑体", 20), width=0,
                                             command=self.select_file, fg_color='green', hover_color='darkgreen')
        self.label1.pack(side=tk.LEFT, padx=3, pady=3)
        self.input_yuan.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=3, pady=3)
        self.input_blowse_btn.pack(side=tk.LEFT, padx=3, pady=3)
        self.frame_a.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.frame_b = tk.CTkFrame(self.frame, corner_radius=10, fg_color="#2B2B2C")
        self.label2 = tk.CTkLabel(self.frame_b, text='储存到:', font=("黑体", 20))
        self.input_jiemi_score = tk.StringVar()
        self.input_jiemi = tk.CTkEntry(self.frame_b, font=("黑体", 20), width=200,
                                       textvariable=self.input_jiemi_score)
        self.input_b_btn2 = tk.CTkButton(self.frame_b, text='浏览', font=("黑体", 20), width=0,
                                         command=self.select_save_where, fg_color='green', hover_color='darkgreen')
        self.label2.pack(side=tk.LEFT, padx=3, pady=3)
        self.input_jiemi.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=3, pady=3)
        self.input_b_btn2.pack(side=tk.LEFT, padx=3, pady=3)
        self.frame_b.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.key_var = tk.BooleanVar()
        self.key_var.set(True)
        self.select = tk.CTkRadioButton(self.frame, text='解密方式：使用秘钥', font=("黑体", 20), value=True,
                                        variable=self.key_var, fg_color='green', hover_color='darkgreen')
        self.select.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.frame2 = tk.CTkFrame(self.frame, corner_radius=10, fg_color="#2B2B2C")
        self.label3 = tk.CTkLabel(self.frame2, text='秘钥:', font=("黑体", 20))
        self.key = tk.StringVar()
        self.input_key_show = tk.CTkEntry(self.frame2, font=("黑体", 20), show='·',
                                          textvariable=self.key)
        self.label3.pack(side=tk.LEFT, padx=3, pady=3)
        self.input_key_show.pack(side=tk.LEFT, padx=3, pady=3, fill=tk.BOTH, expand=True, )
        self.frame2.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.startBtn = tk.CTkButton(self.root, text='现在解密!', font=("黑体", 90), command=self.jiemi,
                                     fg_color='green', hover_color='darkgreen')
        self.startBtn.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.root.resizable(False, False)

    def jiemi(self):
        yuan = self.input_yuan_score.get()
        input_jiemi_score = self.input_jiemi_score.get()
        if yuan and input_jiemi_score:
            key = self.key.get()
            if key:
                new_dl = OneJieMiGUI(self._root, yuan, self.input_jiemi_score.get(), key)
                new_dl.pack(padx=10, pady=10, side=tk.BOTTOM)
                new_dl.start()
                self.root.destroy()
            else:
                tm.showerror("错误", "您只有填写完所有信息之后，才能进行加密！")
        else:
            tm.showerror("错误", "您只有填写完所有信息之后，才能进行加密！")

    def select_file(self):
        name = tf.askopenfilename(
            title='选择加密文件',
            filetypes=[('加密结果图片', '*.png')],
        )
        if name:
            self.input_yuan_score.set(name)

    def select_save_where(self):
        out_dir = tf.askdirectory(
            title='选择保存位置',
        )
        if out_dir:
            self.input_jiemi_score.set(out_dir)

    def mainloop(self):
        self.root.mainloop()


class HelloGUI:
    def __init__(self, root):
        self.root = root
        self.frame = tk.CTkFrame(root, corner_radius=10, fg_color="#2B2B2C")
        self.frame2 = tk.CTkFrame(self.frame)
        self.frame2.grid(row=0, column=0, padx=3, pady=3)
        self.label = tk.CTkLabel(self.frame2, text="HELLO:)", font=("黑体", 50), text_color="white", bg_color="#2b2b2c")
        self.label.pack(padx=3, pady=3)
        self.label2 = tk.CTkLabel(self.frame2,
                                  text='这是一个完美的加密助手',
                                  font=("黑体", 10), text_color='grey')
        self.label2.pack(padx=3, pady=3)
        self.label3 = tk.CTkLabel(self.frame,
                                  text=f'使用右边的按钮新建加密或解密，使用安全的加密或快捷的解密在几秒钟内保障数据安全。',
                                  wraplength=350, font=("黑体", 15),
                                  text_color='grey')
        self.label3.grid(row=0, column=1, padx=3, pady=3)
        self.frame3 = tk.CTkFrame(self.frame)
        self.btn = tk.CTkButton(self.frame3, text="加密！", fg_color='#1E6BA5', hover_color='#134870', font=('楷体', 20),
                                width=280, command=self.jiami_add)
        self.btn.pack(padx=10, pady=5)
        self.btn2 = tk.CTkButton(self.frame3, text="解密！", fg_color='green', hover_color='darkgreen',
                                 font=("楷体", 20), width=280, command=self.jiemi_add)
        self.btn2.pack(padx=10, pady=5)
        self.frame3.grid(row=0, column=2, padx=3, pady=3)

    def jiami_add(self):
        AddAJiaMi(self.root).mainloop()

    def jiemi_add(self):
        AddAJieMi(self.root).mainloop()

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def place(self, **kwargs):
        self.frame.place(**kwargs)


def guis():
    tk.set_appearance_mode("dark")
    root = tk.CTk()
    root.title("完美加密——您的最后底牌")
    root.geometry('1008x622')  # 黄金分割
    root.resizable(False, False)
    scroll_frame = tk.CTkScrollableFrame(root, fg_color='#434343')
    hello = HelloGUI(scroll_frame)
    hello.pack(padx=10, pady=10)
    scroll_frame.pack(fill=tk.BOTH, expand=True, side=tk.BOTTOM)
    root.mainloop()


if __name__ == '__main__':
    guis()
