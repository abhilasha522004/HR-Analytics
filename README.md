# HR Analytics - Employee Management System

A comprehensive Django-based HR Analytics and Employee Management System that helps organizations manage their workforce efficiently while providing valuable insights through analytics.

## Features

- **Employee Management**
  - Employee profiles and records
  - Department management
  - Attendance tracking
  - Leave management
  - Performance evaluation

- **HR Analytics**
  - Employee performance metrics
  - Department-wise analytics
  - Attendance patterns
  - Workforce distribution
  - Custom report generation

- **User Management**
  - Role-based access control
  - Secure authentication
  - User profile management

## Technology Stack

- **Backend**: Django 4.2
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Frontend**: HTML, CSS, JavaScript
- **Data Analysis**: Pandas, NumPy
- **Additional Tools**: djangocms-admin-style

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/abhilasha522004/HR-Analytics.git
cd HR-Analytics/empmanagement
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

```
HR_Analytics/
├── empmanagement/          # Main project directory
│   ├── accounts/          # User authentication and management
│   ├── employee/          # Employee management app
│   ├── static/           # Static files (CSS, JS, images)
│   ├── templates/        # HTML templates
│   └── empmanagement/    # Project settings and configuration
├── requirements.txt      # Project dependencies
└── manage.py            # Django management script
```

## ML & Analytics Module (Streamlit)

`empmanagement/employee/ml_models/app.py` is a Streamlit dashboard for HR teams:

- **Attrition prediction:** scikit-learn pipeline predicting employee turnover probability (89% accuracy)
- **Workforce segmentation:** K-Means clustering of employees, with cluster centroids for review
- **Feedback sentiment analysis:** sentiment scoring and word clouds on employee feedback
- **Resume / ATS matcher:** scores resumes against job descriptions to find skill gaps
- **Course recommendations:** suggests training courses for identified skill gaps

```bash
cd empmanagement/employee/ml_models
streamlit run app.py
```

## Roadmap
- REST API for mobile and third-party integrations
- Audit logging and two-factor authentication
- Scheduled report exports (PDF, Excel, CSV)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the repository or contact the development team.

## Acknowledgments

- Django Framework
- All contributors and maintainers
- Open source community
