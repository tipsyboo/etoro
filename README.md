# Simple Web - Helm Chart

This repository contains a Helm chart for the `simple-web` application, a legacy Python 2.7 web server. I have optimized this chart for security, high availability, and cost-efficiency within an Azure Kubernetes Service (AKS) environment.

## Architectural Decisions & Hardening

### 1. "Stripped Root" Security Model

The application is a legacy Python 2.7 script that requires root permissions to bind to port 80 and perform file I/O within its own code directory (`/code`). To secure this without breaking functionality, I implemented a "Stripped Root" model:

* **Capabilities**: I dropped `ALL` kernel capabilities and added only `NET_BIND_SERVICE`. This ensures that even as "root," the process cannot perform administrative tasks (like `chmod`, `chown`, or raw socket access).
* **Privilege Escalation**: I disabled `allowPrivilegeEscalation` to prevent the process from ever regaining privileges.
* **ServiceAccount**: I disabled `automountServiceAccountToken` to eliminate the risk of a compromised pod accessing the Kubernetes API.
* **Non-Root (Pod Level)**: While the container runs as root, I applied `fsGroup: 2000` to ensure volume compatibility if storage is added later.

### 2. High Availability & Scheduling

To ensure the application is resilient to node failures and follows AKS best practices:

* **Topology Spread Constraints**: I configured `maxSkew: 1` using the `kubernetes.io/hostname` key. This ensures the scheduler distributes the 3 replicas across different nodes.
* **Availability vs. Distribution**: I set `whenUnsatisfiable: ScheduleAnyway`. This prioritizes keeping the app running on a single node if others fail, rather than leaving pods in a `Pending` state.
* **Node Pool Isolation**: I implemented a `nodeSelector` for `kubernetes.azure.com/mode: user`. This keeps application workloads on "User Pools" and off the "System Pools," protecting the cluster's internal services.

### 3. Resource Optimization
Based on empirical data gathered via `kubectl top`, I right-sized the resource requests to maintain efficiency:
*   **CPU**: `5m` (Request).
*   **Memory**: `16Mi` (Request).
*   **Bursting**: I kept limits higher (`100m`/`128Mi`) to allow the Python interpreter to handle synchronous file operations (Pickle serialization) during traffic spikes.

### 4. Health Check Refinement

The application logs every successful HTTP GET request to its "Visitor Results" page.

* **Problem**: Standard HTTP probes were polluting the logs with internal "Node Request" entries every 10 seconds.
* **Solution**: I switched to `tcpSocket` probes. This verifies the process is listening without triggering the internal logging logic, resulting in a cleaner UI and reduced I/O overhead.

### 5. Advanced Scaling (KEDA)

I implemented a `ScaledObject` using KEDA to handle dynamic traffic patterns:

* **Multi-Trigger Scaling**: The app scales based on both CPU and Memory utilization (threshold: 70%).
* **Scheduled Scaling**: I added a `cron` trigger to ensure a minimum of 3 replicas are running during peak business hours (8:00 AM to 12:00 AM).

## Deployment & Pipeline

### Ingress Configuration

The app is exposed via Nginx Ingress on the path `/pavelni`.

* **Public IP**: `20.160.225.212`
* **Path**: `/pavelni`

### Jenkins Pipeline

The `Jenkinsfile` provides a fully automated lifecycle for the chart:

* **Authentication**: Uses Managed Identity (`az login -i`) and `kubelogin` for secure, passwordless access to AKS.
* **Actions**: Supports both `Deploy` (using `helm upgrade --install`) and `Destroy` (using `helm uninstall`) via pipeline parameters.
* **Validation**: Includes a `helm lint` stage to ensure chart integrity before every deployment.

---
*Developed by Pavel Nikolaichuk - DevOps Technical Assignment.*
