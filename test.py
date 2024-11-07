import redis
import random
import time
import threading
from kubernetes import client, config

#use in cluster config since we are local
#config.load_incluster_config()

# python3 /Users/marcusvaughnjones/k8s/MFmon.py

r = redis.Redis(host='localhost', port=6379, db=0)

# Initialize metrics in Redis
r.set("cpu", 30)
r.set("dasd", 20)
r.set("pagein", 10)
r.set("pageout", 28)
r.set("iops", 120)

def high_cpu():
    # Simulate high CPU usage
    cpu = random.randint(80, 99)
    r.set("cpu", cpu)  # Update CPU in Redis
    metrics = {
            "cpu": f"{int(r.get('cpu'))}%",  # Adding % symbol to cpu
            "dasd": f"{int(r.get('dasd'))}%",  # Adding % symbol to dasd
            "pagein": int(r.get("pagein")),
            "pageout": int(r.get("pageout")),
            "iops": int(r.get("iops")),
        }
    
    print("High CPU metrics:", metrics)
    check_and_trigger_pod(cpu)

def high_dasd():
    print("high dasd no logic")

def high_iops():
    print("high iops no logic")

def high_pagein():
    print("high pagein no logic")

def high_pageout():
    print("high pageout no logic")

high_metrics_functions = [high_cpu, high_dasd, high_iops, high_pagein, high_pageout]

def check_and_trigger_pod(cpu):
    if cpu > 75:
        print("High workload detected. Triggring a maintnence Pod")

        # Define pod metadata and specifications
        pod_name = "maitnence-pod"
        namespace = "default"  # Change if your pod needs to be in a specific namespace
        pod_template = client.V1Pod(
            metadata=client.V1ObjectMeta(name=pod_name),
            spec=client.V1PodSpec(
                containers=[client.V1Container(
                    name="maitnence",
                    image="your-container-image",  # Replace with your container image
                    command=["python", "/Users/marcusvaughnjones/MFmon.py"],  # Replace with your script path
                )]
            )
        )

        # Initialize the Kubernetes API
        v1 = client.CoreV1Api()

        # Try to create the pod, if it doesn’t already exist
        try:
            v1.create_namespaced_pod(namespace=namespace, body=pod_template)
            print(f"Pod {pod_name} created.")
        except client.exceptions.ApiException as e:
            if e.status == 409:  # Conflict error, pod already exists
                print(f"Pod {pod_name} already exists.")
            else:
                print(f"Failed to create pod: {e}")


# Dedicating a thread to displaying mainframe metrics 
def display_metrics():
    while True:
        # Generate random values for each metric
        cpu = random.randint(30, 75)
        dasd = random.randint(10, 85)
        pagein = random.randint(5, 100)
        pageout = random.randint(5, 50)
        iops = random.randint(100, 500)

        # Update metrics in Redis
        r.set("cpu", cpu)
        r.set("dasd", dasd)
        r.set("pagein", pagein)
        r.set("pageout", pageout)
        r.set("iops", iops)

        metrics = {
            "cpu": f"{int(r.get('cpu'))}%",  # Adding % symbol to cpu
            "dasd": f"{int(r.get('dasd'))}%",  # Adding % symbol to dasd
            "pagein": int(r.get("pagein")),
            "pageout": int(r.get("pageout")),
            "iops": int(r.get("iops")),
        }
        print("Current Mainframe metrics:", metrics)
        time.sleep(5)
metrics_thread = threading.Thread(target=display_metrics, daemon=True)
metrics_thread.start()

def main():
# Main loop to display metrics and accept user input
    try:
        while True:

            # Check for user input
            selected_function = random.choice(high_metrics_functions)
            print(f"Running {selected_function.__name__}")
            selected_function()
            time.sleep(30)

    except KeyboardInterrupt:
        print("Program interrupted. Exiting...")

main()
# python3 /Users/marcusvaughnjones/k8s/MFmon.py