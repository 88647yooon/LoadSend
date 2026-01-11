import socket
import json

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
        """소켓이 없거나 끊겼을 때만 새로 연결하는 헬퍼 메서드"""
        if self.sock is None:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(2.0)
                self.sock.connect((self.target_ip, self.port))
                print(f"[{self.target_ip}] 연결 성공 (지속 연결 시작)")
            except Exception as e:
                self.sock = None
                raise ConnectionError(f"연결 실패: {e}")
        return self.sock

    def dispatch(self, packet):
        try:
            sock = self._get_connection()
            json_data = json.dumps(packet).encode('utf-8')
            # 💡 패킷 간 구분을 위해 구분자(예: \n)를 추가하는 것이 좋습니다.
            sock.sendall(json_data + b"\n") 
        except (socket.error, ConnectionError) as e:
            print(f" 전송 중 연결 끊김, 재시도 중... ({e})")
            self.close() # 끊긴 소켓 정리
            # 재연결 후 다시 시도하거나 에러 처리

    def close(self):
        if self.sock:
            self.sock.close()
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