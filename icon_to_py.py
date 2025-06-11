with open("icon.ico", "rb") as f:
    with open("icon.py", "w") as f2:
        f2.write("ICONDATA = " + str(f.read()))