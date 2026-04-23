# Simple Web - Hardened Helm Chart

This repository contains a production-grade Helm chart for the `simple-web` application, a legacy Python 2.7 web server. I have optimized this chart for security, high availability, and cost-efficiency within an Azure Kubernetes Service (AKS) environment.

## Architectural Decisions & Hardening

### 1. "Stripped Root" Security Model
The application is a legacy Python 2.7 script that requires root permissions to bind to port 80 and perform file I/O within its own code directory (`/code`). To secure this without breaking functionality, I implemented a "Stripped Root" model:
*   **Capabilities**: I dropped `ALL` kernel capabilities and added only `NET_BIND_SERVICE`. This ensures that even as "root," the process cannot perform administrative tasks (like `chmod`, `chown`, or raw socket access).
*   **Privilege Escalation**: I disabled `allowPrivilegeEscalation` to prevent the process from ever regaining privileges.
*   **ServiceAccount**: I disabled `automountServiceAccountToken` at both the ServiceAccount and Pod levels to eliminate the risk of a compromised pod accessing the Kubernetes API.
*   **Non-Root (Pod Level)**: While the container runs as root, I applied `fsGroup: 2000` to ensure volume compatibility if storage is added later.

### 2. High Availability & Scheduling
To ensure the application is resilient to node failures and follows AKS best practices:
*   **Topology Spread Constraints**: I configured `maxSkew: 1` using the `kubernetes.io/hostname` key. This ensures the scheduler distributes the 3 replicas across different nodes.
*   **Availability vs. Distribution**: I set `whenUnsatisfiable: ScheduleAnyway`. This prioritizes keeping the app running on a single node if others fail, rather than leaving pods in a `Pending` state.
*   **Node Pool Isolation**: I implemented a `nodeSelector` for `kubernetes.azure.com/mode: user`. This keeps application workloads on "User Pools" and off the "System Pools," protecting the cluster's internal services.

### 3. Resource Optimization
Based on empirical data gathered via `kubectl top`, I right-sized the resource requests to maintain efficiency:
*   **CPU**: `5m` (Request).
*   **Memory**: `32Mi` (Request).
*   **Bursting**: I kept limits higher (`100m`/`128Mi`) to allow the Python interpreter to handle synchronous file operations (Pickle serialization) during traffic spikes.

### 4. Health Check Refinement
The application logs every successful HTTP GET request to its "Visitor Results" page.
*   **Problem**: Standard HTTP probes were polluting the logs with internal "Node Request" entries every 10 seconds.
*   **Solution**: I switched to `tcpSocket` probes. This verifies the process is listening without triggering the internal logging logic, resulting in a cleaner UI and reduced I/O overhead.

### 5. Advanced Scaling (KEDA)
I implemented a toggleable `ScaledObject` using KEDA to handle dynamic traffic patterns:
*   **Multi-Trigger Scaling**: The app scales based on both CPU and Memory utilization (threshold: 70%).
*   **Scheduled Scaling**: I added a `cron` trigger to ensure a minimum of 3 replicas are running during peak business hours (8:00 AM to 12:00 AM).
*   **Production Readiness**: The KEDA template is wrapped in a conditional block (`keda.enabled`) to prevent deployment failures on clusters without the KEDA controller.

## Automated Testing & Validation

I follow a multi-tier testing strategy to ensure every release is healthy and secure.

### Internal Validation (Helm Tests)
I implemented `helm.sh/hook: test` pods to perform deep diagnostics inside the cluster:
*   **Functional Audit**: Uses `curl` to verify that the service returns a `200 OK` and that the HTML body correctly renders the "Visit Results" page.
*   **Security Audit**: A dedicated pod verifies that the ServiceAccount token is **not** mounted and that the `root` user is unable to perform privileged operations (e.g., `chown` fails), validating the "Stripped Root" enforcement.

### External Validation (Pipeline)
The pipeline performs an automated end-to-end check after deployment:
*   **Ingress Discovery**: Dynamically retrieves the Public IP of the NGINX Ingress Controller.
*   **Resilient Smoke Test**: Uses a `waitUntil` retry loop with a 2-minute timeout to account for cloud LoadBalancer propagation, ensuring the app is reachable from the internet before finishing the build.

## Deployment & Pipeline

### Jenkins Pipeline
The `Jenkinsfile` provides a fully automated lifecycle for the chart:
*   **Continuous Deployment**: Integrated with GitHub Webhooks (`githubPush()`) to trigger an automated `Deploy` action on every commit to the main branch.
*   **Conditional Builds**: Optimized to skip deployment and testing stages for documentation-only changes. The pipeline uses a `Initialize & Detect Changes` stage to ensure it only runs when the Helm chart or the `Jenkinsfile` itself is modified.
*   **Concurrency Protection**: Implemented `disableConcurrentBuilds()` to prevent race conditions and Helm state locks during overlapping deployments.
*   **Authentication**: Uses Managed Identity (`az login -i`) and `kubelogin` for secure, passwordless access to AKS.
*   **Synchronization**: Uses `kubectl rollout status` to block the pipeline until the new version is fully healthy.
*   **Actions**: Supports both `Deploy` and `Destroy` actions via pipeline parameters.

## Future Enhancements
*   **Pod Disruption Budget (PDB)**: I have implemented a PDB template with `minAvailable: 1` to ensure zero downtime during node maintenance. This is currently **disabled** (`podDisruptionBudget.enabled: false`) due to cluster-level RBAC restrictions on the `policy` API group. 

---
*Developed by Pavel Nikolaichuk - DevOps Technical Assignment.*
