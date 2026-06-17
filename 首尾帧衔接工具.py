import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from PIL import Image, ImageTk
import threading
import json
import base64
import requests
from model_manager import ModelManager

class VideoTransitionGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("首尾帧衔接工具 - 视频生成工作流")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # 初始化模型管理器
        self.model_manager = ModelManager()
        
        self.start_image = ""
        self.end_image = ""
        self.output_dir = ""
        self.start_img_data = None
        self.end_img_data = None
        self.is_generating = False
        self.is_analyzing = False
        
        self.start_image_info = ""
        self.end_image_info = ""
        self.ai_prompt = ""
        
        # 获取模型分类
        self.categories = self.model_manager.get_categories()
        
        self.setup_ui()
    
    def setup_ui(self):
        style = ttk.Style()
        style.configure('Title.TLabel', font=('微软雅黑', 14, 'bold'), foreground='#2c3e50')
        style.configure('SubTitle.TLabel', font=('微软雅黑', 10), foreground='#7f8c8d')
        style.configure('TButton', font=('微软雅黑', 9), padding=4)
        style.configure('Info.TLabel', font=('微软雅黑', 9), foreground='#34495e')
        style.configure('TEntry', font=('微软雅黑', 9))
        style.configure('TCombobox', font=('微软雅黑', 9))
        
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="🎬 首尾帧衔接工具", style='Title.TLabel')
        title_label.pack(pady=(0, 5))
        
        top_content_frame = ttk.Frame(main_frame)
        top_content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 左侧图片区域
        image_frame = ttk.LabelFrame(top_content_frame, text="图片", padding=8)
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        start_frame = ttk.Frame(image_frame)
        start_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 3))
        
        self.start_canvas = tk.Canvas(start_frame, bg='#2c3e50', highlightthickness=0, height=200)
        self.start_canvas.pack(fill=tk.BOTH, expand=True, pady=(0, 3))
        self.start_canvas.create_text(100, 100, text="起始图片", fill='white', font=('微软雅黑', 9), tags="placeholder")
        
        start_btn = ttk.Button(start_frame, text="选择起始", command=self.load_start_image)
        start_btn.pack(fill=tk.X)
        
        end_frame = ttk.Frame(image_frame)
        end_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(3, 0))
        
        self.end_canvas = tk.Canvas(end_frame, bg='#2c3e50', highlightthickness=0, height=200)
        self.end_canvas.pack(fill=tk.BOTH, expand=True, pady=(0, 3))
        self.end_canvas.create_text(100, 100, text="结束图片", fill='white', font=('微软雅黑', 9), tags="placeholder")
        
        end_btn = ttk.Button(end_frame, text="选择结束", command=self.load_end_image)
        end_btn.pack(fill=tk.X)
        
        # 右侧配置区域
        right_frame = ttk.Frame(top_content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        
        # AI配置区域
        ai_config_frame = ttk.LabelFrame(right_frame, text="AI配置", padding=8)
        ai_config_frame.pack(fill=tk.X, pady=(0, 8))
        
        # 模型分类选择
        ttk.Label(ai_config_frame, text="模型类型：", style='Info.TLabel').grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        self.vision_category_var = tk.StringVar(value="vision")
        vision_categories = ["vision"]
        category_combo = ttk.Combobox(ai_config_frame, textvariable=self.vision_category_var, values=vision_categories, width=20, state='readonly')
        category_combo.grid(row=0, column=1, sticky=tk.W, padx=2, pady=2)
        
        # 视觉模型选择
        ttk.Label(ai_config_frame, text="视觉模型：", style='Info.TLabel').grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        self.vision_model_var = tk.StringVar()
        vision_models = [m["name"] for m in self.categories["vision"]["models"]]
        self.vision_model_combo = ttk.Combobox(ai_config_frame, textvariable=self.vision_model_var, values=vision_models, width=28, state='readonly')
        if vision_models:
            self.vision_model_var.set(vision_models[0])
        self.vision_model_combo.grid(row=1, column=1, sticky=tk.W, padx=2, pady=2)
        
        # 文本模型选择
        ttk.Label(ai_config_frame, text="文本模型：", style='Info.TLabel').grid(row=2, column=0, sticky=tk.W, padx=2, pady=2)
        self.text_model_var = tk.StringVar()
        text_models = [m["name"] for m in self.categories["text_to_text"]["models"]]
        self.text_model_combo = ttk.Combobox(ai_config_frame, textvariable=self.text_model_var, values=text_models, width=28, state='readonly')
        if text_models:
            self.text_model_var.set(text_models[0])
        self.text_model_combo.grid(row=2, column=1, sticky=tk.W, padx=2, pady=2)
        
        # API Key输入
        ttk.Label(ai_config_frame, text="API Key：", style='Info.TLabel').grid(row=3, column=0, sticky=tk.W, padx=2, pady=2)
        self.api_key_var = tk.StringVar(value="")
        api_key_entry = ttk.Entry(ai_config_frame, textvariable=self.api_key_var, width=30, show="*")
        api_key_entry.grid(row=3, column=1, sticky=tk.W, padx=2, pady=2)
        
        # 视频参数区域
        param_frame = ttk.LabelFrame(right_frame, text="视频参数", padding=8)
        param_frame.pack(fill=tk.X, pady=(0, 8))
        
        param_grid = ttk.Frame(param_frame)
        param_grid.pack(fill=tk.X)
        
        ttk.Label(param_grid, text="分辨率：", style='Info.TLabel').grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        self.width_var = tk.StringVar(value="1920")
        width_entry = ttk.Entry(param_grid, textvariable=self.width_var, width=6)
        width_entry.grid(row=0, column=1, padx=2, pady=2)
        ttk.Label(param_grid, text="×", style='Info.TLabel').grid(row=0, column=2, padx=0, pady=2)
        self.height_var = tk.StringVar(value="1080")
        height_entry = ttk.Entry(param_grid, textvariable=self.height_var, width=6)
        height_entry.grid(row=0, column=3, padx=2, pady=2)
        
        ttk.Label(param_grid, text="帧率：", style='Info.TLabel').grid(row=0, column=4, sticky=tk.W, padx=2, pady=2)
        self.fps_var = tk.StringVar(value="30")
        fps_entry = ttk.Entry(param_grid, textvariable=self.fps_var, width=4)
        fps_entry.grid(row=0, column=5, padx=2, pady=2)
        
        ttk.Label(param_grid, text="时长：", style='Info.TLabel').grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        self.duration_var = tk.StringVar(value="5")
        duration_entry = ttk.Entry(param_grid, textvariable=self.duration_var, width=4)
        duration_entry.grid(row=1, column=1, padx=2, pady=2)
        
        ttk.Label(param_grid, text="过渡：", style='Info.TLabel').grid(row=1, column=2, sticky=tk.W, padx=2, pady=2)
        self.transition_mode = tk.StringVar(value="morph")
        mode_combo = ttk.Combobox(param_grid, textvariable=self.transition_mode, width=8, state='readonly')
        mode_combo['values'] = ('morph', 'flow', 'blend')
        mode_combo.grid(row=1, column=3, padx=2, pady=2)
        
        ttk.Label(param_grid, text="缓动：", style='Info.TLabel').grid(row=1, column=4, sticky=tk.W, padx=2, pady=2)
        self.easing_var = tk.StringVar(value="ease_in_out")
        easing_combo = ttk.Combobox(param_grid, textvariable=self.easing_var, width=10, state='readonly')
        easing_combo['values'] = ('linear', 'ease_in', 'ease_out', 'ease_in_out')
        easing_combo.grid(row=1, column=5, padx=2, pady=2)
        
        # 转换要求区域
        requirement_frame = ttk.LabelFrame(right_frame, text="转换要求", padding=8)
        requirement_frame.pack(fill=tk.BOTH, expand=True)
        
        self.requirement_text = scrolledtext.ScrolledText(requirement_frame, height=4, font=('微软雅黑', 9), wrap=tk.WORD)
        self.requirement_text.pack(fill=tk.X, pady=(0, 5))
        self.requirement_text.insert(tk.END, "请描述你希望的视频转换效果...")
        
        self.analyze_btn = ttk.Button(requirement_frame, text="🎯 AI分析并生成", command=self.analyze_with_ai)
        self.analyze_btn.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(requirement_frame, text="AI提示词：", style='Info.TLabel').pack(anchor=tk.W)
        self.ai_prompt_text = scrolledtext.ScrolledText(requirement_frame, height=3, font=('微软雅黑', 8), wrap=tk.WORD)
        self.ai_prompt_text.pack(fill=tk.BOTH, expand=True)
        
        # 底部操作区域
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(5, 0))
        
        output_frame = ttk.Frame(bottom_frame)
        output_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(output_frame, text="输出目录：", style='Info.TLabel').pack(side=tk.LEFT, padx=(0, 5))
        self.output_dir_var = tk.StringVar(value="")
        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var, width=30)
        output_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        browse_output_btn = ttk.Button(output_frame, text="选择", command=self.browse_output, width=6)
        browse_output_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        open_output_btn = ttk.Button(output_frame, text="打开", command=self.open_output_dir, width=6)
        open_output_btn.pack(side=tk.LEFT)
        
        button_container = ttk.Frame(bottom_frame)
        button_container.pack(side=tk.RIGHT)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(button_container, variable=self.progress_var, maximum=100, length=150)
        self.progress_bar.pack(side=tk.LEFT, padx=(0, 10))
        
        self.generate_btn = ttk.Button(button_container, text="🚀 生成视频", command=self.generate_video)
        self.generate_btn.pack(side=tk.LEFT)
        
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, style='Info.TLabel')
        self.status_label.pack(fill=tk.X, pady=(5, 0))
    
    def get_selected_vision_provider(self):
        """获取选择的视觉模型提供商"""
        model_name = self.vision_model_var.get()
        for model in self.categories["vision"]["models"]:
            if model["name"] == model_name:
                return model["provider"]
        return None
    
    def get_selected_text_provider(self):
        """获取选择的文本模型提供商"""
        model_name = self.text_model_var.get()
        for model in self.categories["text_to_text"]["models"]:
            if model["name"] == model_name:
                return model["provider"]
        return None
    
    def load_start_image(self):
        path = filedialog.askopenfilename(
            title="选择起始图片",
            filetypes=[("图片文件", "*.jpg;*.jpeg;*.png;*.bmp")]
        )
        if path:
            self.start_image = path
            self.start_img_data = self.read_image_with_chinese_path(path)
            if self.start_img_data is not None:
                self.start_img_data = cv2.cvtColor(self.start_img_data, cv2.COLOR_BGR2RGB)
                self.show_image_on_canvas(self.start_img_data, self.start_canvas)
                self.status_var.set(f"已加载起始图片: {os.path.basename(path)}")
            else:
                messagebox.showerror("错误", f"无法读取图片文件:\n{path}")
    
    def load_end_image(self):
        path = filedialog.askopenfilename(
            title="选择结束图片",
            filetypes=[("图片文件", "*.jpg;*.jpeg;*.png;*.bmp")]
        )
        if path:
            self.end_image = path
            self.end_img_data = self.read_image_with_chinese_path(path)
            if self.end_img_data is not None:
                self.end_img_data = cv2.cvtColor(self.end_img_data, cv2.COLOR_BGR2RGB)
                self.show_image_on_canvas(self.end_img_data, self.end_canvas)
                self.status_var.set(f"已加载结束图片: {os.path.basename(path)}")
            else:
                messagebox.showerror("错误", f"无法读取图片文件:\n{path}")
    
    def read_image_with_chinese_path(self, path):
        try:
            img_array = np.fromfile(path, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            print(f"读取图片错误: {e}")
            return None
    
    def show_image_on_canvas(self, img_data, canvas):
        canvas.delete("all")
        
        canvas.update_idletasks()
        canvas_w = canvas.winfo_width()
        canvas_h = canvas.winfo_height()
        
        if canvas_w <= 1:
            canvas_w = 400
        if canvas_h <= 1:
            canvas_h = 300
        
        h, w = img_data.shape[:2]
        scale = min(canvas_w / w, canvas_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        img_resized = cv2.resize(img_data, (new_w, new_h), interpolation=cv2.INTER_AREA)
        img = Image.fromarray(img_resized)
        photo = ImageTk.PhotoImage(image=img)
        
        x = (canvas_w - new_w) // 2
        y = (canvas_h - new_h) // 2
        
        canvas.create_image(x, y, anchor=tk.NW, image=photo)
        
        if canvas == self.start_canvas:
            self.start_canvas.image = photo
        else:
            self.end_canvas.image = photo
    
    def browse_output(self):
        path = filedialog.askdirectory(title="选择输出目录")
        if path:
            self.output_dir = path
            self.output_dir_var.set(path)
    
    def open_output_dir(self):
        if self.output_dir and os.path.exists(self.output_dir):
            os.startfile(self.output_dir)
        else:
            messagebox.showwarning("警告", "请先选择一个有效的输出目录")
    
    def encode_image_to_base64(self, img_data):
        _, buffer = cv2.imencode('.jpg', img_data)
        return base64.b64encode(buffer).decode('utf-8')
    
    def analyze_with_ai(self):
        if not self.start_image or not self.end_image:
            messagebox.showwarning("警告", "请先选择起始图片和结束图片")
            return
        
        api_key = self.api_key_var.get()
        if not api_key:
            messagebox.showwarning("警告", "请先配置API Key")
            return
        
        if self.is_analyzing:
            messagebox.showwarning("警告", "正在分析中，请稍候...")
            return
        
        self.is_analyzing = True
        self.analyze_btn.config(state='disabled')
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))
        
        thread = threading.Thread(target=self.do_analyze)
        thread.start()
    
    def do_analyze(self):
        try:
            self.status_var.set("正在准备图片数据...")
            self.progress_var.set(10)
            
            # 获取选择的模型
            vision_provider = self.get_selected_vision_provider()
            text_provider = self.get_selected_text_provider()
            
            # 设置API Key
            api_key = self.api_key_var.get()
            if vision_provider:
                self.model_manager.set_api_key(vision_provider, api_key)
            if text_provider:
                self.model_manager.set_api_key(text_provider, api_key)
            
            # 转换为BGR格式用于编码
            start_img_bgr = cv2.cvtColor(self.start_img_data, cv2.COLOR_RGB2BGR)
            end_img_bgr = cv2.cvtColor(self.end_img_data, cv2.COLOR_RGB2BGR)
            
            start_base64 = self.encode_image_to_base64(start_img_bgr)
            end_base64 = self.encode_image_to_base64(end_img_bgr)
            
            self.status_var.set("正在分析第一张图片...")
            self.progress_var.set(20)
            
            prompt = """请详细分析这张图片，提取以下信息：
1. 场景描述：图片中的整体场景、环境
2. 主体对象：图片中的主要物体、人物、元素
3. 视觉特征：颜色、光线、氛围、风格
4. 空间布局：物体的位置关系、前景背景
5. 其他重要信息：任何有助于视频过渡的细节

请用简洁但全面的中文描述这些信息。"""
            
            # 使用视觉模型分析起始图片
            if vision_provider:
                self.start_image_info = self.model_manager.vision_completion(vision_provider, prompt, start_base64)
            else:
                self.start_image_info = "未能分析图片"
            
            self.status_var.set("正在分析第二张图片...")
            self.progress_var.set(50)
            
            # 使用视觉模型分析结束图片
            if vision_provider:
                self.end_image_info = self.model_manager.vision_completion(vision_provider, prompt, end_base64)
            else:
                self.end_image_info = "未能分析图片"
            
            self.status_var.set("正在生成过渡提示词...")
            self.progress_var.set(70)
            
            transition_requirement = self.requirement_text.get("1.0", tk.END).strip()
            
            # 使用文本模型生成提示词
            if text_provider:
                self.ai_prompt = self.generate_transition_prompt(text_provider, self.start_image_info, self.end_image_info, transition_requirement)
            else:
                self.ai_prompt = json.dumps({
                    "transition_type": "morph",
                    "easing": "ease_in_out",
                    "duration": 5,
                    "description": transition_requirement,
                    "key_effects": ["平滑过渡", "颜色渐变"],
                    "emphasis": "自然流畅"
                }, ensure_ascii=False, indent=2)
            
            self.root.after(0, lambda: self.ai_prompt_text.delete("1.0", tk.END))
            self.root.after(0, lambda: self.ai_prompt_text.insert(tk.END, self.ai_prompt))
            
            self.progress_var.set(100)
            self.status_var.set("AI分析完成！")
            messagebox.showinfo("成功", "AI分析完成！已生成过渡提示词，可以生成视频了。")
            
        except Exception as e:
            import traceback
            error_msg = f"分析失败: {str(e)}\n\n{traceback.format_exc()}"
            print(error_msg)
            messagebox.showerror("错误", f"分析失败: {str(e)}")
        finally:
            self.is_analyzing = False
            self.analyze_btn.config(state='normal')
            self.progress_bar.pack_forget()
    
    def generate_transition_prompt(self, provider_id, start_info, end_info, user_requirement):
        prompt = f"""你是一个专业的视频过渡效果设计师。请根据以下信息，生成一个详细的视频过渡提示词。

【起始图片分析】：
{start_info}

【结束图片分析】：
{end_info}

【用户转换要求】：
{user_requirement}

请生成一个详细的JSON格式提示词，包含以下字段：
{{
    "transition_type": "过渡类型（morph/flow/blend）",
    "easing": "缓动曲线（linear/ease_in/ease_out/ease_in_out）",
    "duration": 建议时长（秒）,
    "description": "详细的过渡效果描述",
    "key_effects": ["关键效果1", "关键效果2", "关键效果3"],
    "emphasis": "需要特别强调的效果"
}}

请直接返回JSON格式，不要包含其他文字。"""
        
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        return self.model_manager.chat_completion(provider_id, messages)
    
    def generate_video(self):
        if not self.start_image or not self.end_image:
            messagebox.showwarning("警告", "请先选择起始图片和结束图片")
            return
        if not self.output_dir:
            messagebox.showwarning("警告", "请先选择输出目录")
            return
        
        ai_prompt_content = self.ai_prompt_text.get("1.0", tk.END).strip()
        if ai_prompt_content:
            try:
                ai_params = json.loads(ai_prompt_content)
                if "transition_type" in ai_params:
                    self.transition_mode.set(ai_params["transition_type"])
                if "easing" in ai_params:
                    self.easing_var.set(ai_params["easing"])
                if "duration" in ai_params:
                    self.duration_var.set(str(ai_params["duration"]))
            except:
                pass
        
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            fps = int(self.fps_var.get())
            duration = float(self.duration_var.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字参数")
            return
        
        if self.is_generating:
            messagebox.showwarning("警告", "正在生成中，请稍候...")
            return
        
        self.is_generating = True
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))
        self.generate_btn.config(state='disabled')
        
        thread = threading.Thread(target=self.do_generate, args=(width, height, fps, duration))
        thread.start()
    
    def do_generate(self, width, height, fps, duration):
        try:
            total_frames = int(fps * duration)
            
            self.status_var.set("正在调整图片尺寸...")
            self.progress_var.set(10)
            
            start_img = cv2.resize(self.start_img_data, (width, height), interpolation=cv2.INTER_AREA)
            end_img = cv2.resize(self.end_img_data, (width, height), interpolation=cv2.INTER_AREA)
            
            start_img = cv2.cvtColor(start_img, cv2.COLOR_RGB2BGR)
            end_img = cv2.cvtColor(end_img, cv2.COLOR_RGB2BGR)
            
            self.status_var.set("正在生成过渡帧...")
            self.progress_var.set(20)
            
            mode = self.transition_mode.get()
            easing = self.easing_var.get()
            
            frames = []
            
            if mode == "morph":
                frames = self.generate_morph_frames(start_img, end_img, total_frames, easing)
            elif mode == "flow":
                frames = self.generate_flow_frames(start_img, end_img, total_frames, easing)
            else:
                frames = self.generate_blend_frames(start_img, end_img, total_frames, easing)
            
            self.status_var.set("正在编码视频...")
            self.progress_var.set(80)
            
            output_path = os.path.join(self.output_dir, "transition_video.mp4")
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            for i, frame in enumerate(frames):
                out.write(frame)
                progress = 80 + (i / len(frames)) * 15
                self.progress_var.set(progress)
            
            out.release()
            
            self.progress_var.set(100)
            self.status_var.set(f"生成完成！视频已保存到: {output_path}")
            messagebox.showinfo("成功", f"过渡视频生成完成！\n\n保存路径: {output_path}\n帧数: {total_frames}\n时长: {duration}秒")
            
        except Exception as e:
            import traceback
            error_msg = f"生成失败: {str(e)}\n\n{traceback.format_exc()}"
            print(error_msg)
            messagebox.showerror("错误", f"生成失败: {str(e)}")
        finally:
            self.is_generating = False
            self.generate_btn.config(state='normal')
            self.progress_bar.pack_forget()
    
    def generate_morph_frames(self, start_img, end_img, total_frames, easing):
        frames = []
        t_values = self.get_easing_values(total_frames, easing)
        
        for i, t in enumerate(t_values):
            frame = cv2.addWeighted(start_img, 1 - t, end_img, t, 0)
            frames.append(frame)
            if i % 10 == 0:
                self.progress_var.set(20 + (i / total_frames) * 60)
        
        return frames
    
    def generate_flow_frames(self, start_img, end_img, total_frames, easing):
        frames = []
        t_values = self.get_easing_values(total_frames, easing)
        
        start_gray = cv2.cvtColor(start_img, cv2.COLOR_BGR2GRAY).astype(np.float32)
        end_gray = cv2.cvtColor(end_img, cv2.COLOR_BGR2GRAY).astype(np.float32)
        
        flow = cv2.calcOpticalFlowFarneback(start_gray, end_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        
        h, w = start_img.shape[:2]
        y_coords, x_coords = np.mgrid[0:h, 0:w]
        
        for i, t in enumerate(t_values):
            flow_map_x = x_coords + flow[..., 0] * t
            flow_map_y = y_coords + flow[..., 1] * t
            
            flow_map_x = np.clip(flow_map_x, 0, w - 1).astype(np.float32)
            flow_map_y = np.clip(flow_map_y, 0, h - 1).astype(np.float32)
            
            warped = cv2.remap(start_img, flow_map_x, flow_map_y, cv2.INTER_LINEAR)
            
            blend = cv2.addWeighted(warped, 1 - t * 0.3, end_img, t * 0.3, 0)
            frames.append(blend)
            
            if i % 10 == 0:
                self.progress_var.set(20 + (i / total_frames) * 60)
        
        return frames
    
    def generate_blend_frames(self, start_img, end_img, total_frames, easing):
        frames = []
        t_values = self.get_easing_values(total_frames, easing)
        
        start_gray = cv2.cvtColor(start_img, cv2.COLOR_BGR2GRAY).astype(np.float32)
        end_gray = cv2.cvtColor(end_img, cv2.COLOR_BGR2GRAY).astype(np.float32)
        
        flow = cv2.calcOpticalFlowFarneback(start_gray, end_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        
        h, w = start_img.shape[:2]
        y_coords, x_coords = np.mgrid[0:h, 0:w]
        
        for i, t in enumerate(t_values):
            flow_map_x = x_coords + flow[..., 0] * t
            flow_map_y = y_coords + flow[..., 1] * t
            
            flow_map_x = np.clip(flow_map_x, 0, w - 1).astype(np.float32)
            flow_map_y = np.clip(flow_map_y, 0, h - 1).astype(np.float32)
            
            warped = cv2.remap(start_img, flow_map_x, flow_map_y, cv2.INTER_LINEAR)
            
            morph_frame = cv2.addWeighted(start_img, 1 - t, end_img, t, 0)
            flow_frame = cv2.addWeighted(warped, 1 - t * 0.5, end_img, t * 0.5, 0)
            
            blend_weight = abs(t - 0.5) * 2
            final_frame = cv2.addWeighted(morph_frame, 1 - blend_weight, flow_frame, blend_weight, 0)
            frames.append(final_frame)
            
            if i % 10 == 0:
                self.progress_var.set(20 + (i / total_frames) * 60)
        
        return frames
    
    def get_easing_values(self, total_frames, easing_type):
        t_linear = np.linspace(0, 1, total_frames)
        
        if easing_type == "linear":
            return t_linear
        elif easing_type == "ease_in":
            return t_linear ** 2
        elif easing_type == "ease_out":
            return 1 - (1 - t_linear) ** 2
        elif easing_type == "ease_in_out":
            return np.where(t_linear < 0.5, 2 * t_linear ** 2, 1 - 2 * (1 - t_linear) ** 2)
        return t_linear

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoTransitionGenerator(root)
    root.mainloop()
