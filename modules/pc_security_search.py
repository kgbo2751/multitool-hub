import os
from dotenv import load_dotenv
import shodan
from scapy.all import sniff, IP, TCP

load_dotenv()

SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")

def capture_packets(count: int = 10, timeout: int = 5):
    captured_data = []

    def packet_handler(pkt):
        if pkt.haslayer(IP) and pkt.haslayer(TCP):
            captured_data.append({
                "src_ip": pkt[IP].src,
                "src_port": pkt[TCP].sport,
                "dst_ip": pkt[IP].dst,
                "dst_port": pkt[TCP].dport
            })

    try:
        sniff(prn=packet_handler, store=0, filter="tcp", count=count, timeout=timeout)
        return {"success": True, "packets": captured_data}
    except Exception as e:
        return {"success": False, "error": str(e)}

def search_shodan_ip(ip_address: str):
    if not SHODAN_API_KEY:
        return {"success": False, "error": "Shodan API 키가 설정되지 않았습니다."}

    try:
        api = shodan.Shodan(SHODAN_API_KEY)
        host_info = api.host(ip_address)
        return {
            "success": True,
            "data": {
                "ip": host_info.get("ip_str"),
                "org": host_info.get("org", "N/A"),
                "isp": host_info.get("isp", "N/A"),
                "os": host_info.get("os", "N/A"),
                "country": host_info.get("country_name", "N/A"),
                "ports": host_info.get("ports", []),
                "vulns": list(host_info.get("vulns", {}).keys()) if "vulns" in host_info else []
            }
        }
    except shodan.APIError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}