import tkinter
import socket
import threading


class Pixelflut:
    def __init__(self, ip="127.0.0.1", port=1234):
        fenster = tkinter.Tk()
        # TODO add event to kill server thread when closing window

        self.ip = ip
        self.port = port

        self.canvas = tkinter.Canvas(fenster, background="white")
        self.canvas.pack(fill=tkinter.BOTH, expand=1)

        self.init_canvas()

        th = threading.Thread(target=self.run_pixel_server)
        th.start()

        fenster.mainloop()

    def run_pixel_server(self):
        server = PixelServer(self, self.ip, self.port)
        server.start()

    def get_canvas_size(self):
        """Return size of the current canvas in form of (width, height)."""
        # TODO does not change when window size changes
        return (self.canvas.cget("width"),
                self.canvas.cget("height"))

    def draw_pixel(self, x, y):
        # TODO Support for colors
        self.canvas.create_rectangle(x, y, x+1, y+1, fill="black")

    def init_canvas(self):
        t = "Pixelflutserver"
        t += "@" + self.ip + ":" + str(self.port)
        self.canvas.create_text(0, 0, anchor="nw", text=t)


class PixelServer:
    def __init__(self, pixelflut, ip="127.0.0.1", port=1234):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip, port))
        self.client_sock = self.server.listen(100)
        self.pixelflut = pixelflut

    def start(self):
        while True:
            sock, address = self.server.accept()
            self.handle(sock)

    def handle(self, client_sock):
        bytes_request = client_sock.recv(1024)
        command = str(bytes_request, "utf-8")
        print("Command", command)
        if command.lower().startswith("px"):
            try:
                px, x, y = command.split(' ')
                self.pixelflut.draw_pixel(int(x), int(y))
            except Exception as e:
                print("Command Error", command, e)

        elif command.lower() == "size":
            w, h = self.pixelflut.get_canvas_size()
            client_sock.send(bytes(w + "x" + h, "utf-8"))

        client_sock.close()


if __name__ == "__main__":
    import argparse
    d = """
        Pixelflut - A Server, that listens for TCP packets that allow for
        drawing on the screen. Valid content of the packets is \"PX x y\"
        where x and
        y are coordinates on the screen. A pixel will be drawn there. When
        the packet contains \"SIZE\" you will receive the size of the screen
        in the format WIDTHxHEIGHT.
        """
    parser = argparse.ArgumentParser(description=d)
    parser.add_argument("-i", "--ip",
                        help="An IP address the server should be bound to.",
                        dest="ip", default="127.0.0.1")
    parser.add_argument("-p", "--port",
                        help="The port number to listen to.", type=int,
                        dest="port", default=12345)
    args = parser.parse_args()

    Pixelflut(ip=args.ip, port=args.port)
