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
        self.sock = None 

    def _get_connection(self):
        # 복잡한 체크 대신, 소켓이 없으면 새로 만듭니다.
        if self.sock is None:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(2.0)
                self.sock.connect((self.target_ip, self.port))
                print(f" [{self.target_ip}] 지속 연결 수립 성공")
            except Exception as e:
                self.sock = None
                raise ConnectionError(f"서버 접속 불가: {e}")
        return self.sock

    def dispatch(self, packet):
        try:
            sock = self._get_connection()
            
            # JSON 직렬화 및 줄바꿈 추가
            json_data = (json.dumps(packet) + "\n").encode('utf-8')
            
            # 전송 시도
            sock.sendall(json_data)
            return True
            
        except (socket.error, ConnectionError) as e:
            # 전송에 실패했을 때만 소켓을 닫고 다음 루프에서 재연결하게 합니다.
            print(f" [{self.target_ip}] 연결 유실 발생, 다음 패킷 전송 시 재연결 시도 ({e})")
            self.close()
            return False

    def close(self):
        if self.sock:
            try:
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