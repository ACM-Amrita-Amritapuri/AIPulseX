# Taskify

A modern task management application built with Flask and MongoDB. Taskify helps you organize, track, and manage your tasks efficiently with a beautiful, responsive user interface.

## Features

- 🔐 **User Authentication** - Secure login and registration system
- 📋 **Task Management** - Create, organize, and track your tasks
- 📊 **Analytics** - Monitor your productivity and task completion rates
- 🎨 **Modern UI** - Clean, responsive design with dark theme
- 📱 **Mobile Friendly** - Works seamlessly on all devices
- ⚡ **Real-time Validation** - Instant feedback on form inputs
- 🔔 **Smart Notifications** - Flash messages with auto-dismiss

## Tech Stack

- **Backend**: Flask, Python
- **Database**: MongoDB
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: Flask-JWT-Extended
- **Security**: Werkzeug password hashing

## Getting Started

### Prerequisites

- Python 3.8+
- MongoDB
- pip or uv package manager

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd Taskify
```

2. Install dependencies:

```bash
pip install -r requirements.txt
# or if using uv:
uv sync
```

3. Set up environment variables:
   Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key-here
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=Taskify
COLLECTION_NAME=Users
```

4. Start MongoDB service

5. Run the application:

```bash
python app.py
```

6. Open your browser and navigate to `http://127.0.0.1:5000`

## Project Structure

```
Taskify/
├── app.py                 # Main Flask application
├── Backend/
│   ├── auth.py           # Authentication blueprint
│   └── utils.py          # Utility functions
├── Frontend/
│   ├── Templates/        # HTML templates
│   └── scripts/          # CSS and JavaScript files
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Usage

1. **Register**: Create a new account with a username and password
2. **Login**: Access your dashboard with your credentials
3. **Dashboard**: View your tasks and productivity metrics
4. **Task Management**: Create, edit, and organize your tasks (coming soon)
5. **Analytics**: Track your progress and productivity (coming soon)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support or questions, please open an issue in the repository.

---

**Taskify** - Making task management simple and efficient! 🚀
