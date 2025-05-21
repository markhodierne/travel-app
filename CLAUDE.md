**IMPORTANT FOR CLAUDE: Reference this file before implementing anything**

# Project: Travel Planning Application

## Project Overview

The Travel Planning Application is a web-based tool built with Django that allows users to create, manage, and organize their trips. Users can plan itineraries, add activities, and check weather conditions for their destinations.

Key features include:
1. Trip management (creation, editing, deletion)
2. Itinerary planning with activities
3. Weather checking for destinations

## Tech Stack

- Languages: Python 3.8+
- Frameworks: Django 4.2+
- Database: PostgreSQL
- Frontend: Django Templates with basic CSS and JavaScript enhancements
- Libraries: Django Rest Framework, Requests (for API calls), Pillow (for image handling)
- Package Manager: pip

## Code Style & Conventions

### Import/Module Standards

- Group imports in the following order:
  1. Standard library imports
  2. Django imports
  3. Third-party app imports
  4. Local app imports
- Use absolute imports for clarity
- Alphabetize imports within each group

### Naming Conventions

- Functions: snake_case (create_trip, get_weather)
- Classes/Models: CamelCase singular nouns (Trip, Activity)
- Constants: UPPER_CASE_WITH_UNDERSCORES
- Files: snake_case (models.py, trip_views.py)
- Templates: app_name/model_action.html (trips/trip_detail.html)
- URL patterns: snake_case descriptive names

### Patterns to Follow

- Model-Template-View (MTV) Django pattern
- Class-based views for complex functionality
- Form classes for input validation
- Service pattern for external API calls (weather)
- Object-Oriented Programming principles:
  - Encapsulation
  - Single Responsibility
  - Composition over inheritance

## Development Workflow

- Branch strategy: Feature Branch Workflow
  - Create branches for each feature/fix (e.g., "feature/trip-creation", "fix/weather-api")
- Commit message format: Conventional Commits
  - feat: A new feature
  - fix: A bug fix
  - docs: Documentation changes
  - style: Code style changes
  - refactor: Code changes that neither fix bugs nor add features
  - test: Adding or modifying tests
  - chore: Changes to build process or auxiliary tools
- PR requirements:
  - All tests passing
  - Code follows style guidelines
  - Documentation updated

## Testing Strategy

- Test frameworks: Django's built-in TestCase
- Coverage requirements: Core functionality must have tests
- Test naming conventions: test_should_description_when_condition

## Environment Setup

- Required environment variables:
  - DATABASE_URL
  - SECRET_KEY
  - WEATHER_API_KEY
- Setup commands: See Common Commands section
- Local development server: Django development server

## Common Commands

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Run tests
python manage.py test
```

## Project Structure

Key directories and their purpose:

- `/travel_project/` - Main project settings
- `/trips/` - Trip management app
- `/itineraries/` - Itinerary planning app
- `/weather/` - Weather integration app
- `/templates/` - Project-wide templates
- `/docs/` - Project documentation

## Review Process Guidelines

Before submitting any code, ensure the following steps are completed:

1. **Run all lint, check and test commands**
   - `python manage.py check`
   - `python manage.py test`

2. **Review outputs and iterate until all issues are resolved**

3. **Assess compliance**:
   For each standard, explicitly state ✅ or ❌ and explain why:

   - Code style and formatting: Does the code follow PEP 8 and Django style?
   - Naming conventions: Do names follow our conventions?
   - Architecture patterns: Does code follow MTV pattern and OOP principles?
   - Error handling: Are errors properly caught and handled?
   - Test coverage: Are key functions tested?
   - Documentation: Are docstrings and comments added where needed?

4. **Self-review checklist**:
   - [ ] Code follows defined patterns
   - [ ] No debug/commented code
   - [ ] Error handling implemented
   - [ ] Tests written and passing
   - [ ] Documentation updated

## Development Principles

- **KISS (Keep It Simple, Stupid)**: Prefer simple solutions over complex ones
- **DRY (Don't Repeat Yourself)**: Avoid code duplication
- **Convention over Configuration**: Follow Django conventions when possible

## Error Handling

- Use Django's built-in error handling for HTTP errors
- Implement try-except blocks for operations that might fail (API calls, etc.)
- Display user-friendly error messages
- Log errors appropriately

## Known Issues & Workarounds

- Weather API integration requires an API key
- PostgreSQL must be installed and configured locally for development

## References

- [Django Documentation](https://docs.djangoproject.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- Functional Specification: `/docs/FUNCTIONAL_SPEC.md`
- Architectural Specification: `/docs/ARCHITECTURAL_SPEC.md`