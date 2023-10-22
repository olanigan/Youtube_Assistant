import time
import subprocess
import os

def logtime(func):
  """
  Decorator to log the execution time of a function.

  Args:
    func: The function to decorate.

  Returns:
    A decorated function that logs its execution time.
  """

  def wrapper(*args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    execution_time = end_time - start_time
    minutes, seconds = divmod(execution_time, 60)
    print(f"Function {func.__name__} executed in {minutes:.0f} minutes and {seconds:.3f} seconds.")
    return result

  return wrapper


# Helper function for printing docs
def get_metadata(info):
    return f"{info['source'].replace('docs/','')}, Page {info['page']}"

def pretty_print_docs(docs):
    return f"\n{'-' * 100}\n".join([f"Source {i+1}: " + get_metadata(d.metadata) + ":\n\n" + d.page_content for i, d in enumerate(docs)])

def load_ffmpeg():
    # Check if ffmpeg is installed
    exist = subprocess.run(["which", "ffmpeg"], capture_output=True).stdout.decode("utf-8").strip()
    if not exist:
        # Download and install ffmpeg
        subprocess.run(["curl", "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz", "-o", "ffmpeg.tar.xz"], capture_output=True)
        subprocess.run(["tar", "-xf", "ffmpeg.tar.xz"])
        subprocess.run(["rm", "ffmpeg.tar.xz"])

        # Get the path to ffmpeg
        ffmdir = subprocess.run(["find", ".", "-iname", "ffmpeg-*-static"], capture_output=True).stdout.decode("utf-8").strip()

        # Add the path to ffmpeg to the PATH environment variable
        path = os.environ["PATH"]
        path += ":" + ffmdir
        os.environ["PATH"] = path

    print()
    # Check if ffmpeg is now installed
    exist = subprocess.run(["which", "ffmpeg"], capture_output=True).stdout.decode("utf-8").strip()
    print(exist)
    print("Done!")
