import os
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import threading

class VideoFrameExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("视频首尾帧提取工具")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        self.video_path = ""
        self.video_list = []
        self.output_dir = ""
        self.video_info = {}
        self.is_batch_mode = False
        
        self.setup_ui()
    
    def setup_ui(self):
        style = ttk.Style()
        style.configure('Title.TLabel', font=('微软雅黑', 16, 'bold'), foreground='#2c3e50')
        style.configure('SubTitle.TLabel', font=('微软雅黑', 12), foreground='#7f8c8d')
        style.configure('TButton', font=('微软雅黑', 10), padding=6)
        style.configure('Info.TLabel', font=('微软雅黑', 10), foreground='#34495e')
        style.configure('Treeview', font=('微软雅黑', 10), rowheight=25)
        style.configure('Treeview.Heading', font=('微软雅黑', 10, 'bold'))
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="🎬 视频首尾帧提取工具", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        mode_frame = ttk.Frame(main_frame)
        mode_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.mode_var = tk.StringVar(value="single")
        single_radio = ttk.Radiobutton(mode_frame, text="单视频模式", variable=self.mode_var, value="single", command=self.switch_mode)
        single_radio.pack(side=tk.LEFT, padx=(0, 20))
        
        batch_radio = ttk.Radiobutton(mode_frame, text="批量模式", variable=self.mode_var, value="batch", command=self.switch_mode)
        batch_radio.pack(side=tk.LEFT)
        
        self.single_frame = ttk.Frame(main_frame)
        self.single_frame.pack(fill=tk.BOTH, expand=True)
        
        top_frame = ttk.Frame(self.single_frame)
        top_frame.pack(fill=tk.X, pady=(0, 15))
        
        left_top_frame = ttk.Frame(top_frame)
        left_top_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        
        video_frame = ttk.LabelFrame(left_top_frame, text="视频选择", padding=15)
        video_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.video_path_var = tk.StringVar()
        video_entry = ttk.Entry(video_frame, textvariable=self.video_path_var, width=40, state='readonly')
        video_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        browse_video_btn = ttk.Button(video_frame, text="浏览视频", command=self.browse_video)
        browse_video_btn.pack(side=tk.LEFT)
        
        output_frame = ttk.LabelFrame(left_top_frame, text="输出目录", padding=15)
        output_frame.pack(fill=tk.X)
        
        self.output_dir_var = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var, width=40, state='readonly')
        output_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        browse_output_btn = ttk.Button(output_frame, text="选择目录", command=self.browse_output)
        browse_output_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        open_output_btn = ttk.Button(output_frame, text="打开目录", command=self.open_output_dir)
        open_output_btn.pack(side=tk.LEFT)
        
        info_frame = ttk.LabelFrame(top_frame, text="视频信息", padding=15)
        info_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        info_grid = ttk.Frame(info_frame)
        info_grid.pack(fill=tk.Y)
        
        ttk.Label(info_grid, text="文件名：", style='Info.TLabel').grid(row=0, column=0, sticky=tk.W, padx=5)
        self.filename_label = ttk.Label(info_grid, text="-", style='Info.TLabel')
        self.filename_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(info_grid, text="分辨率：", style='Info.TLabel').grid(row=1, column=0, sticky=tk.W, padx=5)
        self.resolution_label = ttk.Label(info_grid, text="-", style='Info.TLabel')
        self.resolution_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(info_grid, text="帧数：", style='Info.TLabel').grid(row=2, column=0, sticky=tk.W, padx=5)
        self.frame_count_label = ttk.Label(info_grid, text="-", style='Info.TLabel')
        self.frame_count_label.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(info_grid, text="时长：", style='Info.TLabel').grid(row=3, column=0, sticky=tk.W, padx=5)
        self.duration_label = ttk.Label(info_grid, text="-", style='Info.TLabel')
        self.duration_label.grid(row=3, column=1, sticky=tk.W, padx=5)
        
        preview_frame = ttk.LabelFrame(self.single_frame, text="预览", padding=15)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        preview_canvas = ttk.Frame(preview_frame)
        preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.first_frame_label = ttk.Label(preview_canvas, text="首帧预览", style='SubTitle.TLabel')
        self.first_frame_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.last_frame_label = ttk.Label(preview_canvas, text="尾帧预览", style='SubTitle.TLabel')
        self.last_frame_label.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.batch_frame = ttk.Frame(main_frame)
        
        batch_list_frame = ttk.LabelFrame(self.batch_frame, text="视频列表", padding=10)
        batch_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        tree_container = ttk.Frame(batch_list_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        self.video_tree = ttk.Treeview(tree_container, columns=("name", "resolution", "duration", "status"), show="headings", height=8)
        self.video_tree.heading("name", text="文件名")
        self.video_tree.heading("resolution", text="分辨率")
        self.video_tree.heading("duration", text="时长")
        self.video_tree.heading("status", text="状态")
        self.video_tree.column("name", width=250)
        self.video_tree.column("resolution", width=100)
        self.video_tree.column("duration", width=80)
        self.video_tree.column("status", width=100)
        
        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.video_tree.yview)
        self.video_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.video_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        batch_btn_frame = ttk.Frame(batch_list_frame)
        batch_btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        add_files_btn = ttk.Button(batch_btn_frame, text="添加视频", command=self.add_batch_files)
        add_files_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        add_folder_btn = ttk.Button(batch_btn_frame, text="添加文件夹", command=self.add_batch_folder)
        add_folder_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        remove_btn = ttk.Button(batch_btn_frame, text="移除选中", command=self.remove_selected)
        remove_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_btn = ttk.Button(batch_btn_frame, text="清空列表", command=self.clear_list)
        clear_btn.pack(side=tk.LEFT)
        
        batch_output_frame = ttk.LabelFrame(self.batch_frame, text="输出目录", padding=10)
        batch_output_frame.pack(fill=tk.X)
        
        self.batch_output_var = tk.StringVar()
        batch_output_entry = ttk.Entry(batch_output_frame, textvariable=self.batch_output_var, width=50, state='readonly')
        batch_output_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        batch_browse_btn = ttk.Button(batch_output_frame, text="选择目录", command=self.browse_batch_output)
        batch_browse_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        batch_open_btn = ttk.Button(batch_output_frame, text="打开目录", command=self.open_batch_output)
        batch_open_btn.pack(side=tk.LEFT)
        
        button_frame = ttk.Frame(main_frame, padding=10)
        button_frame.pack(fill=tk.X, pady=(10, 10))
        
        self.extract_btn = ttk.Button(button_frame, text="提取首尾帧", command=self.extract_frames)
        self.extract_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))
        self.progress_bar.pack_forget()
        
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, style='Info.TLabel')
        self.status_label.pack(fill=tk.X, pady=(5, 0))
        
        self.switch_mode()
    
    def switch_mode(self):
        mode = self.mode_var.get()
        self.is_batch_mode = (mode == "batch")
        
        self.single_frame.pack_forget()
        self.batch_frame.pack_forget()
        
        if self.is_batch_mode:
            self.batch_frame.pack(fill=tk.BOTH, expand=True)
            self.extract_btn.config(text="批量提取")
        else:
            self.single_frame.pack(fill=tk.BOTH, expand=True)
            self.extract_btn.config(text="提取首尾帧")
    
    def browse_video(self):
        path = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=[("视频文件", "*.mp4;*.avi;*.mov;*.mkv;*.flv;*.wmv")]
        )
        if path:
            self.video_path = path
            self.video_path_var.set(path)
            self.load_video_info()
    
    def browse_output(self):
        path = filedialog.askdirectory(title="选择输出目录")
        if path:
            self.output_dir = path
            self.output_dir_var.set(path)
    
    def browse_batch_output(self):
        path = filedialog.askdirectory(title="选择输出目录")
        if path:
            self.output_dir = path
            self.batch_output_var.set(path)
    
    def open_output_dir(self):
        if self.output_dir and os.path.exists(self.output_dir):
            os.startfile(self.output_dir)
        else:
            messagebox.showwarning("警告", "请先选择一个有效的输出目录")
    
    def open_batch_output(self):
        if self.output_dir and os.path.exists(self.output_dir):
            os.startfile(self.output_dir)
        else:
            messagebox.showwarning("警告", "请先选择一个有效的输出目录")
    
    def load_video_info(self):
        try:
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                messagebox.showerror("错误", "无法打开视频文件")
                return
            
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            duration = frame_count / fps if fps > 0 else 0
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            
            self.video_info = {
                'width': width,
                'height': height,
                'frame_count': frame_count,
                'fps': fps,
                'duration': f"{minutes}:{seconds:02d}"
            }
            
            self.filename_label.config(text=os.path.basename(self.video_path))
            self.resolution_label.config(text=f"{width} × {height}")
            self.frame_count_label.config(text=str(frame_count))
            self.duration_label.config(text=self.video_info['duration'])
            
            self.preview_frames(cap)
            cap.release()
            
        except Exception as e:
            messagebox.showerror("错误", f"读取视频信息失败：{str(e)}")
    
    def preview_frames(self, cap):
        try:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, first_frame = cap.read()
            if ret:
                first_frame_rgb = cv2.cvtColor(first_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(first_frame_rgb)
                img = img.resize((150, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image=img)
                self.first_frame_label.config(image=photo, text="")
                self.first_frame_label.image = photo
            
            last_frame_idx = max(0, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, last_frame_idx)
            ret, last_frame = cap.read()
            if ret:
                last_frame_rgb = cv2.cvtColor(last_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(last_frame_rgb)
                img = img.resize((150, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image=img)
                self.last_frame_label.config(image=photo, text="")
                self.last_frame_label.image = photo
                
        except Exception as e:
            print(f"预览帧加载失败：{e}")
    
    def add_batch_files(self):
        paths = filedialog.askopenfilenames(
            title="选择视频文件",
            filetypes=[("视频文件", "*.mp4;*.avi;*.mov;*.mkv;*.flv;*.wmv")]
        )
        if paths:
            for path in paths:
                if path not in self.video_list:
                    self.video_list.append(path)
                    info = self.get_video_info_quick(path)
                    self.video_tree.insert("", tk.END, values=(os.path.basename(path), info['resolution'], info['duration'], "等待中"))
    
    def add_batch_folder(self):
        folder = filedialog.askdirectory(title="选择视频文件夹")
        if folder:
            video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith(video_extensions):
                        path = os.path.join(root, file)
                        if path not in self.video_list:
                            self.video_list.append(path)
                            info = self.get_video_info_quick(path)
                            self.video_tree.insert("", tk.END, values=(os.path.basename(path), info['resolution'], info['duration'], "等待中"))
    
    def get_video_info_quick(self, path):
        try:
            cap = cv2.VideoCapture(path)
            if cap.isOpened():
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                duration = frame_count / fps if fps > 0 else 0
                minutes = int(duration // 60)
                seconds = int(duration % 60)
                cap.release()
                return {'resolution': f"{width} × {height}", 'duration': f"{minutes}:{seconds:02d}"}
        except:
            pass
        return {'resolution': "未知", 'duration': "未知"}
    
    def remove_selected(self):
        selected = self.video_tree.selection()
        for item in selected:
            idx = self.video_tree.index(item)
            if idx < len(self.video_list):
                self.video_list.pop(idx)
            self.video_tree.delete(item)
    
    def clear_list(self):
        self.video_list.clear()
        for item in self.video_tree.get_children():
            self.video_tree.delete(item)
    
    def extract_frames(self):
        if self.is_batch_mode:
            if not self.video_list:
                messagebox.showwarning("警告", "请先添加视频文件")
                return
            if not self.output_dir:
                messagebox.showwarning("警告", "请先选择输出目录")
                return
            self.batch_extract()
        else:
            if not self.video_path or not self.output_dir:
                messagebox.showwarning("警告", "请先选择视频文件和输出目录")
                return
            self.single_extract()
    
    def single_extract(self):
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))
        self.status_var.set("正在提取...")
        thread = threading.Thread(target=self.do_extract, args=([self.video_path],))
        thread.start()
    
    def batch_extract(self):
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))
        self.status_var.set("正在批量提取...")
        thread = threading.Thread(target=self.do_extract, args=(self.video_list.copy(),))
        thread.start()
    
    def do_extract(self, video_paths):
        success_count = 0
        fail_count = 0
        total = len(video_paths)
        
        for i, video_path in enumerate(video_paths):
            try:
                self.status_var.set(f"正在处理 ({i+1}/{total}): {os.path.basename(video_path)}")
                self.progress_var.set((i / total) * 100)
                
                if not os.path.exists(video_path):
                    self.update_status(i, "文件不存在")
                    fail_count += 1
                    continue
                
                output_dir = os.path.normpath(self.output_dir)
                video_path_norm = os.path.normpath(video_path)
                
                cap = cv2.VideoCapture(video_path_norm)
                if not cap.isOpened():
                    self.update_status(i, "打开失败")
                    fail_count += 1
                    continue
                
                ret, first_frame = cap.read()
                if not ret:
                    self.update_status(i, "读取首帧失败")
                    cap.release()
                    fail_count += 1
                    continue
                
                last_frame = None
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                
                for attempt in range(3):
                    last_frame_idx = max(0, total_frames - 1 - attempt)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, last_frame_idx)
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        last_frame = frame
                        break
                
                cap.release()
                
                if last_frame is None:
                    self.update_status(i, "读取尾帧失败")
                    fail_count += 1
                    continue
                
                video_name = os.path.splitext(os.path.basename(video_path_norm))[0]
                first_frame_path = os.path.join(output_dir, f"{video_name}_首帧.jpg")
                last_frame_path = os.path.join(output_dir, f"{video_name}_尾帧.jpg")
                
                first_frame_rgb = cv2.cvtColor(first_frame, cv2.COLOR_BGR2RGB)
                first_image = Image.fromarray(first_frame_rgb)
                first_image.save(first_frame_path, 'JPEG', quality=95)
                
                last_frame_rgb = cv2.cvtColor(last_frame, cv2.COLOR_BGR2RGB)
                last_image = Image.fromarray(last_frame_rgb)
                last_image.save(last_frame_path, 'JPEG', quality=95)
                
                self.update_status(i, "成功")
                success_count += 1
                
            except Exception as e:
                print(f"提取失败: {video_path} - {str(e)}")
                self.update_status(i, "失败")
                fail_count += 1
        
        self.progress_var.set(100)
        self.status_var.set(f"提取完成！成功: {success_count}, 失败: {fail_count}")
        messagebox.showinfo("完成", f"批量提取完成！\n\n成功: {success_count} 个\n失败: {fail_count} 个")
        self.progress_bar.pack_forget()
    
    def update_status(self, index, status):
        items = self.video_tree.get_children()
        if index < len(items):
            item = items[index]
            values = list(self.video_tree.item(item, "values"))
            values[3] = status
            self.video_tree.item(item, values=values)

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoFrameExtractor(root)
    root.mainloop()
