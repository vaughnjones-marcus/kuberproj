import redis
import sys
import random

# Connect to Redis
r = redis.Redis(host='redis-service', port=6379, db=0)

def lower_metric(metric):
    # Define healthy ranges for each metric
    healthy_ranges = {
        "cpu": (30, 60),
        "dasd": (10, 40),
        "pagein": (5, 20),
        "pageout": (5, 25),
        "iops": (100, 200)
    }

    # Set the metric to a healthy level
    if metric in healthy_ranges:
        low, high = healthy_ranges[metric]
        normal_value = random.randint(low, high)
        r.set(metric, normal_value)
        r.set(f"high_state_{metric}", 0)  # Reset high state flag in Redis (0 = False)
        print(f"Maintenance completed for {metric}: Lowered to healthy range ({normal_value})")
    else:
        print(f"Unknown metric: {metric}")

if __name__ == "__main__":
    # Get metric name from arguments
    if len(sys.argv) > 1:
        metric = sys.argv[1]
        lower_metric(metric)
    else:
        print("No metric specified for maintenance.")