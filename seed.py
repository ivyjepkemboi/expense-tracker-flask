# seed_data.py
from app import create_app
from db import db
from models import ExpenseHead, Category, SubCategory

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()

    # Add some ExpenseHeads
    family_expense = ExpenseHead(name='Family Expense')
    projects_investment = ExpenseHead(name='Projects/Investment')
    family_friends = ExpenseHead(name='Family/Friends')

    db.session.add_all([family_expense, projects_investment, family_friends])
    db.session.commit()

    # Example: categories for Family Expense
    utilities = Category(name='Utilities', expense_head_id=family_expense.id)
    food = Category(name='Food', expense_head_id=family_expense.id)
    fuel = Category(name='Fuel', expense_head_id=family_expense.id)

    db.session.add_all([utilities, food, fuel])
    db.session.commit()

    # Example: subcategories for Utilities
    electricity = SubCategory(name='Electricity', category_id=utilities.id)
    internet = SubCategory(name='Internet', category_id=utilities.id)
    water = SubCategory(name='Water Bill', category_id=utilities.id)
    db.session.add_all([electricity, internet, water])
    db.session.commit()

    print("Database seeded successfully!")
