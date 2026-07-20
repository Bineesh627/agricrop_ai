# 🌾 AgriCrop AI - Smart Crop Recommendation & Agricultural Analytics System

**AgriCrop AI** is an intelligent, machine learning-powered web application built with Python and Django. It helps farmers, agricultural advisors, and researchers determine the optimal crops to cultivate based on specific soil nutrient levels and environmental climate conditions.

---

## 🚀 Features

- **🤖 AI-Powered Crop Recommendation**: Predicts the best crop species using Machine Learning based on:
  - **Soil Nutrients**: Nitrogen (N), Phosphorus (P), Potassium (K), and pH levels.
  - **Environmental Factors**: Temperature (°C), Humidity (%), and Rainfall (mm).
- **📖 Comprehensive Crop Library**: Explore ideal growing conditions, fertilizer split-dosing strategies, water requirements, and harvesting periods for various crops (Cereals, Pulses, Fruits, Commercial/Cash crops).
- **📊 Prediction History & Analytics**: Logged-in users can save and review past recommendations and environmental test records.
- **👥 User & Role Management**: Multi-user support with custom profiles for **Farmers** and **Administrators**.
- **🌱 Automated Database Seeding**: Pre-built script (`seed_db.py`) to populate the system with standard crop profiles and benchmark data.
- **💬 Feedback & Support System**: In-app feedback submission system allowing users to contact admins or request guidance.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.x, Django 4.2+
- **Machine Learning**: Scikit-Learn, Joblib, NumPy, Pandas
- **Database**: SQLite3 (default for development)
- **Frontend**: HTML5, CSS3, JavaScript, FontAwesome Icons

---

## 📁 Project Structure

```text
agriculture/
├── agri_project/          # Main Django project settings & routing
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── crop_app/              # Main Django application module
│   ├── models.py          # Database models (UserProfile, CropInformation, PredictionRecord)
│   ├── views.py           # Application views & ML integration logic
│   ├── forms.py           # Django forms for user inputs and feedback
│   ├── ml_model.py        # Machine Learning inference logic
│   ├── templates/         # HTML templates
│   └── urls.py            # App-level routing
├── ml_assets/             # Trained ML model artifacts & scalers
├── static/                # Static assets (CSS, JS, images)
├── db.sqlite3             # SQLite Database
├── seed_db.py             # Database seed script for initial crop data
├── manage.py              # Django command-line utility
├── .gitignore             # Git ignore configuration
└── README.md              # Project documentation
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
Ensure you have Python 3.8 or higher installed on your system.

### 2. Clone the Repository
```bash
git clone https://github.com/Bineesh627/agricrop_ai.git
cd agriculture
```

### 3. Create and Activate Virtual Environment
- **Windows**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```
- **macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 4. Install Dependencies
```bash
pip install django scikit-learn pandas numpy joblib
```

### 5. Apply Migrations & Seed Database
```bash
python manage.py makemigrations
python manage.py migrate
python seed_db.py
```

### 6. Create a Superuser / Admin (Optional)
```bash
python manage.py createsuperuser
```

### 7. Run the Development Server
```bash
python manage.py runserver
```

Open your browser and navigate to `http://127.0.0.1:8000/`.

---

## 🛡️ License

This project is open-source and available under the [MIT License](LICENSE).
