import uuid
import random
import time
import uuid

class DataProvider():
    def __init__(self, size_kb):
        # 정확한 바이트 크기 계산: 10KB = 10240 bytes
        self.target_size = size_kb * 1024
        

        self.raw_data = b"a" * (self.target_size - 1) + b"\n" 
        
    def create_packet(self):
        # 이제 딕셔너리가 아닌 순수 바이트 데이터를 반환합니다.
        return self.raw_data
        
    def stream_data(self, total_count):
        for _ in range(total_count):
            yield self.create_packet()