from pathlib import Path

from tcp import Socket
from protocol import Protocol
from config import SERVER_HOST, SERVER_PORT

from ._config import AIRPORTS_FILE, ITINERARIES_FILE
from .reader import Reader


class Client:
    def __init__(
        self,
        host: str = SERVER_HOST,
        port: int = SERVER_PORT,
        airports: Path = AIRPORTS_FILE,
        itineraries: Path = ITINERARIES_FILE,
    ):
        self.host = host
        self.port = port
        self.airports = airports
        self.itineraries = itineraries

    def run(self):
        print("client | state | INIT")
        with Socket(self.host, self.port) as sock:
            print("client | connected")
            self.send_airports(sock)
            self.send_itineraries(sock)
            self.recv_results(sock)

    def _send_file(self, sock: Socket, file: Path):
        print(f"client | sending file | {file}")
        count = 0
        with file.open("rt") as f:
            for batch in Reader(f, batch_size=2):
                count += len(batch)
                sock.send(Protocol.serialize_batch(batch))
                if count % 10000 == 0:
                    print(f"client | sent | {count}")
                if count >= 10: # TEMP: cap 10 lines
                    break
            sock.send(Protocol.EOF_MESSAGE)

    def send_airports(self, sock: Socket):
        self._send_file(sock, self.airports)

    def send_itineraries(self, sock: Socket):
        self._send_file(sock, self.itineraries)

    def recv_results(self, sock: Socket):
        print("client | receiving results", flush=True)
        while True:
            try:
                data = Protocol.receive_batch(sock)
            except TimeoutError:
                print("client | timeout")
                continue
            if data is None:
                break
            for result in data:
                print(result)
