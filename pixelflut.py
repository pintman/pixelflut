"""Pixelflut is a TCP server screen inspired by the pixelflut project of the CCC
Göttingen (https://cccgoe.de/wiki/Pixelflut). It uses the core python
libraries and will not rely on other libraries.

There is a server and a client component in this package. The server listens for packages
with commands as content. The following commands are recognized:

SIZE - will respond with the actual size of the screen in the format WIDTHxHEIGHT

PX x y on_off - will draw (on_off=1) or clear (on_off=0) the pixel at (x|y).

"""

import tkinter
import socket
import threading


class Pixelflut:
    """A canvas that shows the screen which can be used by clients to print or clear 
    pixels on.
    """

    def __init__(self, ip="127.0.0.1", port=1234):
        fenster = tkinter.Tk()
        # TODO add event to kill server thread when closing window

        self.ip = ip
        self.port = port
        self.coord2rectangle = dict()

        self.canvas = tkinter.Canvas(fenster, background="white")
        self.canvas.pack(fill=tkinter.BOTH, expand=1)

        self.__init_canvas()

        th = threading.Thread(target=self.__run_pixel_server)
        th.start()

        fenster.mainloop()

    def __run_pixel_server(self):
        server = PixelServer(self, self.ip, self.port)
        server.start()

    def get_canvas_size(self):
        """Return size of the current canvas in form of (width, height)."""
        return (self.canvas.winfo_width(),
                self.canvas.winfo_height())

    def draw_pixel(self, x, y):
        """Draw a black pixel at (x|y)."""
        # TODO Support for colors
        if (x, y) not in self.coord2rectangle:
            r = self.canvas.create_rectangle(x, y, x+1, y+1, fill="black")
            self.coord2rectangle[(x,y)] = r

    def clear_pixel(self, x, y):
        """Remove the pixel at (x|y) from the screen."""
        if (x, y) in self.coord2rectangle:
            self.canvas.delete(self.coord2rectangle[(x, y)])
            del(self.coord2rectangle[(x, y)])

    def __init_canvas(self):
        t = "Pixelflutserver"
        t += "@" + self.ip + ":" + str(self.port)
        self.canvas.create_text(10, 0, anchor="nw", text=t)


class PixelServer:
    def __init__(self, pixelflut, ip="127.0.0.1", port=1234):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip, port))
        self.client_sock = self.server.listen(100)
        self.pixelflut = pixelflut

    def start(self):
        """Start server. This method does not return."""
        while True:
            sock, _address = self.server.accept()
            # TODO only call handle if window is visible - call for window state
            #th = threading.Thread(target=self.__handle, args=(sock,))
            #th.start()
            self.__handle(sock)

    def __handle(self, client_sock):
        bytes_request = client_sock.recv(1024)
        command = str(bytes_request, "utf-8")
        print("Command:", command)
        if command.lower().startswith("px"):
            try:
                _px, x, y, on_off = command.split(' ')
                if on_off == "1":
                    self.pixelflut.draw_pixel(int(x), int(y))
                elif on_off == "0":
                    self.pixelflut.clear_pixel(int(x), int(y))
            except Exception as e:
                print("Command Error", command, e)

        elif command.lower() == "size":
            w, h = self.pixelflut.get_canvas_size()
            client_sock.send(bytes(str(w) + "x" + str(h), "utf-8"))

        client_sock.close()


class PixelClient:
    def __init__(self, ip="127.0.0.1", port=1234):
        self.ip = ip
        self.port = port

    def px(self, x, y, on_off):
        """Send the PX-Command to the server. This will draw or clear the 
        pixel at (x|y)."""

        cmd = "PX {x} {y} {on_off}".format(x=x, y=y, on_off=on_off)
        cmd = bytes(cmd, "utf-8")
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.ip, self.port))
        client.send(cmd)
        client.close()


def __run_client(ip, port):
    print("Connecting to {ip}:{po}.".format(ip=ip, po=port))
    user_input = ""
    cl = PixelClient(ip=ip, port=port)
    while user_input != "n":
        x = int(input("x="))
        y = int(input("y="))
        on_off = int(input("on_off (1,0)="))
        cl.px(x, y, on_off)
        user_input = input("Again? (y/n)")


def __main():
    d = """
        Pixelflut - A Server, that listens for TCP packets that allow for
        drawing on the screen. Valid content of the packets is \"PX x y on_off\"
        where x and
        y are coordinates on the screen and on_off is either 1 or 0.
        A pixel will be drawn there if on_off is 1 - otherwise it will be
        cleared. When
        the packet contains \"SIZE\" you will receive the size of the screen
        in the format WIDTHxHEIGHT. There is a simple client that can be used as well.
        """
    parser = argparse.ArgumentParser(description=d)
    parser.add_argument("-s", "--server", action="store_const", const=True,
                        help="Start server.")
    parser.add_argument("-c", "--client", action="store_const", const=True,
                        help="Start client.")
    parser.add_argument("-i", "--ip",
                        help="An IP address the client or server should be bound to.",
                        dest="ip", default="127.0.0.1")
    parser.add_argument("-p", "--port",
                        help="The port number to listen or to connect to.", type=int,
                        dest="port", default=1234)
    args = parser.parse_args()
    if args.client:
        __run_client(args.ip, args.port)

    elif args.server:
        Pixelflut(ip=args.ip, port=args.port)


if __name__ == "__main__":
    import argparse
    __main()
