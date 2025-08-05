import os
import subprocess
import platform
import shutil
import time


def ppt_to_pptx_soffice(src_path: str) -> str:
    """
    Convert .ppt → .pptx using LibreOffice CLI.
    Returns the .pptx path (existing or newly created).
    """
    if not src_path.lower().endswith(".ppt"):
        return src_path

    # Normalize paths for Windows
    src_path = os.path.normpath(os.path.abspath(src_path))
    dst_path = os.path.splitext(src_path)[0] + ".pptx"
    
    if os.path.exists(dst_path):
        return dst_path

    print(f"🔄 Converting {src_path} → {dst_path} using LibreOffice...")
    
    # Get the correct LibreOffice executable
    soffice_cmd = get_soffice_command()
    
    # Use absolute paths and ensure output directory exists
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
        print(f"Source file exists: {os.path.exists(src_path)}")
        print(f"Output directory: {output_dir}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=output_dir)
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
        if result.returncode != 0:
            raise RuntimeError(f"LibreOffice conversion failed with return code {result.returncode}. "
                             f"STDOUT: {result.stdout}, STDERR: {result.stderr}")
        
        # Wait a bit for file system to sync
        time.sleep(1)
        
        # Check multiple possible output locations
        possible_outputs = [
            dst_path,
            os.path.join(output_dir, os.path.basename(dst_path)),
            os.path.join(os.getcwd(), os.path.basename(dst_path)),
        ]
        
        for possible_output in possible_outputs:
            if os.path.exists(possible_output):
                print(f"✅ Found output file at: {possible_output}")
                # Move to expected location if necessary
                if possible_output != dst_path:
                    shutil.move(possible_output, dst_path)
                return dst_path
        
        # List files in output directory for debugging
        print(f"Files in output directory: {os.listdir(output_dir)}")
        raise RuntimeError(f"LibreOffice conversion completed but output file was not found. "
                          f"Expected: {dst_path}")
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("LibreOffice conversion timed out after 5 minutes")
    except FileNotFoundError:
        raise RuntimeError(f"LibreOffice executable '{soffice_cmd}' not found.")
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
