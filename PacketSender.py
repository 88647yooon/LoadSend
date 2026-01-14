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
        if sock is None : return False
        sock.sendall(packet) 
        return True
     
     except Exception as e:
        print(f" 전송 중 오류 발생: {e}")
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
                sock.sendall(packet)
                self.current_index += 1
            except socket.error:
                print(f" {target_ip} 연결 유실로 인한 소켓 제거")
                self.sockets[target_ip].close()
                del self.sockets[target_ip]

    def close(self):
        for s in self.sockets.values():
            if s: s.close()
        self.sockets = {}