import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from setup_rag import RAGSystem
import os

class FAQHandler(FileSystemEventHandler):
    def __init__(self):
        self.rag = RAGSystem()
        self.last_processed = 0
        self.processing_interval = 2  # Minimum seconds between processing

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('education_faq.json'):
            current_time = time.time()
            # Prevent multiple rapid updates
            if current_time - self.last_processed > self.processing_interval:
                print(f"\nDetected change in {event.src_path}")
                self.rag.update_documents(event.src_path)
                self.last_processed = current_time

if __name__ == "__main__":
    # Path to watch
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'documents')
    
    # Create an observer and handler
    event_handler = FAQHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    
    # Start watching
    print(f"Starting to watch {path} for changes...")
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopping file watch...")
    
    observer.join()
