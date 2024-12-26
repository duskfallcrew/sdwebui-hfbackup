from modules import scripts
from scripts import hfbackup_script

class Script(scripts.Script):
  def title(self):
    return "Huggingface Backup"

  def show(self, is_img2img):
    return scripts.AlwaysVisible

  def ui(self, is_img2img):
    return hfbackup_script.on_ui(self)

  def run(self, p, *args):
    return hfbackup_script.on_run(self, p, *args)
  
  def on_script_load(self):
     return hfbackup_script.on_script_load(self)
