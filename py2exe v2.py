import wx
import subprocess
import os
import threading
import time

class PyToExeConverter(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Python to EXE Converter", size=(600, 400))
        #self.SetIcon(wx.Icon("py2exe.ico", wx.BITMAP_TYPE_ICO))  # ← Add this line
        panel = wx.Panel(self)
        self.defult_taget_path=os.path.join(os.path.expanduser("~"), "Desktop")

        self.py_path = wx.TextCtrl(panel, style=wx.TE_READONLY)
        browse_py_btn = wx.Button(panel, label="Browse .py")
        self.icon_path = wx.TextCtrl(panel, style=wx.TE_READONLY)
        browse_icon_btn = wx.Button(panel, label="Browse .ico")
        self.dest_path = wx.TextCtrl(panel, style=wx.TE_READONLY)
        self.dest_path.SetValue(self.defult_taget_path)
        browse_dest_btn = wx.Button(panel, label="Select Destination")
        self.onefile_cb = wx.CheckBox(panel, label="Bundle into one file (--onefile)")
        self.auto_open_cb = wx.CheckBox(panel, label="Auto-open output folder")
        self.noconsole_cb = wx.CheckBox(panel, label="Hide console window (--noconsole)")
        self.cleanup_cb = wx.CheckBox(panel, label="Remove build folder after build")
        convert_btn = wx.Button(panel, label="Convert to EXE")
        self.output = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.progress = wx.Gauge(panel, range=100, style=wx.GA_HORIZONTAL)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        for label, ctrl, btn in [
            ("Python File:", self.py_path, browse_py_btn),
            ("Icon File (.ico):", self.icon_path, browse_icon_btn),
            ("Destination Folder:", self.dest_path, browse_dest_btn)
        ]:
            row = wx.BoxSizer(wx.HORIZONTAL)
            row.Add(ctrl, proportion=1, flag=wx.EXPAND | wx.RIGHT, border=10)  # ← proportion changed to 1
            row.Add(btn, proportion=0, flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border=5)
            sizer.Add(row, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=5)

        sizer.Add(self.onefile_cb, flag=wx.LEFT | wx.TOP, border=5)
        sizer.Add(self.auto_open_cb, flag=wx.LEFT | wx.TOP, border=5)
        sizer.Add(self.noconsole_cb, flag=wx.LEFT | wx.TOP, border=5)
        sizer.Add(self.cleanup_cb, flag=wx.LEFT | wx.TOP, border=5)
        sizer.Add(convert_btn, flag=wx.ALL | wx.ALIGN_CENTER, border=5)
        sizer.Add(self.progress, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)
        sizer.Add(self.output, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        
        panel.SetSizer(sizer)

        # Events
        browse_py_btn.Bind(wx.EVT_BUTTON, self.on_browse_py)
        browse_icon_btn.Bind(wx.EVT_BUTTON, self.on_browse_icon)
        browse_dest_btn.Bind(wx.EVT_BUTTON, self.on_browse_dest)
        
        convert_btn.Bind(wx.EVT_BUTTON, self.on_convert)

    def on_browse_py(self, event):
        with wx.FileDialog(self, "Select Python file", wildcard="Python files (*.py)|*.py",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.py_path.SetValue(dlg.GetPath())

    def on_browse_icon(self, event):
        with wx.FileDialog(self, "Select Icon file", wildcard="Icon files (*.ico)|*.ico|(*.png)|*.png",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.icon_path.SetValue(dlg.GetPath())

    def on_browse_dest(self, event):
        with wx.DirDialog(self, "Select Destination Folder", style=wx.DD_DEFAULT_STYLE) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.dest_path.SetValue(dlg.GetPath())

    def on_convert(self, event):
        py_file = self.py_path.GetValue()
        icon_file = self.icon_path.GetValue()
        dest_folder = self.dest_path.GetValue()
        onefile = self.onefile_cb.GetValue()
        auto_open = self.auto_open_cb.GetValue()
        noconsole = self.noconsole_cb.GetValue()
        cleanup = self.cleanup_cb.GetValue()

        if not py_file or not dest_folder:
            self.output.SetValue("Please select both Python file and destination folder.")
            return

        cmd = ["pyinstaller"]
        if onefile:
            cmd.append("--onefile")
        if noconsole:
            cmd.append("--noconsole")    
        if icon_file:
            cmd.append(f"--icon={icon_file}")
        cmd.append(f"--distpath={dest_folder}")
        cmd.append(py_file)

        self.output.SetValue("Running: " + " ".join(cmd) + "\n\n")
        self.progress.SetValue(0)

        def run_conversion():
            try:
                with open("conversion_log.txt", "w") as log_file:
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                    for i in range(1, 101):
                        time.sleep(0.05)
                        wx.CallAfter(self.progress.SetValue, i)
                        if process.poll() is not None:
                            break
                    for line in process.stdout:
                        wx.CallAfter(self.output.AppendText, line)
                        log_file.write(line)
                    process.wait()
                    if cleanup:
                        build_dir = "build"
                        if os.path.exists(build_dir):
                            #import shutil
                            try:
                                #shutil.rmtree(build_dir)
                                os.system(f'rmdir /S /Q "{build_dir}"')
                                wx.CallAfter(self.output.AppendText, "\nRemoved build folder.")
                            except Exception as e:
                                wx.CallAfter(self.output.AppendText, f"\nFailed to remove build folder: {e}")
                    wx.CallAfter(self.progress.SetValue, 100)
                    wx.CallAfter(self.output.AppendText, "\nConversion complete.")
                    if auto_open:
                        wx.CallAfter(lambda: os.startfile(dest_folder))
            except Exception as e:
                wx.CallAfter(self.output.AppendText, f"Error: {e}")
                
            

        threading.Thread(target=run_conversion).start()

if __name__ == "__main__":
    app = wx.App(False)
    frame = PyToExeConverter()
    frame.Show()
    app.MainLoop()