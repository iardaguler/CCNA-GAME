# network/tools.py
import subprocess
import platform


class NetworkToolbox:
    """
    CCNA-GAME öğrencileri için ağ araçlarını simüle eder veya çalıştırır.
    """

    @staticmethod
    def check_ping(host):
        """
        Gerçek bir ping atar (Oyun içinde gerçekçilik için).
        """
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', host]

        try:
            output = subprocess.check_output(command)
            return True  # Bağlantı başarılı
        except subprocess.CalledProcessError:
            return False  # Bağlantı başarısız

    @staticmethod
    def validate_ip(ip_addr):
        """
        Girilen IP'nin formatını kontrol eder (Örn: 192.168.1.1).
        Basit bir mantık kontrolü.
        """
        parts = ip_addr.split(".")
        if len(parts) != 4:
            return False
        for item in parts:
            if not 0 <= int(item) <= 255:
                return False
        return True