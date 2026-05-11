# TODO - Auth + User-owned Scan History

- [x] Add authentication dependency (Flask-Login)
- [x] Create User model and register it in models package
- [x] Initialize Flask-Login in app factory
- [x] Add `user_id` ownership to Scan model
- [x] Update ScannerEngine to persist scans with owner
- [x] Add auth routes: register/login/logout
- [x] Protect scan/history/results routes and enforce ownership checks
- [x] Update base layout with auth-aware navigation
- [x] Add login/register templates
- [ ] Run quick validation (import/app startup level)
- [x] Update TODO progress
