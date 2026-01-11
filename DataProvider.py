import uuid
import random
import time
import uuid
# 트래픽을 생성만 하는 책임을 가지는 클래스
class DataProvider():
    def __init__(self, size_kb=1):
        
        self.size_kb = size_kb
        padding_size = max(0, (size_kb * 1024) - 200)
        self.dummy_payload = "a" * padding_size
        self.machine_id = 0
        
    def create_packet(self, machine_id):
    
     return {
    
            "uuid": str(uuid.uuid4()),
            "timestamp": time.time(),
            "type": "ALARM" if machine_id % 10 == 0 else "NORMAL",
            "size_kb": self.size_kb,
            "payload": self.dummy_payload  # 실제 용량을 차지하는 부분
        }
       
    
    
        
    def stream_data(self, total_count):
        for i in range(total_count):
            yield self.create_packet(i) # 하나씩 만들때마다 쏨