#!/bin/bash

# Move database and schema files to models
mv database.py src/models/
mv db_schema.py src/models/

# Move API file
mv api.py src/api/

# Move business logic
mv business_logic.py src/business/

# Move test files
mv test_system.py tests/

# Move documentation files
mv README.md docs/
mv API_DOCUMENTATION.md docs/
mv DATABASE_SETUP.md docs/
mv ENHANCEMENTS.md docs/
mv FIRST_TIME_SETUP.md docs/
mv OFFLINE_GUIDE.md docs/
mv QUICKSTART.md docs/
mv IMPLEMENTATION_SUMMARY.txt docs/

# Keep app.py and requirements.txt in root
# Keep .env.example, .gitignore, LICENSE in root

echo "Files moved successfully"
