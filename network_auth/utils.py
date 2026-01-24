import ipaddress

def get_client_ip(request):
    """
    Get real client IP even behind proxy/ngrok
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")

    if ip == "::1":
        ip = "127.0.0.1"

    return ip


def get_network_prefix(ip):
    try:
        ip_obj = ipaddress.ip_address(ip)

        if ip_obj.version == 4:
            return ".".join(ip.split(".")[:3])  # 192.168.1
        else:
            return ":".join(ip.split(":")[:3])  # IPv6 prefix

    except Exception:
        return None
