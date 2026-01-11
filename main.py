from DataProvider import DataProvider
from PacketSender import NetworkLoadBalancer
from SimulationManager import SimulationManager


# 받는 쪽 기기(윈도우/데스크탑)의 IP 주소들
ASUS_IP = "192.168.0.53"
DESKTOP_IP = "192.168.0.141" # 윈도우 노트북 IP " # 데스크탑 IP
PORT = 5000

# 실험 파라미터
TOTAL_PACKETS = 1000       # 총 보낼 메시지 개수
TARGET_TPS = 1           # 초당 전송 개수 (부하 조절)
PACKET_SIZE_KB = 10        # 패킷 용량 (1, 10, 100KB 중 선택) -> 집가 한번 봐야함

def run_experiment():
    print("--- 분산 시스템 성능 테스트 시작 ---")
    
    # [Step 1] 데이터 공급자 생성 (용량 설정)
    # 1KB, 10KB, 100KB 실험 시 이 부분의 숫자를 변경합니다.
    provider = DataProvider(size_kb=PACKET_SIZE_KB)

    # 모드 B: 로드밸런서 사용하여 여러 대에 나눠 쏘기 (성능 비교용)
    # 나중에 실험 A가 끝나면 아래 줄의 주석을 해제하고 위 줄을 주석 처리하세요.
    dispatcher = NetworkLoadBalancer(ip_list=[ASUS_IP, DESKTOP_IP], port=PORT)

    # [Step 3] 시뮬레이션 매니저 생성
    # 설정한 TPS를 기반으로 정밀하게 전송 속도를 제어합니다.
    manager = SimulationManager(dispatcher, tps=TARGET_TPS)

    # [Step 4] 실험 시작
    try:
        manager.start(provider, total_count=TOTAL_PACKETS)
    except Exception as e:
        print(f" 실험 도중 오류 발생: {e}")
    finally:
        print("--- 테스트 종료 ---")

if __name__ == "__main__":
    run_experiment()