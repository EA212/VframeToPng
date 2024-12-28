import configparser
import os
import shutil
import subprocess
import webbrowser
from tkinter import filedialog, messagebox


class SettingsManager:
    def __init__(self):
        self.config_file = 'settings.ini'
        self.load_settings()

    def load_settings(self):
        self.config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self.config['DEFAULT'] = {
                'language': 'English',
                'create_folder': 'True',  # Default to True for batch processing
                'FFMPEG_PATH': 'ffmpeg',
                'frames_per_second': '30',  # Default frames per second
                'compression_quality': '6',  # Default compression quality (1-9)
                'auto_adjust_fps': 'True'  # Default auto adjust fps
            }
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)  # Write the default settings to the config file

    def save_settings(self, ffmpeg_path=None, language=None, create_folder=None, frames_per_second=None, compression_quality=None, auto_adjust_fps=None, max_concurrent_tasks=None):
        if ffmpeg_path is not None:
            self.config.set('DEFAULT', 'FFMPEG_PATH', ffmpeg_path)
        if language is not None:
            self.config.set('DEFAULT', 'language', language)
        if create_folder is not None:
            self.config.set('DEFAULT', 'create_folder', str(create_folder))
        if frames_per_second is not None:
            self.config.set('DEFAULT', 'frames_per_second', str(frames_per_second))
        if compression_quality is not None:
            self.config.set('DEFAULT', 'compression_quality', str(compression_quality))
        if auto_adjust_fps is not None:
            self.config.set('DEFAULT', 'auto_adjust_fps', str(auto_adjust_fps))
        if max_concurrent_tasks is not None:
            self.config.set('DEFAULT', 'max_concurrent_tasks', str(max_concurrent_tasks))  

        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def restore_defaults(self):
        default_settings = {
            'language': 'English',
            'create_folder': 'True',
            'FFMPEG_PATH': 'ffmpeg',
            'frames_per_second': '30',
            'compression_quality': '6',
            'auto_adjust_fps': 'True'
        }
        for key, value in default_settings.items():
            self.config.set('DEFAULT', key, value)

        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def get_setting(self, key, fallback=None):
        return self.config.get('DEFAULT', key, fallback=fallback)

    def show_about(self):
        messagebox.showinfo("About", "Author: Vivideo-studio(bilibili.com)\nVersion: 1.0\nDescription: A tool to convert video files into frames.")  # 改为你们的信息

    def show_help(self):
        help_text = """
        Help:
        - Select an input video file or folder using the respective buttons.
        - Choose an output directory where the frames will be saved.
        - Optionally check the box to create a folder named after the video for saving frames.
        - Set the desired frames per second and compression quality.
        - Click 'Convert to Frames' to start the conversion process.
        """
        messagebox.showinfo("Help", help_text)

    def open_authors_homepage(self):
        url = "https://space.bilibili.com/1464311623"  # 改为你们的网页
        webbrowser.open(url)

    def install_ffmpeg(self):
        ffmpeg_zip_path = filedialog.askopenfilename(
            title="Select FFmpeg ZIP File",
            filetypes=[("ZIP files", "*.zip")]
        )
        if not ffmpeg_zip_path:
            return

        install_dir = filedialog.askdirectory(
            title="Select Installation Directory"
        )
        if not install_dir:
            return

        try:
            shutil.unpack_archive(ffmpeg_zip_path, install_dir)
            ffmpeg_bin_path = os.path.join(install_dir, 'bin', 'ffmpeg.exe')
            if os.path.exists(ffmpeg_bin_path):
                self.save_settings(ffmpeg_path=ffmpeg_bin_path)
                messagebox.showinfo("Success得咗", "FFmpeg has been successfully installed.")
            else:
                messagebox.showerror("Error", "叼奶咯，FFmpeg executable not found in the extracted files.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while installing FFmpeg: {str(e)}")

    def check_ffmpeg(self):
        ffmpeg_path = self.get_setting('FFMPEG_PATH', fallback='ffmpeg')
        if self.is_ffmpeg_installed(ffmpeg_path):
            version_info = self.get_ffmpeg_version(ffmpeg_path)
            messagebox.showinfo("FFmpeg Info", f"FFmpeg is installed at: {ffmpeg_path}\nVersion: {version_info}")
        else:
            messagebox.showwarning("FFmpeg Not Found", "叼奶咯，FFmpeg is not installed or selected.")

    def get_ffmpeg_version(self, ffmpeg_path):
        try:
            result = subprocess.run([ffmpeg_path, '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
            return result.stdout.splitlines()[0].strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "Unknown"

    def select_ffmpeg_path(self):
        ffmpeg_path = filedialog.askopenfilename(
            title="Select FFmpeg Executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if ffmpeg_path:
            self.save_settings(ffmpeg_path=ffmpeg_path)
            messagebox.showinfo("Success", f"FFmpeg path set to: {ffmpeg_path}")

    def is_ffmpeg_installed(self, ffmpeg_path):
        try:
            subprocess.run([ffmpeg_path, '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False



