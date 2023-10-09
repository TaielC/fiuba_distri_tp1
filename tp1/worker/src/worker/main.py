"""Worker main."""

from .worker_factory import WorkerFactory


def main():
    worker = WorkerFactory.create_worker()
    worker.run()


if __name__ == "__main__":
    main()
