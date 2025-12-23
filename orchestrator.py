from subprocess import Popen

processes = []
port = 3000  # starting val
id = 1
delay = 150

for i in range(2):
    cmd = [
        "python3",
        "main.py",
        "-i",
        str(id),
        "-d",
        str(delay),
        "-p",
        str(port),
    ]
    p = Popen(cmd)
    processes.append(p)
    port += 1
    id += 1
    delay += 50


for i in processes:
    assert isinstance(i, Popen)

    i.wait()
