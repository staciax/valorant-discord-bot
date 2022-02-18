import os
import time
import subprocess

def ptime():
  x = time.localtime()
  z = []
  for i in x:
    z.append(str(i))
  z = f"{z[0]} {z[1]}/{z[2]} {z[3]}:{z[4]}:{z[5]}"
  return z

def imports():
    x = subprocess.check_output("python3 --version",shell=True) # check if compatible
    try:
        x = x.split(" ")
        y = x[1].split(".")
        if int(y[1]) >= 6:
          os.system("python3 -m pip install poetry")
          os.system("python3 -m poetry install")
        else:
            print("Please update python3 to 3.6+")
    except Exception as err:
        str(err)
        os.system("python -m pip install poetry")
        os.system("python -m poetry install")
    finally:
        with open(f"log.txt","w") as fp:
          fp.write(f"[{ptime()}] Finished Install Packages and created setup_done.yay file.\n")

if __name__ == "__main__":
    my_file = os.path.exists(f"setup_done.yay")
    if my_file:
        print("Packages Already Imported, Exiting!")
    else:
        imports()
    with open("setup_done.yay","w") as file:
        pass