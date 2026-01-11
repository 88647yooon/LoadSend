import time

class SimulationManager:
    def __init__(self, dispatcher, tps):
        self.dispatcher = dispatcher
        self.tps = tps
        self.interval = 1.0 / tps 
        self.start_time = 0
        self.end_time = 0

    def start(self, provider, total_count):
        print(f"실험 시작 (Total: {total_count}, TPS: {self.tps})")
        self.start_time = time.time()
        
        try:
            for packet in provider.stream_data(total_count):
                
                self.dispatcher.dispatch(packet)
                
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\n사용자에 의해 실험 중단")
        finally:
            self.end_time = time.time()
            # 💡 중요: 실험 종료 후 열려있는 모든 소켓을 닫습니다.
            self.dispatcher.close()
            self.report(total_count)

    def report(self, total_count):
        duration = (self.end_time - self.start_time)
        print("\n" + "="*40)
        print(" 실험 결과 리포트")
        print(f" 총 소요 시간: {duration:.2f} 초")
        print(f" 실제 평균 TPS: {total_count / duration:.2f}")
        print(f"패킷당 평균 지연: {(duration / total_count) * 1000:.4f} ms")
        print("="*40)