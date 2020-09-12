import tkinter as tk
from tkinter.filedialog import askdirectory
import json
import random
import os
from os.path import isfile, join
import logging

CONFIG_PATH = "config.json"
DEFAULT_EXECUTABLES = [".mp4", ".mov", ".wmv", ".flv", ".avi"]
#pyinstaller --onefile --clean -w main.py


class Gui(tk.Tk):
    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Random File Executer")
        self.executables = []
        self.header = tk.Frame(self, height=30)
        self.content = tk.Frame(self, bg='gray')
        self.footer = tk.Frame(self, height=30)

        self.header.pack(fill='both')
        self.content.pack(fill='both', expand=True)
        self.content.category_frames = []
        self.footer.pack(fill='both')


        self.prev_files_active_var = tk.IntVar(value=0)
        self.prev_files_active = tk.Checkbutton(self.header, text="Don't open the last", variable=self.prev_files_active_var)
        self.prev_files_active.pack(side=tk.LEFT)
        self.prev_files_var = tk.IntVar(value=0)
        vcmd = (self.register(validate_is_digit))
        self.prev_files = tk.Entry(self.header, textvariable=self.prev_files_var, validate='all', validatecommand=(vcmd, '%P'), width=5)
        self.prev_files.pack(side=tk.LEFT)
        tk.Label(self.header, text="files").pack(side=tk.LEFT)


        self.auto_save_var = tk.IntVar(value=0)
        self.auto_save = tk.Checkbutton(self.header, text="Save config on execute", variable=self.auto_save_var)
        self.auto_save.pack(side=tk.LEFT)
        self.save_button = tk.Button(self.header, text="Save Config", command=self.save_config)
        self.save_button.pack(side=tk.LEFT)
        self.execute_button = tk.Button(self.header, text="Execute File", command=self.start_video)
        self.execute_button.pack(side=tk.RIGHT)

        self.execute_label = tk.Label(self.footer, text="loading...")
        self.execute_label.pack(side=tk.LEFT)
        self.add_button = tk.Button(self.footer, text="Add category", command=self.add_category_command)
        self.add_button.pack(side=tk.RIGHT)

        self.last_added_path = '/'
        self.close_on_execute = True

        self.read_config()

    def read_config(self): #TODO dont add config.json to zip
        try:
            with open(CONFIG_PATH, "r") as config_file:
                config = json.load(config_file)
        except Exception as e:
            logging.warning("Couldn't read config.")
            config = {}

        prev_files = config.get("prev_files")
        if prev_files and type(prev_files) == dict:
            self.prev_files_active_var.set(1 if prev_files.get("active", False) else 0)
            self.prev_files_var.set(prev_files.get("number", 0))

        self.last_added_path = config.get("last_added_path", "/")
        self.close_on_execute = config.get("close_on_execute", True)
        self.executables = config.get("executables", DEFAULT_EXECUTABLES)
        if self.executables:
            self.execute_label.configure(text="Executing files: {}".format(", ".join(self.executables)))
        else:
            self.execute_label.configure(text="WARNING: No executing files set! Any chosen file will be executed!", bg="yellow")

        self.auto_save_var.set(1 if config.get("auto_save", True) else 0)

        for category in config.get("categories", []):
            self.add_category_frame(path=category.get("path"), name=category.get("name"), weight=category.get("weight"))

    def save_config(self):
        with open(CONFIG_PATH, "w+", encoding='utf-8') as config_file:
            config = {}

            config["executables"] = self.executables
            config["auto_save"] = True if self.auto_save_var.get() else False
            config["last_added_path"] = self.last_added_path
            config["close_on_execute"] = self.close_on_execute
            config["prev_files"] = {
                "active": True if self.prev_files_active_var.get() else False,
                "number": self.prev_files_var.get()
            }
            categories = []
            for category in self.content.category_frames:
                categories.append({
                    "name": category.name.get(),
                    "path": category.path.get(),
                    "weight": category.weight.get(),
                    "series": category.series
                })
            config["categories"] = categories
            json.dump(config, config_file, ensure_ascii=False, indent=4)

    def add_category_frame(self, path, name="noname", weight=1, series=False):
        frame = CategoryFrame(self.content, path, name=name, weight=weight, series=series)
        self.content.category_frames.append(frame)
        frame.pack(fill='both', padx=5, pady=2)

    def add_category_command(self):
        dirname = askdirectory(initialdir=self.last_added_path, title="Select directory")
        if dirname:
            try:
                self.last_added_path, name = dirname.rsplit('/', 1)
            except:
                self.last_added_path = dirname
                name = None
            self.add_category_frame(dirname, name=name)

    def start_video(self):
        if self.auto_save_var.get():
            self.save_config()

        abs_weight = 0
        for category in self.content.category_frames:
            abs_weight += category.weight.get()

        if abs_weight == 0:
            message("ConfigError", "Combined weight must be bigger than 0. Combined Weight is: {}".format(abs_weight))
            return

        choice = random.randint(1, abs_weight)

        for category in self.content.category_frames:
            abs_weight -= category.weight.get()
            if choice > abs_weight:
                file = self.get_file(category)
                break
        else:
            logging.error("how did we get here?")
            return
        if file:
            os.startfile(file, 'open')
            with open("./executed_files.log", "a+") as executed_files:
                executed_files.write(file + "\n")

        if self.close_on_execute:
            self.quit()

    def get_file(self, path):
        dirpath = path.path.get()
        file_paths = []
        prev_files_active = self.prev_files_active_var.get()
        prev_files_count = 0
        executed_files = []
        if prev_files_active:
            try:
                with open("./executed_files.log", "r+") as ex_files:
                    executed_files = ex_files.readlines()[-self.prev_files_var.get():]
            except:
                pass

        for i in range(2):
            for f in os.listdir(dirpath):
                file_path = join(dirpath, f)
                if not isfile(file_path):
                    continue
                if path.series and "1" not in f:
                    continue
                if prev_files_active:
                    if file_path + "\n" in executed_files:
                        prev_files_count += 1
                        continue
                for executable in self.executables:
                    if f.endswith(executable):
                        break
                else:
                    continue
                file_paths.append(file_path)

            if prev_files_count and not file_paths: #Try again if all files were previously executed
                logging.debug("found no file that wasn't executed before: restart search")
                prev_files_active = False
            else:
                break

        if not file_paths:
            message("NotFoundError", "Couldn't find files in {} which end with: {}".format(path.path.get(), self.executables))
            return False
        else:
            return random.choice(file_paths)


def message(pop_title, msg): #stops rest of code execution
    logging.debug("Popup: {}: {}".format(pop_title, msg))
    popup = tk.Toplevel()
    popup.title(pop_title)
    label = tk.Label(popup, text=msg)  # Can add a font arg here
    label.pack(side="top", fill="x", pady=10)
    B1 = tk.Button(popup, text="Ok", command=popup.destroy)
    B1.pack()
    popup.mainloop()


class CategoryFrame(tk.Frame):
    def __init__(self, parent, path, name, weight, series=False):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.name = tk.StringVar(value=name)
        tk.Label(self, text="name:").pack(side=tk.LEFT)
        tk.Entry(self, textvariable=self.name).pack(side=tk.LEFT)

        self.path = tk.StringVar(value=path)
        tk.Label(self, text="path:").pack(side=tk.LEFT)
        tk.Entry(self, textvariable=self.path).pack(side=tk.LEFT, expand=True, fill='both')

        tk.Button(self, text="Remove", command=self.remove).pack(side=tk.RIGHT)

        self.weight = tk.IntVar(value=weight)
        vcmd = (self.register(validate_is_digit))
        tk.Entry(self, textvariable=self.weight, validate='all', validatecommand=(vcmd, '%P'), width=5).pack(side=tk.RIGHT)
        tk.Label(self, text="weight:").pack(side=tk.RIGHT)

        self.series = series

    def remove(self):
        self.parent.category_frames.remove(self)
        self.destroy()


def validate_is_digit(P):
    if str.isdigit(P) or P == "":
        return True
    else:
        return False


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%d.%m.%Y %H:%M',
                    filename='debug.log')
try:
    app = Gui()
    app.geometry("720x400")
    app.mainloop()
except Exception as e:
    logging.error(repr(e), exc_info=True)
