from scapy.all import IP, TCP, UDP
import time

class FlowAggregator:

    def __init__(self, timeout=30):
        self.flows = {}       # key: 5-tuple → value: list of packets + metadata
        self.timeout = timeout

    def add_packet(self, pkt):
        key = self._get_key(pkt)
        if key is None:
            return None

        now = time.time()

        # If flow doesn't exist yet, create it
        if key not in self.flows:
            self.flows[key] = {
                'packets'    : [],      # list of (timestamp, size, direction)
                'start_time' : now,
                'last_seen'  : now,
                'fwd_packets': [],      # src→dst
                'bwd_packets': [],      # dst→src
                'flags'      : {'SYN':0, 'ACK':0, 'FIN':0,
                                'RST':0, 'PSH':0, 'URG':0}
            }

        flow = self.flows[key]
        flow['last_seen'] = now

        # Packet size
        pkt_size = len(pkt)

        # Direction — compare against the key's src IP
        first_src = key[0]
        if pkt[IP].src == first_src:
            flow['fwd_packets'].append(pkt_size)
        else:
            flow['bwd_packets'].append(pkt_size)

        # TCP flags
        if pkt.haslayer(TCP):
            flags = pkt[TCP].flags
            if 'S' in str(flags): flow['flags']['SYN'] += 1
            if 'A' in str(flags): flow['flags']['ACK'] += 1
            if 'F' in str(flags): flow['flags']['FIN'] += 1
            if 'R' in str(flags): flow['flags']['RST'] += 1
            if 'P' in str(flags): flow['flags']['PSH'] += 1
            if 'U' in str(flags): flow['flags']['URG'] += 1

        flow['packets'].append((now, pkt_size))

        # Check if flow is finished
        is_fin = pkt.haslayer(TCP) and ('F' in str(pkt[TCP].flags)
                                        or 'R' in str(pkt[TCP].flags))
        is_timeout = (now - flow['start_time']) > self.timeout

        if is_fin or is_timeout:
            return self._extract_features(key)

        return None

    def _get_key(self, pkt):
        if not pkt.haslayer(IP):
            return None

        src_ip = pkt[IP].src
        dst_ip = pkt[IP].dst
        proto  = pkt[IP].proto

        if pkt.haslayer(TCP):
            sport = pkt[TCP].sport
            dport = pkt[TCP].dport
        elif pkt.haslayer(UDP):
            sport = pkt[UDP].sport
            dport = pkt[UDP].dport
        else:
            sport, dport = 0, 0

        forward_key  = (src_ip, dst_ip, sport, dport, proto)
        backward_key = (dst_ip, src_ip, dport, sport, proto)

        # If backward key exists, this is a reply packet — use same key
        if backward_key in self.flows:
            return backward_key

        # Otherwise treat as new forward flow
        return forward_key

    def _extract_features(self, key):
        import numpy as np

        flow = self.flows.pop(key)   # remove from active flows

        fwd = flow['fwd_packets']    # list of packet sizes going forward
        bwd = flow['bwd_packets']    # list of packet sizes going backward
        all_pkts = fwd + bwd

        duration = flow['last_seen'] - flow['start_time']
        duration = max(duration, 0.000001)   # avoid division by zero

        # Helper — safe stats on a list
        def stats(lst):
            if not lst:
                return 0, 0, 0, 0
            arr = np.array(lst)
            return arr.mean(), arr.std(), arr.min(), arr.max()

        fwd_mean, fwd_std, fwd_min, fwd_max = stats(fwd)
        bwd_mean, bwd_std, bwd_min, bwd_max = stats(bwd)
        all_mean, all_std, all_min, all_max = stats(all_pkts)

        # Inter-arrival times
        timestamps = [t for t, _ in flow['packets']]
        iats = np.diff(timestamps) if len(timestamps) > 1 else [0]
        iat_mean = np.mean(iats)

        total_bytes = sum(all_pkts)

        features = {
            'Destination Port'            : key[3],
            'Flow Duration'               : duration * 1e6,   # microseconds
            'Total Fwd Packets'           : len(fwd),
            'Total Backward Packets'      : len(bwd),
            'Total Length of Fwd Packets' : sum(fwd),
            'Total Length of Bwd Packets' : sum(bwd),
            'Fwd Packet Length Max'       : fwd_max,
            'Fwd Packet Length Min'       : fwd_min,
            'Fwd Packet Length Mean'      : fwd_mean,
            'Fwd Packet Length Std'       : fwd_std,
            'Bwd Packet Length Max'       : bwd_max,
            'Bwd Packet Length Min'       : bwd_min,
            'Bwd Packet Length Mean'      : bwd_mean,
            'Bwd Packet Length Std'       : bwd_std,
            'Flow Bytes/s'                : total_bytes / duration,
            'Flow Packets/s'              : len(all_pkts) / duration,
            'Flow IAT Mean'               : iat_mean,
            'SYN Flag Count'              : flow['flags']['SYN'],
            'ACK Flag Count'              : flow['flags']['ACK'],
            'FIN Flag Count'              : flow['flags']['FIN'],
            'RST Flag Count'              : flow['flags']['RST'],
            'PSH Flag Count'              : flow['flags']['PSH'],
            'URG Flag Count'              : flow['flags']['URG'],
            'Average Packet Size'         : all_mean,
            'Avg Fwd Segment Size'        : fwd_mean,
            'Avg Bwd Segment Size'        : bwd_mean,
            'Packet Length Mean'          : all_mean,
            'Packet Length Std'           : all_std,
            'Packet Length Variance'      : all_std ** 2,
            'Max Packet Length'           : all_max,
        }

        return features
