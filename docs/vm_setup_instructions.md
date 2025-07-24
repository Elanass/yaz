# VM Setup Instructions

## Step 1: Create a Virtual Machine
1. Use a virtualization tool like VirtualBox, VMware, or a cloud provider (e.g., Google Cloud, AWS, Azure).
2. Allocate the following resources:
   - **CPU**: 2 cores
   - **RAM**: 4 GB
   - **Disk Space**: 20 GB
   - **OS**: Ubuntu 22.04 LTS (recommended)

## Step 2: Install Docker and Docker Compose
1. Update the package index:
   ```bash
   sudo apt update
   ```
2. Install Docker:
   ```bash
   sudo apt install -y docker.io
   ```
3. Enable and start Docker:
   ```bash
   sudo systemctl enable docker
   sudo systemctl start docker
   ```
4. Add your user to the Docker group (optional):
   ```bash
   sudo usermod -aG docker $USER
   ```
   Log out and back in for the group change to take effect.
5. Install Docker Compose:
   ```bash
   sudo apt install -y docker-compose
   ```

## Step 3: Clone the Project Repository
1. Clone the project repository into the VM:
   ```bash
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```bash
   cd <project-directory>
   ```

## Step 4: Deploy Services
1. Run Docker Compose to start the backend and database services:
   ```bash
   docker-compose up --build
   ```
2. Verify that the services are running:
   ```bash
   docker ps
   ```

## Step 5: Access the Application
1. Access the backend API at `http://<vm-ip>:8000`.
2. Access the frontend at `http://<vm-ip>:3000` (if applicable).

## Notes
- Replace `<repository-url>` and `<project-directory>` with the actual values.
- Ensure the VM has network access to pull Docker images and dependencies.
