class CLIEngine:
    def __init__(self, available_commands=None):
        self.history = []
        self.history_index = -1
        self.available_commands = available_commands or []

    def normalize(self, cmd):
        """Dinamik komut normalizasyonu: Cisco kısaltmalarını tam hallerine çevirir."""
        original_cmd = cmd.strip()
        cmd = cmd.lower().strip()
        if not cmd: return ""
        
        # Token bazlı değişim tablosu
        mapping = {
            "conf t": "configure terminal",
            "conf terminal": "configure terminal",
            "no sh": "no shutdown",
            "no shut": "no shutdown",
            "int": "interface",
            "fa": "fastethernet",
            "gi": "gigabitethernet",
            "gig": "gigabitethernet",
            "en": "enable",
            "sh": "show",
            "v": "vlan",
            "access-l": "access-list",
            "ip nat i": "ip nat inside",
            "ip nat o": "ip nat outside"
        }

        # 1. Tam öbek eşleşmesi (Örn: "conf t")
        for key, value in mapping.items():
            if cmd.startswith(key):
                if len(cmd) == len(key) or cmd[len(key)] == " ":
                    cmd = value + cmd[len(key):]
                    break

        # 2. Kelime bazlı değişim (Sadece komutun başındaki kelimeler için kritik olanlar)
        parts = cmd.split()
        if parts:
            # Baştaki 'host'u 'hostname' yap (Sadece en başta ise)
            if parts[0] == "host":
                parts[0] = "hostname"
            
            # Diğer tekil kelime eşleşmeleri
            word_mapping = {"int": "interface", "fa": "fastethernet", "gi": "gigabitethernet", "en": "enable"}
            for i in range(len(parts)):
                if parts[i] in word_mapping:
                    # 'interface' gibi kelimeleri her yerde düzeltebiliriz (Cisco esnekliği)
                    parts[i] = word_mapping[parts[i]]
            
            cmd = " ".join(parts)
        
        return cmd

    def add_to_history(self, cmd):
        if cmd.strip():
            self.history.append(cmd.strip())
            self.history_index = len(self.history)

    def get_previous_command(self):
        if self.history and self.history_index > 0:
            self.history_index -= 1
            return self.history[self.history_index]
        return ""

    def get_next_command(self, current_input):
        if self.history and self.history_index < len(self.history) - 1:
            self.history_index += 1
            return self.history[self.history_index]
        self.history_index = len(self.history)
        return "" 

    def tab_complete(self, current_input):
        """Gerçek Cisco IOS tarzı token bazlı otomatik tamamlama."""
        if not current_input:
            return current_input
            
        ends_with_space = current_input.endswith(" ")
        parts = current_input.split()
        
        if not parts:
            return current_input
            
        if ends_with_space:
            return current_input
            
        last_token = parts[-1].lower()
        
        # 'host' kelimesini buradan çıkardım ki 'hostname' benzersiz kalsın
        cisco_keywords = [
            "enable", "configure", "terminal", "interface", "fastethernet", 
            "gigabitethernet", "serial", "ip", "address", "no", "shutdown",
            "vlan", "name", "access-list", "deny", "permit", "any",
            "nat", "inside", "outside", "source", "list", "overload",
            "dhcp", "pool", "network", "default-router", "dns-server",
            "line", "console", "vty", "password", "login", "exit", "end", 
            "hostname", "show", "running-config", "ip-address"
        ]
        
        for cmd in self.available_commands:
            cisco_keywords.extend(cmd.lower().split())
            
        candidates = list(set(cisco_keywords))
        matches = [k for k in candidates if k.startswith(last_token)]
        
        if len(matches) == 1:
            parts[-1] = matches[0]
            return " ".join(parts) + " "
        elif len(matches) > 1:
            # Eğer tam eşleşen bir tane varsa (Örn: hem 'ip' hem 'ip-address' varken 'ip' yazıldıysa)
            if last_token in matches:
                return current_input + " "
                
            prefix = os.path.commonprefix(matches)
            if prefix != last_token:
                parts[-1] = prefix
                return " ".join(parts)
        
        return current_input
        
import os # For commonprefix
