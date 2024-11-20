import redis
import random
import time
import threading
from kubernetes import client, config

#use in cluster config since we are local
config.load_incluster_config()
#config.load_kube_config()

# python3 /Users/marcusvaughnjones/k8s/MFmon.py

r = redis.Redis(host='redis-service', port=6379, db=0)

# Initialize metrics in Redis
default_metrics = {
    "cpu": 30,
    "dasd": 20,
    "pagein": 10,
    "pageout": 28,
    "iops": 120
}

for key, value in default_metrics.items():
    r.set(key, value)

# Set flags to indicate when metrics are in a high state
high_state = {
    "cpu": False,
    "dasd": False,
    "pagein": False,
    "pageout": False,
    "iops": False
}

# Healthy ranges for each metric
healthy_ranges = {
    "cpu": (30, 60),
    "dasd": (10, 40),
    "pagein": (5, 20),
    "pageout": (5, 25),
    "iops": (100, 200)
}
for key, value in default_metrics.items():
    r.set(key, value)
    r.set(f"high_state_{key}", 0)  # 0 = False, 1 = True
    
def high_cpu():
    cpu = random.randint(80, 99)
    r.set("cpu", cpu)
    high_state["cpu"] = True  # Set the CPU high state flag
    print("High CPU metrics:", get_metrics())
    check_and_trigger_pod(cpu)

def high_dasd():
    dasd = random.randint(80, 99)
    r.set("dasd", dasd)
    high_state["dasd"] = True
    print("High DASD metrics:", get_metrics())

def high_iops():
    iops = random.randint(400, 500)
    r.set("iops", iops)
    high_state["iops"] = True
    print("High IOPS metrics:", get_metrics())

def high_pagein():
    pagein = random.randint(80, 100)
    r.set("pagein", pagein)
    high_state["pagein"] = True
    print("High Page In metrics:", get_metrics())

def high_pageout():
    pageout = random.randint(40, 60)
    r.set("pageout", pageout)
    high_state["pageout"] = True
    print("High Page Out metrics:", get_metrics())

# List of high-metrics functions for random selection
high_metrics_functions = [high_cpu, high_dasd, high_iops, high_pagein, high_pageout]

def check_and_trigger_pod(metric):
    v1 = client.CoreV1Api()

    # !!!!!! Check if the maintenance pod already exists by querying Kubernetes with labels
    try:
        pods = v1.list_namespaced_pod(
            namespace="default",
            label_selector="app=maintenance"  # Ensure label matches maintenance pod
        )
        if pods.items:  # If pods with the label exist
            print("Maintenance pod already exists.")
            return
    except Exception as e:
        print(f"Error checking for existing maintenance pods: {e}")
        return

    print(f"High workload detected for {metric}. Triggering a maintenance pod.")
    pod_name = "maintenance-pod"
    namespace = "default"

    # !!!!!! Update pod template with proper command and labels
    pod_template = client.V1Pod(
        metadata=client.V1ObjectMeta(
            name=pod_name,
            labels={"app": "maintenance"}  # Add label for easier querying
        ),
        spec=client.V1PodSpec(
            containers=[
                client.V1Container(
                    name="maintenance",
                    image="maintenance-pod-image",  # Ensure this matches the correct image
                    command=["python", "maintenance_pod.py"],  # Correct script path
                )
            ],
            restart_policy="Never"  # Set to Never to avoid unexpected restarts
        )
    )

    try:
        # !!!!!! Create pod if none exists
        v1.create_namespaced_pod(namespace=namespace, body=pod_template)
        print(f"Pod {pod_name} created.")
    except client.exceptions.ApiException as e:
        print(f"Failed to create pod: {e}")


def get_metrics():
    return {
        "cpu": f"{int(r.get('cpu'))}%",
        "dasd": f"{int(r.get('dasd'))}%",
        "pagein": int(r.get("pagein")),
        "pageout": int(r.get("pageout")),
        "iops": int(r.get("iops")),
    }

# Display metrics and maintain healthy ranges unless a high state is active
def display_metrics():
    while True:
        for metric, (low, high) in healthy_ranges.items():
            if not high_state[metric]:  # Only adjust if not in a high state
                value = random.randint(low, high)
                r.set(metric, value)

        print("Current Mainframe metrics:", get_metrics())
        time.sleep(5)

metrics_thread = threading.Thread(target=display_metrics, daemon=True)
metrics_thread.start()

def main():
    try:
        while True:
            selected_function = random.choice(high_metrics_functions)
            print(f"Running {selected_function.__name__}")
            selected_function()
            time.sleep(30)
    except KeyboardInterrupt:
        print("Program interrupted. Exiting...")

main()
# python3 /Users/marcusvaughnjones/k8s/MFmon.py
