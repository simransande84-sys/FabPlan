# Window and Door Fabrication Software

A production-ready Django 5.x application for window and door fabrication, featuring cutting optimization, hardware BOQ generation, and comprehensive reporting.

## Features
- **Single-page UI**: Clean and minimal interface without heavy JS frameworks.
- **Cutting Optimizer**: Implements First-Fit Decreasing Bin Packing Algorithm to minimize bar waste.
- **Hardware BOQ Engine**: Evaluates formula-based quantities dynamically based on window typologies.
- **PDF & Excel Reports**: Automated generation of Quotations, Material BOQs, and Bar Cutting Charts.

## Local Setup

1. **Clone the repository** (if applicable) and navigate to the project directory:
   ```bash
   cd final-idt
   ```

2. **Create a virtual environment and activate it**:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Seed the database** (Creates default profiles, hardware, and sample orders):
   ```bash
   python manage.py seed_data
   ```

6. **Run the development server**:
   ```bash
   python manage.py runserver
   ```
   Open `http://localhost:8000` in your browser.

## Docker Deployment (DigitalOcean Ready)

You can easily deploy this application using Docker.

1. **Build the Docker image**:
   ```bash
   docker build -t fabrication-software .
   ```

2. **Run the Docker container**:
   ```bash
   docker run -d -p 8000:8000 fabrication-software
   ```
   
   The app will be accessible at `http://your-server-ip:8000`.

*Note: For production on DigitalOcean, it is recommended to put Nginx in front of Gunicorn, or use DigitalOcean App Platform to deploy directly from the Dockerfile.*
