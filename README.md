# Expense Tracker
#### Video Demo:  <https://youtu.be/jY5hsqmjch8?si=kjh7kDnJen5klmUD>
#### Description:
## What is Expense Tracker?
Expense Tracker is a web-based application built with Python, Flask, SQL, HTML, CSS, and JavaScript. The app allows
users to track their daily expenses, categorize their spending, set a monthly budget, and visualize their financial habits
through interactive charts. The goal of this project is to solve a real-world problem that almost everyone faces: managing
personal finances effectively.
The idea came from a simple observation — most people spend money every day without truly knowing where it goes. By
the end of the month, they're surprised by how much they've spent. Expense Tracker solves this by giving users a clear,
visual, and easy-to-use tool to record and monitor every expense.
---
## Features
### 1. User Authentication
The app supports full user registration and login. Each user has their own private account, and all data is isolated per
user. Passwords are never stored in plain text — they are hashed using Werkzeug's `generate_password_hash` function
before being saved to the database. This ensures that even if the database is compromised, passwords remain secure.
### 2. Add Expenses
Users can add a new expense by entering the amount, selecting a category (such as Food, Transport, Housing, Health,
Entertainment, Shopping, Education, Bills, Travel, or Other), picking a date, and optionally writing a note. The date input
automatically defaults to today's date using JavaScript, which makes the process faster and more convenient.
### 3. Edit and Delete Expenses
Mistakes happen — a user might enter the wrong amount or forget to add a note. The History page allows users to edit
any past expense or delete it entirely. The app always verifies that the expense belongs to the currently logged-in user
before allowing any modification or deletion, which prevents unauthorized access to other users' data.
### 4. Monthly Budget
Users can set their monthly income and an optional spending limit. The app then calculates how much money is
remaining after expenses. If the user reaches 90% or more of their spending limit, a warning alert is displayed on the
Dashboard. This feature encourages users to be more mindful of their spending before it's too late.
### 5. Dashboard
The main page of the app gives users a quick overview of their financial situation for the current month. It displays the
total amount spent, the monthly income, the remaining balance, a list of the 5 most recent expenses, and an interactive
doughnut chart showing spending by category — all powered by Chart.js.
### 6. Reports
The Reports page provides deeper insights. It shows a pie chart of spending by category for the current month, a bar
chart showing total spending over the last 6 months, a breakdown table by category with totals, and an all-time total
spending figure. These visualizations make it easy to spot patterns and identify areas where the user can cut back.
### 7. Expense History with Filtering
The History page shows a complete list of all recorded expenses in reverse chronological order. Users can filter expenses
by category using a dropdown menu, making it easy to find specific records.
---
## Project Files
### `app.py`
This is the main Python file that runs the entire application using Flask. It contains all the routes and logic for every page:
login, register, logout, dashboard (index), add expense, edit expense, delete expense, budget, and reports. It also uses the
`login_required` decorator to protect all pages that require authentication, redirecting unauthenticated users to the login
page.
### `finance.db`
This is the SQLite database file that stores all the application's data. It contains three tables:
- `users` — stores usernames and hashed passwords
- `expenses` — stores all expense records with amount, category, note, date, and a foreign key to the user
- `budgets` — stores the monthly income and spending limit per user per month
### `templates/layout.html`
This is the base HTML template that all other pages extend using Jinja2's template inheritance. It contains the navigation
bar, flash message display, footer, and links to Bootstrap, Chart.js, and the custom CSS and JavaScript files. Using a
shared layout avoids repetition and ensures a consistent look and feel across all pages.
### `templates/index.html`
The Dashboard page. It extends layout.html and displays the monthly summary cards, the recent expenses table, and the
doughnut chart. The chart data is passed from Flask as JSON and rendered using Chart.js.
### `templates/add.html`
A simple form for adding a new expense. It includes fields for amount, category (dropdown), date, and an optional note.
### `templates/edit.html`
Similar to add.html but pre-filled with the existing expense data. It allows the user to modify any field and save the
changes.
### `templates/history.html`
Displays all expenses in a table with Edit and Delete buttons for each row. Includes a category filter form at the top.
### `templates/budget.html`
A form for setting the monthly income and spending limit, along with a card showing the current month's budget settings.
### `templates/reports.html`
Displays two charts (pie and bar) and two tables showing spending by category and by month. Chart data is injected from
Flask using Jinja2 and rendered with Chart.js.
### `templates/login.html` and `templates/register.html`
Simple authentication forms for logging in and creating a new account.
### `static/styles.css`
Custom CSS file that styles the entire application. It uses multiple selectors including tag selectors (body, h1, footer),
class selectors (.card, .btn), and pseudo-class selectors (.card:hover, .form-control:focus). It defines properties such as
font-family, background-color, border-radius, box-shadow, and transform to create a clean and modern design.
### `static/script.js`
A small JavaScript file with two features: automatically setting today's date in any date input field on page load, and
automatically hiding flash messages after 4 seconds with a smooth fade-out animation.
---
## Design Decisions
### Why Flask and not Django?
Flask was chosen because it is lightweight and was taught in CS50. It gives full control over every route and template
without the extra complexity of Django's ORM and admin system. For a project of this size, Flask is the perfect fit.
### Why SQLite and not PostgreSQL?
SQLite requires no separate server setup and works perfectly for a single-user or small-scale application. The cs50 library
makes it very easy to execute SQL queries directly, which was also a key skill practiced throughout the course.
### Why Chart.js?
Chart.js is a simple, well-documented JavaScript library that integrates easily with Flask. It requires no backend changes
— the data is passed as JSON from Flask to the template, and Chart.js handles the rendering entirely on the client side.
### Why separate Edit and Delete instead of a modal?
A dedicated edit page was chosen over a popup modal because it is simpler to implement, easier to validate, and more
accessible on mobile devices. The delete action uses a JavaScript `confirm()` dialog to prevent accidental deletions.
---
## How to Run
```bash
cd project
pip install flask flask-session cs50
flask run
```
Then open the URL shown in the terminal in your browser.
---
## Technologies Used
- **Python 3** — backend logic
- **Flask** — web framework
- **SQLite** — database (via cs50 library)
- **Jinja2** — HTML templating
- **Bootstrap 4** — responsive UI components
- **Chart.js** — interactive charts
- **JavaScript** — date auto-fill and flash message auto-hide
- **HTML5 & CSS3** — structure and styling
