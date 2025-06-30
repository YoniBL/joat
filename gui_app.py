#!/usr/bin/env python3
"""
JOAT - Just One AI Tool (GUI)
Modern Tkinter-based desktop GUI for multi-model AI conversations.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import os
import sys
from datetime import datetime
from ollama_client import OllamaClient
from app import JOATSystem

class ModernChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JOAT - Just One AI Tool")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.joat_system = JOATSystem()
        self.ollama_client = OllamaClient()
        self.message_queue = queue.Queue()
        self.message_row_counter = 0  # Add row counter for grid layout
        self.colors = {
            'bg_primary': '#FAFAFA',
            'bg_secondary': '#F4F1EE',
            'bg_tertiary': '#F4F1EE',
            'accent': '#D4A574',
            'accent_hover': '#C19A6B',
            'text_primary': '#363636',
            'text_secondary': '#363636',
            'text_muted': '#A0A0A0',
            'border': '#E0E0E0',
            'border_dark': '#C0C0C0',
            'user_bubble': '#F9EAE5',
            'assistant_bubble': '#E5D4B1',
            'user_text': '#363636',
            'success': '#8FBC8F',
            'warning': '#D2B48C',
            'error': '#CD5C5C',
            'hover': '#f3f4f6'
        }
        self.root.configure(bg=self.colors['bg_primary'])
        self.current_conversation = None
        self.conversations = []
        self.create_widgets()
        self.setup_bindings()
        self.check_ollama_status()
        self.process_messages()

    def create_widgets(self):
        self.main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.create_sidebar()
        self.create_main_content()

    def create_sidebar(self):
        self.sidebar = tk.Frame(self.main_frame, bg=self.colors['bg_secondary'], width=260)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        sidebar_header = tk.Frame(self.sidebar, bg=self.colors['bg_secondary'], height=60)
        sidebar_header.pack(fill=tk.X)
        sidebar_header.pack_propagate(False)
        new_chat_btn = tk.Button(
            sidebar_header,
            text="+ New Chat",
            command=self.new_conversation,
            font=('SF Pro Display', 13, 'bold'),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            padx=20,
            pady=12,
            cursor='hand2',
            activebackground=self.colors['hover'],
            activeforeground=self.colors['text_primary'],
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['border']
        )
        new_chat_btn.pack(fill=tk.X, padx=16, pady=12)
        status_frame = tk.Frame(self.sidebar, bg=self.colors['bg_secondary'])
        status_frame.pack(fill=tk.X, padx=16, pady=8)
        self.status_indicator = tk.Label(
            status_frame,
            text="●",
            font=('SF Pro Display', 12),
            fg=self.colors['warning'],
            bg=self.colors['bg_secondary']
        )
        self.status_indicator.pack(side=tk.LEFT)
        self.status_text = tk.Label(
            status_frame,
            text="Checking status...",
            font=('SF Pro Display', 11),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary']
        )
        self.status_text.pack(side=tk.LEFT, padx=(8, 0))
        self.model_info = tk.Label(
            status_frame,
            text="",
            font=('SF Pro Display', 10),
            fg=self.colors['text_muted'],
            bg=self.colors['bg_secondary'],
            cursor='arrow'
        )
        self.model_info.pack(side=tk.RIGHT)
        # Always show models mapping below model count
        models_mapping_frame = tk.Frame(self.sidebar, bg=self.colors['bg_secondary'])
        models_mapping_frame.pack(fill=tk.X, padx=16, pady=(0, 8))
        tk.Label(models_mapping_frame, text="Model Mapping", font=('SF Pro Display', 11, 'bold'), fg=self.colors['text_primary'], bg=self.colors['bg_secondary']).pack(anchor=tk.W)
        mapping = self.joat_system.models_mapping
        for task, model in mapping.items():
            tk.Label(models_mapping_frame, text=f"{task}", font=('SF Pro Display', 10), fg=self.colors['text_secondary'], bg=self.colors['bg_secondary']).pack(anchor=tk.W)
            tk.Label(models_mapping_frame, text=f"→ {model}", font=('SF Pro Display', 10, 'bold'), fg=self.colors['accent'], bg=self.colors['bg_secondary']).pack(anchor=tk.W, padx=16)
        separator = tk.Frame(self.sidebar, bg=self.colors['border'], height=1)
        separator.pack(fill=tk.X, padx=16, pady=8)
        conversations_frame = tk.Frame(self.sidebar, bg=self.colors['bg_secondary'])
        conversations_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        conversations_label = tk.Label(
            conversations_frame,
            text="Recent Conversations",
            font=('SF Pro Display', 12, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary']
        )
        conversations_label.pack(anchor=tk.W, padx=8, pady=(0, 8))
        self.conversations_listbox = tk.Listbox(
            conversations_frame,
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            selectbackground=self.colors['accent'],
            selectforeground='white',
            font=('SF Pro Display', 11),
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            activestyle='none'
        )
        self.conversations_listbox.pack(fill=tk.BOTH, expand=True, padx=8)
        self.conversations_listbox.bind('<<ListboxSelect>>', self.on_conversation_select)

    def create_main_content(self):
        self.content_frame = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.create_chat_area()
        self.create_input_area()

    def create_chat_area(self):
        self.chat_frame = tk.Frame(self.content_frame, bg=self.colors['bg_primary'])
        self.chat_frame.pack(fill=tk.BOTH, expand=True)  # Ensure chat area fills all available space
        self.welcome_frame = tk.Frame(self.chat_frame, bg=self.colors['bg_primary'])
        self.welcome_frame.pack(fill=tk.BOTH, expand=True)
        welcome_center = tk.Frame(self.welcome_frame, bg=self.colors['bg_primary'])
        welcome_center.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        welcome_title = tk.Label(
            welcome_center,
            text="JOAT",
            font=('SF Pro Display', 32, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_primary']
        )
        welcome_title.pack()
        welcome_subtitle = tk.Label(
            welcome_center,
            text="Just One AI Tool",
            font=('SF Pro Display', 16),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_primary']
        )
        welcome_subtitle.pack(pady=(0, 20))
        welcome_desc = tk.Label(
            welcome_center,
            text="I can help you with coding, math, writing, and more.\nStart a new conversation to begin.",
            font=('SF Pro Display', 14),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_primary'],
            justify=tk.CENTER
        )
        welcome_desc.pack()
        self.messages_frame = tk.Frame(self.chat_frame, bg=self.colors['bg_primary'])
        self.messages_frame.pack(fill=tk.BOTH, expand=True)  # Ensure messages fill all available space
        messages_container = tk.Frame(self.messages_frame, bg=self.colors['bg_primary'])
        messages_container.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(messages_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.messages_canvas = tk.Canvas(
            messages_container,
            bg=self.colors['bg_primary'],
            yscrollcommand=scrollbar.set,
            highlightthickness=0,
            relief=tk.FLAT
        )
        self.messages_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.messages_canvas.yview)
        self.messages_inner_frame = tk.Frame(self.messages_canvas, bg=self.colors['bg_primary'])
        self.messages_canvas.create_window((0, 0), window=self.messages_inner_frame, anchor=tk.NW)
        self.messages_inner_frame.bind('<Configure>', lambda e: self.messages_canvas.configure(scrollregion=self.messages_canvas.bbox('all')))
        self.messages_canvas.bind('<Configure>', self.on_canvas_configure)
        def _on_mousewheel(event):
            if event.num == 4 or event.delta > 0:
                self.messages_canvas.yview_scroll(-1, 'units')
            elif event.num == 5 or event.delta < 0:
                self.messages_canvas.yview_scroll(1, 'units')
        self.messages_canvas.bind_all('<MouseWheel>', _on_mousewheel)
        self.messages_canvas.bind_all('<Button-4>', _on_mousewheel)
        self.messages_canvas.bind_all('<Button-5>', _on_mousewheel)

    def create_input_area(self):
        input_frame = tk.Frame(self.content_frame, bg=self.colors['bg_primary'])
        input_frame.pack(fill=tk.X)
        input_bg = tk.Frame(input_frame, bg=self.colors['bg_primary'])
        input_bg.pack(fill=tk.X, padx=16, pady=16)
        input_container = tk.Frame(input_bg, bg=self.colors['border'], relief=tk.FLAT, bd=1)
        input_container.pack(fill=tk.X)
        self.input_text = tk.Text(
            input_container,
            height=3,
            wrap=tk.WORD,
            font=('SF Pro Text', 14),
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            borderwidth=0,
            padx=16,
            pady=12,
            insertbackground=self.colors['text_primary']
        )
        self.input_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.send_btn = tk.Button(
            input_container,
            text="→",
            command=self.send_message,
            font=('SF Pro Display', 16, 'bold'),
            bg=self.colors['accent'],
            fg='white',
            relief=tk.FLAT,
            width=3,
            height=1,
            cursor='hand2',
            activebackground=self.colors['accent_hover'],
            activeforeground='white'
        )
        self.send_btn.pack(side=tk.RIGHT, padx=8, pady=8)

    def setup_bindings(self):
        self.input_text.bind('<Return>', self.on_enter_press)
        self.input_text.bind('<Shift-Return>', self.on_shift_enter_press)
        self.input_text.focus()

    def on_enter_press(self, event):
        if not event.state & 0x1:
            self.send_message()
            return 'break'

    def on_shift_enter_press(self, event):
        return None

    def on_canvas_configure(self, event):
        self.messages_canvas.itemconfig(self.messages_canvas.find_withtag('window')[0], width=event.width)

    def new_conversation(self):
        conversation_id = len(self.conversations) + 1
        conversation = {
            'id': conversation_id,
            'title': f"New Chat {conversation_id}",
            'messages': [],
            'created_at': datetime.now()
        }
        self.conversations.append(conversation)
        self.current_conversation = conversation
        self.update_conversations_list()
        self.show_messages_view()
        self.input_text.delete(1.0, tk.END)
        self.input_text.focus()

    def update_conversations_list(self):
        self.conversations_listbox.delete(0, tk.END)
        for conv in self.conversations:
            self.conversations_listbox.insert(tk.END, conv['title'])

    def on_conversation_select(self, event):
        selection = self.conversations_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.conversations):
                self.current_conversation = self.conversations[index]
                self.show_messages_view()
                self.display_conversation_messages()

    def show_messages_view(self):
        if self.welcome_frame.winfo_ismapped():
            self.welcome_frame.pack_forget()
        if not self.messages_frame.winfo_ismapped():
            self.messages_frame.pack(fill=tk.BOTH, expand=True)

    def display_conversation_messages(self):
        # Clear all widgets from the messages frame
        for widget in self.messages_inner_frame.winfo_children():
            widget.destroy()
        
        # Reset grid configuration and row counter
        self.messages_inner_frame.grid_columnconfigure(0, weight=0)
        self.messages_inner_frame.grid_columnconfigure(1, weight=0)
        self.message_row_counter = 0
        
        # Redisplay all messages
        for message in self.current_conversation['messages']:
            self.add_message_display(message['role'], message['content'])

    def add_message_display(self, role, content):
        current_row = self.message_row_counter
        # Create a message_frame with two columns: left spacer and content
        message_frame = tk.Frame(self.messages_inner_frame, bg=self.colors['bg_primary'])
        message_frame.grid(row=current_row, column=0, sticky='ew', padx=0, pady=0)
        message_frame.grid_columnconfigure(0, weight=1)  # Left spacer expands
        message_frame.grid_columnconfigure(1, weight=0)  # Content does not expand

        # Avatar and bubble always in column 1 (right side)
        avatar_frame = tk.Frame(message_frame, bg=self.colors['bg_primary'])
        avatar_frame.grid(row=0, column=1, padx=(8, 16), pady=8, sticky='e')
        if role == 'user':
            avatar = tk.Label(
                avatar_frame,
                text="U",
                font=('SF Pro Display', 12, 'bold'),
                bg=self.colors['user_bubble'],
                fg=self.colors['user_text'],
                width=2,
                height=1,
                relief=tk.FLAT
            )
            bubble = self.create_rounded_bubble(message_frame, content, self.colors['user_bubble'], self.colors['user_text'], 'e', 'user')
            # Add extra left and top margin for user bubble
            bubble.grid(row=0, column=1, padx=(20, 8), pady=(16, 8), sticky='e')
        else:
            avatar = tk.Label(
                avatar_frame,
                text="J",
                font=('SF Pro Display', 12, 'bold'),
                bg=self.colors['text_secondary'],
                fg='white',
                width=2,
                height=1,
                relief=tk.FLAT
            )
            bubble = self.create_rounded_bubble(message_frame, content, self.colors['assistant_bubble'], self.colors['text_primary'], 'e', 'assistant')
            bubble.grid(row=0, column=1, padx=(8, 8), pady=8, sticky='e')
        avatar.pack()
        self.message_row_counter += 1
        self.messages_canvas.update_idletasks()
        self.messages_canvas.configure(scrollregion=self.messages_canvas.bbox('all'))
        self.messages_canvas.yview_moveto(1.0)


    def create_rounded_bubble(self, parent, text, bg, fg, anchor, role):
        font = ('SF Pro Text', 14)
        temp_canvas = tk.Canvas(parent)
        text_id = temp_canvas.create_text(0, 0, text=text, font=font, anchor='nw', width=600)
        bbox = temp_canvas.bbox(text_id)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        if role == 'user':
            padding_x = 12
            padding_y = 6
            width = text_width + 2 * padding_x
            height = text_height + 2 * padding_y
            if width > 2 * height:
                radius = height // 2
            else:
                radius = 14
        else:
            padding_x = 24
            padding_y = 12
            width = text_width + 2 * padding_x
            height = text_height + 2 * padding_y
            radius = 18
        temp_canvas.destroy()
        bubble_canvas = tk.Canvas(parent, bg=self.colors['bg_primary'], highlightthickness=0, bd=0, width=width, height=height)
        def draw_rounded_rect(canvas, x1, y1, x2, y2, r, **kwargs):
            canvas.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, style='pieslice', **kwargs)
            canvas.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, style='pieslice', **kwargs)
            canvas.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, style='pieslice', **kwargs)
            canvas.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, style='pieslice', **kwargs)
            canvas.create_rectangle(x1+r, y1, x2-r, y2, **kwargs)
            canvas.create_rectangle(x1, y1+r, x2, y2-r, **kwargs)
        draw_rounded_rect(bubble_canvas, 0.5, 0.5, width-0.5, height-0.5, radius, fill=bg, outline=bg)
        bubble_canvas.create_text(width//2, height//2, text=text, font=font, fill=fg, anchor='center', width=text_width)
        return bubble_canvas

    def send_message(self):
        message = self.input_text.get(1.0, tk.END).strip()
        if not message:
            return
        if not self.current_conversation:
            conversation_id = len(self.conversations) + 1
            conversation = {
                'id': conversation_id,
                'title': '',
                'messages': [],
                'created_at': datetime.now()
            }
            self.conversations.append(conversation)
            self.current_conversation = conversation
            self.update_conversations_list()
        self.input_text.delete(1.0, tk.END)
        self.current_conversation['messages'].append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now()
        })
        if len(self.current_conversation['messages']) == 1:
            self.current_conversation['title'] = message[:30] + "..." if len(message) > 30 else message
            self.update_conversations_list()
        self.add_message_display('user', message)
        self.show_messages_view()
        self.send_btn.config(state=tk.DISABLED, text="...")
        
        target_conversation = self.current_conversation
        history = [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in target_conversation['messages'][:-1]
        ]

        def process_message():
            try:
                response_data = self.joat_system.process_query(message, history)
                self.message_queue.put(('response', (response_data, target_conversation)))
            except Exception as e:
                self.message_queue.put(('error', (str(e), target_conversation)))
        threading.Thread(target=process_message, daemon=True).start()

    def check_ollama_status(self):
        def check():
            try:
                is_running = self.ollama_client.is_ollama_running()
                models = self.ollama_client.get_available_models()
                self.message_queue.put(('status', {
                    'running': is_running,
                    'models': models
                }))
            except Exception as e:
                self.message_queue.put(('status', {
                    'running': False,
                    'models': [],
                    'error': str(e)
                }))
        threading.Thread(target=check, daemon=True).start()

    def update_status(self, status_data):
        if status_data.get('running'):
            self.status_indicator.config(fg=self.colors['success'])
            self.status_text.config(text="Ollama is running")
        else:
            self.status_indicator.config(fg=self.colors['error'])
            self.status_text.config(text="Ollama is not running")
        models = status_data.get('models', [])
        if models:
            self.model_info.config(text=f"{len(models)} models")
        else:
            self.model_info.config(text="No models")

    def process_messages(self):
        try:
            while True:
                msg_type, data = self.message_queue.get_nowait()
                if msg_type == 'status':
                    self.update_status(data)
                elif msg_type == 'response':
                    response_data, conversation = data
                    response_content = response_data['response']
                    if conversation:
                        conversation['messages'].append({
                            'role': 'assistant',
                            'content': response_content,
                            'timestamp': datetime.now()
                        })
                        if conversation == self.current_conversation:
                            self.add_message_display('assistant', response_content)
                            self.show_messages_view()
                elif msg_type == 'error':
                    error_content, conversation = data
                    if conversation:
                        error_msg = f"Error: {error_content}"
                        conversation['messages'].append({
                            'role': 'assistant',
                            'content': error_msg,
                            'timestamp': datetime.now()
                        })
                        if conversation == self.current_conversation:
                            self.add_message_display('assistant', error_msg)
                            self.show_messages_view()
                self.send_btn.config(state=tk.NORMAL, text="→")
        except queue.Empty:
            pass
        self.root.after(100, self.process_messages)

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernChatApp(root)
    root.mainloop()