import os
import subprocess
import platform
import shutil
import time

def ppt_to_pptx_soffice(src_path: str) -> str:
    """Convert .ppt → .pptx using LibreOffice CLI."""
    if not src_path.lower().endswith(".ppt"):
        return src_path

    src_path = os.path.normpath(os.path.abspath(src_path))
    dst_path = os.path.splitext(src_path)[0] + ".pptx"
    
    if os.path.exists(dst_path):
        return dst_path

    print(f"🔄 Converting {src_path} → {dst_path} using LibreOffice...")
    
    soffice_cmd = get_soffice_command()
    output_dir = os.path.dirname(dst_path)
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        cmd = [
            soffice_cmd,
            "--headless",
            "--convert-to", "pptx",
            "--outdir", output_dir,
            src_path,
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=output_dir)
        
        if result.returncode != 0:
            raise RuntimeError(f"LibreOffice conversion failed: {result.stderr}")
        
        time.sleep(1)  # Wait for file system sync
        
        possible_outputs = [
            dst_path,
            os.path.join(output_dir, os.path.basename(dst_path)),
            os.path.join(os.getcwd(), os.path.basename(dst_path)),
        ]
        
        for possible_output in possible_outputs:
            if os.path.exists(possible_output):
                print(f"✅ Found output file at: {possible_output}")
                if possible_output != dst_path:
                    shutil.move(possible_output, dst_path)
                return dst_path
        
        raise RuntimeError(f"Output file not found: {dst_path}")
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("LibreOffice conversion timed out")
    except FileNotFoundError:
        raise RuntimeError(f"LibreOffice executable '{soffice_cmd}' not found")
    except Exception as e:
        raise RuntimeError(f"LibreOffice conversion failed: {e}")

def get_soffice_command():
    """Get the correct LibreOffice command for the current platform."""
    if platform.system() == "Windows":
        possible_paths = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            "soffice.exe",
            "soffice",
        ]
        
        for path in possible_paths:
            if shutil.which(path) or os.path.exists(path):
                return path
        return "soffice"
    else:
        return "soffice"
