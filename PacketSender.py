import socket
import json
import time

class BaseDispatcher:
    def dispatch(self, packet):
        raise NotImplementedError
    def close(self):
        """실험 종료 시 연결을 깔끔하게 닫기 위한 메서드"""
        pass

class DirectDispatcher(BaseDispatcher):
    def __init__(self, target_ip, port=5000):
        self.target_ip = target_ip
        self.port = port
        self.sock = None # 소켓을 저장할 변수

   
    def _get_connection(self):
    
    # 1. 만약 소켓이 있다면, 실제 살아있는지 아주 가볍게 체크해봅니다.
     if self.sock is not None:
        try:
            # 0바이트를 읽어보려 시도하거나 소켓 에러 상태를 체크 (가장 가벼운 방법)
            # 혹은 그냥 아무것도 안 하고 다음 전송 단계에서 에러가 나길 기다려도 됩니다.
            # 하지만 확실히 하려면 아래 코드를 추가할 수 있습니다.
            self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        except Exception:
            # 무언가 문제가 있다면 닫고 새로 시작하기 위해 None 처리
            self.close()

    
     if self.sock is None:
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 타임아웃은 실험 환경에 맞춰 1.0~2.0초가 적당합니다.
            self.sock.settimeout(2.0) 
            self.sock.connect((self.target_ip, self.port))
            print(f"✅ [{self.target_ip}] 새 연결 성공")
        except Exception as e:
            # 연결 실패 시 반드시 None으로 초기화해서 다음 시도 때 다시 connect하게 함
            self.sock = None
            raise ConnectionError(f"서버 접속 불가: {e}")

        return self.sock

    def dispatch(self, packet):
        
     try:
        sock = self._get_connection()
        
       
        if sock is None:
            print(f"⚠️ [{self.target_ip}] 연결된 소켓이 없어 전송을 취소합니다.")
            return False
            
        json_data = (json.dumps(packet) + "\n").encode('utf-8')
        sock.sendall(json_data)
        return True
        
     except (socket.error, ConnectionError, AttributeError) as e:
        # AttributeError도 예외 처리에 추가하여 프로그램 중단을 방지
        print(f" 전송 중 오류 발생 ({self.target_ip}): {e}")
        self.close()
        return False

    def close(self):
    
     if self.sock:
        try:
            self.sock.shutdown(socket.SHUT_RDWR) # 연결 강제 종료 신호
            self.sock.close()
        except:
            pass
    
     self.sock = None


class NetworkLoadBalancer(BaseDispatcher):
    def __init__(self, ip_list, port=5000):
        self.ip_list = ip_list
        self.port = port
        self.sockets = {} # IP별 소켓 관리 {ip: socket_object}
        self.current_index = 0

    def _get_connection(self, ip):
        if ip not in self.sockets or self.sockets[ip] is None:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2.0)
                s.connect((ip, self.port))
                self.sockets[ip] = s
            except Exception as e:
                print(f"{ip} 연결 실패: {e}")
                return None
        return self.sockets[ip]

    def dispatch(self, packet):
        target_ip = self.ip_list[self.current_index % len(self.ip_list)]
        sock = self._get_connection(target_ip)
        
        if sock:
            try:
                json_data = json.dumps(packet).encode('utf-8')
                sock.sendall(json_data + b"\n")
                self.current_index += 1
            except socket.error:
                print(f" {target_ip} 연결 유실로 인한 소켓 제거")
                self.sockets[target_ip].close()
                del self.sockets[target_ip]

    def close(self):
        for s in self.sockets.values():
            if s: s.close()
        self.sockets = {}