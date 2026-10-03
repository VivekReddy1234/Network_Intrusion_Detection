import os
import sys
import json
import joblib
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

from scapy.all import sniff, IP, TCP, UDP
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(__file__))
from flow_aggregator import FlowAggregator
from db_writer import init_db, write_alert

# Load model and feature list
MODEL_PATH   = os.getenv('MODEL_PATH', os.path.join(os.path.dirname(__file__), '..', 'models', 'rf_model.pkl'))
FEATURE_PATH = os.getenv('FEATURE_PATH', os.path.join(os.path.dirname(__file__), '..', 'models', 'feature_list.json'))
THRESHOLD    = float(os.getenv('THRESHOLD', '0.7'))
IFACE        = os.getenv('IFACE')

clf      = joblib.load(MODEL_PATH)
features = json.load(open(FEATURE_PATH))

print(f'Model loaded. {len(features)} features expected.')

agg = FlowAggregator(timeout=30)
init_db()
print('FlowAggregator and DB ready.')

def build_vector(flow_dict):
    # Fill missing features with 0
    # Order must match exactly what model was trained on
    return [flow_dict.get(f, 0) for f in features]

def on_packet(pkt):
    if not pkt.haslayer(IP):
        return

    flow = agg.add_packet(pkt)

    if flow is None:
        return  # flow not complete yet

    # Build feature vector in correct order
    import pandas as pd
    vector = build_vector(flow)
    X = pd.DataFrame([vector], columns=features)

    # Run inference
    prob = clf.predict_proba(X)[0][1]  # probability of attack

    print(f'Flow complete | prob={prob:.3f} | dst_port={flow.get("Destination Port")}')

    if prob >= THRESHOLD:
        # Determine protocol
        protocol = 'TCP' if pkt.haslayer(TCP) else 'UDP'

        write_alert(
            src_ip   = pkt[IP].src,
            dst_ip   = pkt[IP].dst,
            dst_port = flow.get('Destination Port', 0),
            protocol = protocol,
            prob     = round(prob, 4),
            label    = 'ATTACK'
        )
        print(f'  ⚠ ALERT written! prob={prob:.3f}')

if __name__ == '__main__':
    print(f'Starting NIDS sniffer on interface: {IFACE}')
    print(f'Alert threshold: {THRESHOLD}')
    print('Press Ctrl+C to stop.\n')

    sniff(
        iface=IFACE,
        prn=on_packet,
        store=False      # don't store packets in memory
    )
