"""Drive one Suno Studio upload end-to-end: file -> 'Full Song' tag -> Continue
-> accept AI description -> Continue. Polls for each dialog button via cdp_eval.

Usage: python3 stage_upload.py /abs/path/to/file.mp3
"""
import subprocess
import sys
import time
from pathlib import Path

SCRIPTS = Path.home() / "claude/computer_control/scripts"
URLPAT = "https://suno.com/studio*"
SEL = 'input[accept*="audio/wav"]'


def cdp(js):
    r = subprocess.run(["python3", str(SCRIPTS / "cdp_eval.py"), URLPAT, js],
                       capture_output=True, text=True)
    return r.stdout.strip()


def set_file(path):
    subprocess.run(["python3", str(SCRIPTS / "cdp_set_file.py"), URLPAT, SEL, path],
                   capture_output=True, text=True)


def click_text(pattern, only_visible=True):
    js = f"""
    (() => {{
      const re=/{pattern}/i;
      const els=[...document.querySelectorAll('button,[role=button],label,[role=checkbox],div,span')]
        .filter(e=>e.offsetParent!==null);
      const t=els.find(e=>re.test((e.innerText||e.textContent||'').trim()) &&
                          (e.innerText||e.textContent||'').trim().length<24);
      if(t){{ (t.closest('button,label,[role=checkbox]')||t).click(); return 'clicked'; }}
      return 'none';
    }})()"""
    return cdp(js)


def dialog_state():
    return cdp("document.body.innerText.match(/Identify audio content|Describe Your Audio/i)?.[0]||'no-dialog'")


def main():
    path = sys.argv[1]
    name = Path(path).name
    print(f"[{name}] uploading file…")
    set_file(path)
    # step 1: wait for 'Identify audio content', tag Full Song, Continue
    for _ in range(15):
        time.sleep(1)
        if "Identify" in dialog_state():
            break
    print("  tag:", click_text("Full Song"))
    time.sleep(1.5)  # let checkbox state register before Continue
    # click Continue repeatedly until both dialog steps clear
    for i in range(20):
        s = dialog_state()
        if "no-dialog" in s:
            print(f"  [{name}] done — in library")
            return
        click_text("Continue")
        time.sleep(2)
    print(f"  [{name}] dialog still open:", dialog_state())


if __name__ == "__main__":
    main()
