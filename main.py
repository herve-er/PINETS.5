import threading
import api


if __name__ == '__main__':
    # Create a thread for the API
    api_thread = threading.Thread(target=api.main)
    # Start the API thread
    api_thread.start()
    # Wait for the API thread to finish
    api_thread.join()


