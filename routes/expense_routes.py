from flask import Blueprint, request, jsonify
from models import Expense, ExpenseHead, Category, SubCategory, db
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

expense_bp = Blueprint('expense', __name__)

# Get all expense heads with total amounts (for pie chart)
@expense_bp.route('/heads', methods=['GET'])
@jwt_required()
def get_expense_heads():
    current_user_id = get_jwt_identity()

    # Fetch only the Expense Heads created by the logged-in user
    heads = ExpenseHead.query.filter_by(user_id=current_user_id).all()

    response = []
    for head in heads:
        total_amount = db.session.query(func.sum(Expense.amount)).join(SubCategory).join(Category).filter(
            Category.expense_head_id == head.id, Expense.user_id == current_user_id
        ).scalar() or 0

        response.append({"id": head.id, "name": head.name, "total_amount": total_amount})
    
    return jsonify(response), 200


# Add a new expense head
@expense_bp.route('/heads', methods=['POST'])
@jwt_required()
def add_expense_head():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    name = data.get('name')

    if ExpenseHead.query.filter_by(name=name, user_id=current_user_id).first():
        return jsonify({"message": "Expense head already exists for this user"}), 400

    new_head = ExpenseHead(name=name, user_id=current_user_id)
    db.session.add(new_head)
    db.session.commit()

    return jsonify({"message": "Expense head added successfully"}), 201


# Get categories within a specific expense head
@expense_bp.route('/categories/<int:head_id>', methods=['GET'])
@jwt_required()
def get_categories(head_id):
    current_user_id = get_jwt_identity()

    # Ensure the expense head belongs to the user
    head = ExpenseHead.query.filter_by(id=head_id, user_id=current_user_id).first()
    if not head:
        return jsonify({"message": "Expense head not found or does not belong to you"}), 403

    categories = Category.query.filter_by(expense_head_id=head_id).all()
    return jsonify([{"id": cat.id, "name": cat.name} for cat in categories]), 200


# Add a new category under an expense head
@expense_bp.route('/categories', methods=['POST'])
@jwt_required()
def add_category():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    name = data.get('name')
    head_id = data.get('head_id')

    # Ensure the expense head belongs to the user
    head = ExpenseHead.query.filter_by(id=head_id, user_id=current_user_id).first()
    if not head:
        return jsonify({"message": "Expense head not found or does not belong to you"}), 403

    if Category.query.filter_by(name=name, expense_head_id=head_id).first():
        return jsonify({"message": "Category already exists for this head"}), 400

    new_category = Category(name=name, expense_head_id=head_id)
    db.session.add(new_category)
    db.session.commit()

    return jsonify({"message": "Category added successfully"}), 201


# Fetch expense reports by filters (head/category/subcategory/date range)
@expense_bp.route('/reports', methods=['GET'])
@jwt_required()
def get_reports():
    current_user_id = get_jwt_identity()
    head_id = request.args.get('head_id')
    category_id = request.args.get('category_id')
    subcategory_id = request.args.get('subcategory_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Expense.query.filter_by(user_id=current_user_id)  # Filter by user

    if head_id:
        query = query.join(SubCategory).join(Category).filter(Category.expense_head_id == head_id)
    if category_id:
        query = query.filter(Expense.subcategory_id == subcategory_id)
    if start_date and end_date:
        query = query.filter(Expense.timestamp.between(start_date, end_date))

    results = query.all()
    response = [{"title": exp.title, "amount": exp.amount, "timestamp": exp.timestamp} for exp in results]
    return jsonify(response), 200


# Add a new expense entry
@expense_bp.route('/add', methods=['POST'])
@jwt_required()
def add_expense():
    data = request.get_json()
    title = data.get('title')
    amount = data.get('amount')
    subcategory_id = data.get('subcategory_id')

    # Check for required fields
    if not title or not amount or not subcategory_id:
        return jsonify({"message": "Title, amount, and expense head are required"}), 400

    # Get the logged-in user
    user_id = get_jwt_identity()

    # Create new expense
    new_expense = Expense(
        title=title,
        amount=amount,
        description=data.get('description', ""),  # Optional
        user_id=user_id,
        subcategory_id=subcategory_id
    )

    db.session.add(new_expense)
    db.session.commit()
    
    return jsonify({"message": "Expense added successfully"}), 201



# Get subcategories under a category
@expense_bp.route('/subcategories/<int:category_id>', methods=['GET'])
@jwt_required()
def get_subcategories(category_id):
    current_user_id = get_jwt_identity()

    # Ensure the category belongs to the user
    category = Category.query.join(ExpenseHead).filter(
        Category.id == category_id, ExpenseHead.user_id == current_user_id
    ).first()

    if not category:
        return jsonify({"message": "Category not found or does not belong to you"}), 403

    subcategories = SubCategory.query.filter_by(category_id=category_id).all()
    return jsonify([{"id": sub.id, "name": sub.name} for sub in subcategories]), 200

# Add a new subcategory under a category
@expense_bp.route('/subcategories', methods=['POST'])
@jwt_required()
def add_subcategory():
    data = request.get_json()
    name = data.get('name')
    category_id = data.get('category_id')

    if SubCategory.query.filter_by(name=name, category_id=category_id).first():
        return jsonify({"message": "Subcategory already exists"}), 400

    new_subcategory = SubCategory(name=name, category_id=category_id)
    db.session.add(new_subcategory)
    db.session.commit()

    return jsonify({"message": "Subcategory added successfully"}), 201

