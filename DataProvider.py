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
        
    def create_packet(self, machine_id, sequence):
     return {
        "uuid": str(uuid.uuid4()),
        "sequence": sequence,  # 이 부분을 추가해야 서버에서 번호를 확인할 수 있습니다!
        "timestamp": time.time(),
        "machine_id": machine_id, # 어떤 머신인지 식별하기 위해 추가
        "type": "ALARM" if machine_id % 10 == 0 else "NORMAL",
        "size_kb": self.size_kb,
        "payload": self.dummy_payload
     }
       
    
    
        
    def stream_data(self, total_count):
        for i in range(total_count):
            yield self.create_packet(machine_id = i, sequence = i) # 하나씩 만들때마다 쏨