# Member 2 - Backend, Uploads, API, and Database

## Your responsibility
Build the Flask server that receives videos, calls the AI module, stores results, and sends results to the frontend.

## Step-by-step tasks
1. Create a Flask application and a health-check route.
2. Create a video-upload endpoint that validates file type and handles missing or invalid files.
3. Save uploaded videos safely in the uploads/ folder and use unique filenames.
4. Create an analysis endpoint that passes the saved video path to the AI processing function.
5. Connect the AI module through a clearly defined Python function or API interface.
6. Create SQLite tables or a simple results store for analysis history if time permits.
7. Return consistent JSON responses for success, processing, and errors.
8. Write setup instructions and test each endpoint with sample requests.

## Expected deliverables
- Working Flask app.
- Video upload and analysis API endpoints.
- Consistent JSON response format.
- Database or result-storage implementation if time permits.
- requirements.txt and backend run instructions.

## Suggested files
```text
backend/app.py, backend/routes.py, backend/database.py, uploads/, requirements.txt
```

## Integration handoff
Agree with Member 1 on endpoint names and response JSON. Agree with Members 3 and 4 on how the video path and analysis results are passed.

## Before you finish
- Run your module and test it.
- Tell the team what files you created or changed.
- Share exact run commands and dependencies.
- Commit and push your work to your assigned Git branch.
