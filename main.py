import tkinter as tk
from tkinter import filedialog, messagebox, Scale, HORIZONTAL
import os
import subprocess
import time
import traceback
from settings_manager import SettingsManager

class VideoToFramesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video to Frames Converter")
        self.root.geometry("600x700")

        # Load settings from config file using SettingsManager
        self.settings_manager = SettingsManager()

        # Ensure ffmpeg_path is set before using it
        self.ffmpeg_path = self.settings_manager.get_setting('FFMPEG_PATH', fallback='ffmpeg')
        self.frames_per_second = int(self.settings_manager.get_setting('frames_per_second', fallback='30'))
        self.compression_quality = int(self.settings_manager.get_setting('compression_quality', fallback='6'))
        self.auto_adjust_fps = self.settings_manager.get_setting('auto_adjust_fps', fallback='True').lower() == 'true'
        self.max_concurrent_tasks = int(self.settings_manager.get_setting('max_concurrent_tasks', fallback='4'))

        # Menu bar
        self.menu_bar = tk.Menu(root)
        root.config(menu=self.menu_bar)

        # Settings menu
        self.settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Settings", menu=self.settings_menu)
        self.language_var = tk.StringVar(value=self.settings_manager.get_setting('language', fallback='English'))
        self.settings_menu.add_radiobutton(label="中文", variable=self.language_var, value="Chinese", command=self.change_language)
        self.settings_menu.add_radiobutton(label="English", variable=self.language_var, value="English", command=self.change_language)
        self.settings_menu.add_separator()
        self.settings_menu.add_command(label="About", command=self.settings_manager.show_about)
        self.settings_menu.add_command(label="Help", command=self.settings_manager.show_help)
        self.settings_menu.add_separator()
        self.settings_menu.add_command(label="Restore Defaults", command=self.restore_defaults)
        self.settings_menu.add_separator()
        self.settings_menu.add_command(label="Author's Homepage", command=self.settings_manager.open_authors_homepage)

        # FFmpeg menu
        self.ffmpeg_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="FFmpeg", menu=self.ffmpeg_menu)
        self.ffmpeg_menu.add_command(label="Install FFmpeg", command=self.settings_manager.install_ffmpeg)
        self.ffmpeg_menu.add_command(label="Check FFmpeg", command=self.settings_manager.check_ffmpeg)
        self.ffmpeg_menu.add_command(label="Select FFmpeg Path", command=self.settings_manager.select_ffmpeg_path)

        # Input video path
        self.input_label = tk.Label(root, text="Input Video Path:")
        self.input_label.pack(pady=5)

        self.input_path_var = tk.StringVar()
        self.input_entry = tk.Entry(root, textvariable=self.input_path_var, width=70)
        self.input_entry.pack(pady=5)

        self.input_button = tk.Button(root, text="Browse Single Video", command=self.select_single_video)
        self.input_button.pack(pady=5)

        self.batch_input_button = tk.Button(root, text="Batch Import Folder", command=self.select_batch_videos)
        self.batch_input_button.pack(pady=5)

        # Output directory path
        self.output_label = tk.Label(root, text="Output Directory Path:")
        self.output_label.pack(pady=5)

        self.output_path_var = tk.StringVar()
        self.output_entry = tk.Entry(root, textvariable=self.output_path_var, width=70)
        self.output_entry.pack(pady=5)

        self.output_button = tk.Button(root, text="Browse", command=self.select_output_directory)
        self.output_button.pack(pady=5)

        # Create folder checkbox
        self.create_folder_var = tk.BooleanVar(value=self.settings_manager.get_setting('create_folder', fallback=False))
        self.create_folder_checkbox = tk.Checkbutton(root, text="Create folder with same name as video", variable=self.create_folder_var, command=self.save_settings)
        self.create_folder_checkbox.pack(pady=10)

        # Auto adjust FPS checkbox
        self.auto_adjust_fps_var = tk.BooleanVar(value=self.auto_adjust_fps)
        self.auto_adjust_fps_checkbox = tk.Checkbutton(root, text="Auto Adjust FPS Based on Video", variable=self.auto_adjust_fps_var, command=self.save_settings)
        self.auto_adjust_fps_checkbox.pack(pady=10)

        # Frames per second entry
        self.fps_label = tk.Label(root, text="Frames per Second:")
        self.fps_label.pack(pady=5)

        self.fps_entry = tk.Entry(root, width=10)
        self.fps_entry.insert(0, str(self.frames_per_second))
        self.fps_entry.pack(pady=5)

        # Compression quality scale
        self.compression_label = tk.Label(root, text="Compression Quality (1-9):")
        self.compression_label.pack(pady=5)

        self.compression_scale = Scale(root, from_=1, to=9, orient=HORIZONTAL, length=200, resolution=1)
        self.compression_scale.set(self.compression_quality)
        self.compression_scale.pack(pady=5)

        # Max concurrent tasks entry
        self.concurrent_tasks_label = tk.Label(root, text="Max Concurrent Tasks (1-16):")
        self.concurrent_tasks_label.pack(pady=5)

        self.concurrent_tasks_entry = tk.Entry(root, width=10)
        self.concurrent_tasks_entry.insert(0, str(self.max_concurrent_tasks))
        self.concurrent_tasks_entry.pack(pady=5)

        # Convert button
        self.convert_button = tk.Button(root, text="Convert to Frames", command=self.convert_to_frames)
        self.convert_button.pack(pady=10)

        self.status_label = tk.Label(root, text="")
        self.status_label.pack(pady=10)

        # Initialize language and check ffmpeg installation
        self.change_language()
        if not self.settings_manager.is_ffmpeg_installed(self.ffmpeg_path):
            messagebox.showwarning("Warning妈妻！", "FFmpeg is not installed or selected. Please install it or select a path.")

    def save_settings(self):
        fps = self.fps_entry.get()
        compression_quality = self.compression_scale.get()
        max_concurrent_tasks = self.concurrent_tasks_entry.get()
        self.settings_manager.save_settings(
            language=self.language_var.get(),
            create_folder=self.create_folder_var.get(),
            frames_per_second=fps,
            compression_quality=compression_quality,
            auto_adjust_fps=self.auto_adjust_fps_var.get(),
            max_concurrent_tasks=max_concurrent_tasks
        )

    def restore_defaults(self):
        self.settings_manager.restore_defaults()
        self.create_folder_var.set(True)
        self.language_var.set('English')
        self.ffmpeg_path = 'ffmpeg'
        self.frames_per_second = 30
        self.compression_quality = 6
        self.auto_adjust_fps_var.set(True)
        self.max_concurrent_tasks = 4
        self.fps_entry.delete(0, tk.END)
        self.fps_entry.insert(0, str(self.frames_per_second))
        self.compression_scale.set(self.compression_quality)
        self.concurrent_tasks_entry.delete(0, tk.END)
        self.concurrent_tasks_entry.insert(0, str(self.max_concurrent_tasks))
        self.save_settings()
        self.change_language()
        messagebox.showinfo("Success", "Settings have been restored to their defaults.")

    def change_language(self):
        lang = self.language_var.get()
        translations = {
            "Chinese": {
                "title": "视频转帧工具",
                "input_label": "输入视频路径：",
                "output_label": "输出目录路径：",
                "create_folder": "创建与视频同名的文件夹",
                "convert_button": "转换为帧",
                "about": "关于",
                "help": "帮助",
                "restore_defaults": "恢复默认设置",
                "authors_homepage": "作者主页",
                "fps_label": "每秒帧数：",
                "compression_label": "压缩程度（1-9）：",
                "batch_import": "批量导入文件夹",
                "browse_single_video": "浏览单个视频",
                "auto_adjust_fps": "根据视频自动调整帧数",
                "concurrent_tasks_label": "最大并发任务数（1-16）："
            },
            "English": {
                "title": "Video to Frames Converter",
                "input_label": "Input Video Path:",
                "output_label": "Output Directory Path:",
                "create_folder": "Create folder with same name as video",
                "convert_button": "Convert to Frames",
                "about": "About",
                "help": "Help",
                "restore_defaults": "Restore Defaults",
                "authors_homepage": "Author's Homepage",
                "fps_label": "Frames per Second:",
                "compression_label": "Compression Quality (1-9):",
                "batch_import": "Batch Import Folder",
                "browse_single_video": "Browse Single Video",
                "auto_adjust_fps": "Auto Adjust FPS Based on Video",
                "concurrent_tasks_label": "Max Concurrent Tasks (1-16):"
            }
        }

        trans = translations[lang]
        self.root.title(trans["title"])
        self.input_label.config(text=trans["input_label"])
        self.output_label.config(text=trans["output_label"])
        self.create_folder_checkbox.config(text=trans["create_folder"])
        self.convert_button.config(text=trans["convert_button"])
        self.settings_menu.entryconfig(0, label="中文" if lang == "Chinese" else "Chinese")
        self.settings_menu.entryconfig(1, label="英文" if lang == "Chinese" else "English")
        self.settings_menu.entryconfig(3, label=trans["about"])
        self.settings_menu.entryconfig(4, label=trans["help"])
        self.settings_menu.entryconfig(6, label=trans["restore_defaults"])
        self.settings_menu.entryconfig(8, label=trans["authors_homepage"])
        self.fps_label.config(text=trans["fps_label"])
        self.compression_label.config(text=trans["compression_label"])
        self.input_button.config(text=trans["browse_single_video"])
        self.batch_input_button.config(text=trans["batch_import"])
        self.auto_adjust_fps_checkbox.config(text=trans["auto_adjust_fps"])
        self.concurrent_tasks_label.config(text=trans["concurrent_tasks_label"])

    def select_single_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mkv;*.mov")])
        if file_path:
            self.input_path_var.set(file_path)
            self.create_folder_var.set(False)  # Uncheck create folder by default for single video

    def select_batch_videos(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.input_path_var.set(dir_path)
            self.create_folder_var.set(True)  # Check create folder by default for batch processing

    def select_output_directory(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_path_var.set(dir_path)

    def convert_to_frames(self):
        if not self.settings_manager.is_ffmpeg_installed(self.ffmpeg_path):
            messagebox.showwarning("Warning", "FFmpeg is not installed or selected. Please install it or select a path.")
            return

        input_video_or_dir = self.input_path_var.get()
        output_dir = self.output_path_var.get()

        if not input_video_or_dir or not output_dir:
            messagebox.showwarning("Warning", "Please select both input video/file and output directory.")
            return

        try:
            fps = int(self.fps_entry.get())
            compression_quality = self.compression_scale.get()
            max_concurrent_tasks = min(int(self.concurrent_tasks_entry.get()), 16)

            if os.path.isdir(input_video_or_dir):
                video_files = [f for f in os.listdir(input_video_or_dir) if f.lower().endswith(('.mp4', '.avi', '.mkv', '.mov'))]
                if not video_files:
                    messagebox.showwarning("No Videos", "No video files found in the selected directory.")
                    return

                self.process_videos(video_files, input_video_or_dir, output_dir, fps, compression_quality, max_concurrent_tasks)
            else:
                video_name = os.path.splitext(os.path.basename(input_video_or_dir))[0]

                if self.create_folder_var.get():
                    frame_dir = os.path.join(output_dir, video_name)
                    os.makedirs(frame_dir, exist_ok=True)
                else:
                    frame_dir = output_dir

                ffmpeg_command = [
                    self.ffmpeg_path,
                    '-i', input_video_or_dir,
                    '-compression_level', str(compression_quality),
                ]

                if not self.auto_adjust_fps_var.get():
                    ffmpeg_command.extend(['-vf', f'fps={fps}'])

                ffmpeg_command.append(os.path.join(frame_dir, f'{video_name}_%05d.png'))

                self.status_label.config(text="Converting...")
                self.root.update_idletasks()

                subprocess.run(ffmpeg_command, check=True)

                self.status_label.config(text="Conversion completed.")
                messagebox.showinfo("Success搞掂晒！", "Frames have been successfully extracted.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for frames per second, compression quality, and max concurrent tasks.")
        except Exception as e:
             # 捕获完整的异常堆栈信息
            error_details = traceback.format_exc()
                
            # 创建一个包含详细信息的字符串，包括 FFmpeg 命令
            detailed_error_info = (
                f"Failed to start conversion for {video_file}.\n"
                f"FFmpeg Command: {' '.join(ffmpeg_command)}\n\n"
                f"Error Details:\n{error_details}"
                )
                
                # 更新状态标签
            self.status_label.config(text=f"Failed to start conversion for {video_file}: {e}")
            self.root.update_idletasks()

            # 显示带有详细信息的消息框，允许用户复制文本
            error_window = tk.Toplevel(self.root)
            error_window.title("Error Details")
            
            text_widget = tk.Text(error_window, wrap='word', height=20, width=80)
            text_widget.insert(tk.END, detailed_error_info)
            text_widget.pack(fill=tk.BOTH, expand=True)
            
            # 添加滚动条
            scrollbar = tk.Scrollbar(error_window, orient='vertical', command=text_widget.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.config(yscrollcommand=scrollbar.set)
                
            # 添加关闭按钮
            close_button = tk.Button(error_window, text="Close", command=error_window.destroy)
            close_button.pack(pady=10)

            # 确保窗口获得焦点
            error_window.grab_set()
            error_window.focus_set()

    def process_videos(self, video_files, input_video_or_dir, output_dir, fps, compression_quality, max_concurrent_tasks):
        total_videos = len(video_files)
        processed_videos = 0
        running_processes = []

        for video_file in video_files:
            while len(running_processes) >= max_concurrent_tasks:
                running_processes = [p for p in running_processes if p.poll() is None]
                time.sleep(1)  # Wait for 1 second before checking again

            video_path = os.path.join(input_video_or_dir, video_file)
            video_name = os.path.splitext(video_file)[0]

            if self.create_folder_var.get():
                frame_dir = os.path.join(output_dir, video_name)
                os.makedirs(frame_dir, exist_ok=True)
            else:
                frame_dir = output_dir

            ffmpeg_command = [
                self.ffmpeg_path,
                '-i', video_path,
                '-compression_level', str(compression_quality),
            ]

            if not self.auto_adjust_fps_var.get():
                ffmpeg_command.extend(['-vf', f'fps={fps}'])

            ffmpeg_command.append(os.path.join(frame_dir, f'{video_name}_%05d.png'))

            self.status_label.config(text=f"Starting conversion for {video_file} ({processed_videos + 1}/{total_videos})...")
            self.root.update_idletasks()

            try:
                process = subprocess.Popen(ffmpeg_command)
                running_processes.append(process)
                processed_videos += 1
                time.sleep(1)  # Wait for 1 second before starting the next task
            except Exception as e:
                # 捕获完整的异常堆栈信息
                error_details = traceback.format_exc()
                
                # 创建一个包含详细信息的字符串，包括 FFmpeg 命令
                detailed_error_info = (
                    f"Failed to start conversion for {video_file}.\n"
                    f"FFmpeg Command: {' '.join(ffmpeg_command)}\n\n"
                    f"Error Details:\n{error_details}"
                )
                
                # 更新状态标签
                self.status_label.config(text=f"Failed to start conversion for {video_file}: {e}")
                self.root.update_idletasks()

                # 显示带有详细信息的消息框，允许用户复制文本
                error_window = tk.Toplevel(self.root)
                error_window.title("Error Details")
                
                text_widget = tk.Text(error_window, wrap='word', height=20, width=80)
                text_widget.insert(tk.END, detailed_error_info)
                text_widget.pack(fill=tk.BOTH, expand=True)
                
                # 添加滚动条
                scrollbar = tk.Scrollbar(error_window, orient='vertical', command=text_widget.yview)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                text_widget.config(yscrollcommand=scrollbar.set)
                
                # 添加关闭按钮
                close_button = tk.Button(error_window, text="Close", command=error_window.destroy)
                close_button.pack(pady=10)

                # 确保窗口获得焦点
                error_window.grab_set()
                error_window.focus_set()

        while running_processes:
            running_processes = [p for p in running_processes if p.poll() is None]
            time.sleep(1)  # Wait for 1 second before checking again

        self.status_label.config(text="All conversions completed.")
        messagebox.showinfo("Success搞掂晒！", "All frames have been successfully extracted.")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoToFramesApp(root)
    root.mainloop()



