# Activity: Configure Observability & Logging

**Activity ID**: TBD
**Order**: 8
**Phase**: Configure
**Dependencies**: Predecessor: BSP-07 (Create Welcome Page & Verify)

## Description

Configure Observability & Logging

## Guidance

# Configure Observability & Logging

## Objective

Set up three-tier logging infrastructure for backend operations (`logs/app.log`), frontend interactions (`logs/gui.log`), and AI token consumption (`logs/consumption.log`). This provides observability from day one and enables EST workflow token tracking for estimate calibration.

---

## Prerequisites

- BSP-07 complete (welcome page verified)
- Project structure exists
- Django settings configured
- Static files directory exists

---

## Goals

### Goal 1: Backend Operation Logging

**What**: All backend operations log to `logs/app.log` with informative context

**Why**: Enable troubleshooting without reproduction by logging who, what, where, when, and why for every significant operation

**Success Criteria**:
- [ ] Django LOGGING configuration added to settings
- [ ] RotatingFileHandler configured (10MB, 5 backups)
- [ ] Log format includes module, function, line number, and context
- [ ] All service methods log entry, exit, and errors
- [ ] Log messages follow `.windsurf/rules/informative-logging.md` pattern

**Implementation**:

# Skill: Django Logging Setup

**Capability Domain**: BACKEND_LOGGING
**Technology Stack**: Django+Python

## Overview

Configure Django's LOGGING settings to implement informative, structured logging with file rotation. Enables effective troubleshooting by logging who, what, why, where, and when for every significant operation. Supports three log files: `app.log` (backend operations), `gui.log` (frontend events), and `consumption.log` (token tracking).

## Reference Implementation

### Pattern 1: Django LOGGING Configuration

Add to `{project_name}/settings.py`:

```python
import os
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} [{name}:{funcName}:{lineno}] {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'json': {
            'format': '{message}',
            'style': '{',
        },
    },
    'handlers': {
        'app_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'app.log',
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'gui_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'gui.log',
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'consumption_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'consumption.log',
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 5,
            'formatter': 'json',  # JSON format for EST workflow parsing
        },
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['app_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        '{project_name}': {
            'handlers': ['app_file', 'console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'gui': {
            'handlers': ['gui_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'consumption': {
            'handlers': ['consumption_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['app_file', 'console'],
        'level': 'INFO',
    },
}
```

### Pattern 2: Create Logs Directory

Add to project initialization (e.g., `manage.py` or `wsgi.py`):

```python
import os
from pathlib import Path

# Ensure logs directory exists
BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)
```

Or create via shell script in BSP workflow:

```bash
mkdir -p logs
touch logs/.gitkeep

# Add to .gitignore
cat >> .gitignore << 'EOF'

# Logs
logs/*.log
!logs/.gitkeep
EOF
```

### Pattern 3: Informative Logging in Services

Include context for troubleshooting in all log messages:

```python
import logging

logger = logging.getLogger(__name__)

class PlaybookService:
    """Service layer for playbook operations."""
    
    def create_playbook(self, name, description, category, author):
        """
        Create a new playbook.
        
        :param name: Playbook name
        :param description: Playbook description
        :param category: Category (e.g., 'development', 'testing')
        :param author: User instance
        :return: Created Playbook instance
        :raises ValidationError: If validation fails
        """
        logger.info(
            f"[{__name__}.create_playbook] Starting playbook creation | "
            f"user_id={author.id} | name={name} | category={category}"
        )
        
        try:
            # Validation
            if not name or len(name) < 3:
                raise ValidationError("Playbook name must be at least 3 characters")
            
            # Create playbook
            playbook = Playbook.objects.create(
                name=name,
                description=description,
                category=category,
                author=author,
                status='draft',
                version='0.1'
            )
            
            logger.info(
                f"[{__name__}.create_playbook] Playbook created successfully | "
                f"user_id={author.id} | playbook_id={playbook.id} | "
                f"name={playbook.name} | version={playbook.version}"
            )
            
            return playbook
            
        except ValidationError as e:
            logger.warning(
                f"[{__name__}.create_playbook] Validation failed | "
                f"user_id={author.id} | name={name} | error={str(e)}"
            )
            raise
            
        except Exception as e:
            logger.error(
                f"[{__name__}.create_playbook] Unexpected error | "
                f"user_id={author.id} | name={name} | "
                f"error_type={type(e).__name__} | error={str(e)}",
                exc_info=True
            )
            raise
```

### Pattern 4: Logging in Views

```python
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

logger = logging.getLogger(__name__)

@login_required
def playbook_create(request):
    """Create new playbook."""
    logger.info(
        f"[{__name__}.playbook_create] View accessed | "
        f"user_id={request.user.id} | method={request.method}"
    )
    
    if request.method == 'POST':
        try:
            service = PlaybookService()
            playbook = service.create_playbook(
                name=request.POST.get('name'),
                description=request.POST.get('description'),
                category=request.POST.get('category'),
                author=request.user
            )
            
            logger.info(
                f"[{__name__}.playbook_create] Playbook created via view | "
                f"user_id={request.user.id} | playbook_id={playbook.id}"
            )
            
            messages.success(request, f'Playbook "{playbook.name}" created successfully')
            return redirect('playbook_detail', playbook_id=playbook.id)
            
        except ValidationError as e:
            logger.warning(
                f"[{__name__}.playbook_create] Form validation failed | "
                f"user_id={request.user.id} | error={str(e)}"
            )
            messages.error(request, str(e))
    
    return render(request, 'playbooks/create.html', {
        'page_title': 'Create Playbook'
    })
```

### Pattern 5: Logging in Models (Signals)

```python
import logging
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Playbook)
def log_playbook_save(sender, instance, created, **kwargs):
    """Log playbook creation/update."""
    action = 'created' if created else 'updated'
    logger.info(
        f"[signals.log_playbook_save] Playbook {action} | "
        f"playbook_id={instance.id} | name={instance.name} | "
        f"author_id={instance.author.id} | version={instance.version} | "
        f"status={instance.status}"
    )

@receiver(pre_delete, sender=Playbook)
def log_playbook_delete(sender, instance, **kwargs):
    """Log playbook deletion."""
    logger.warning(
        f"[signals.log_playbook_delete] Playbook being deleted | "
        f"playbook_id={instance.id} | name={instance.name} | "
        f"author_id={instance.author.id}"
    )
```

### Pattern 6: Logging Database Queries (Debug)

For development debugging, enable SQL query logging:

```python
# In settings.py (DEBUG mode only)
if DEBUG:
    LOGGING['loggers']['django.db.backends'] = {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': False,
    }
```

### Pattern 7: Request/Response Middleware Logging

Create custom middleware for request/response logging:

```python
# {app_name}/middleware/logging_middleware.py
import logging
import time

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    """Log all HTTP requests and responses."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Log request
        start_time = time.time()
        user_id = request.user.id if request.user.is_authenticated else 'anonymous'
        
        logger.info(
            f"[RequestLoggingMiddleware] Request started | "
            f"method={request.method} | path={request.path} | "
            f"user_id={user_id}"
        )
        
        # Process request
        response = self.get_response(request)
        
        # Log response
        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"[RequestLoggingMiddleware] Request completed | "
            f"method={request.method} | path={request.path} | "
            f"user_id={user_id} | status={response.status_code} | "
            f"duration_ms={duration_ms:.2f}"
        )
        
        return response
```

Add to `settings.py`:

```python
MIDDLEWARE = [
    # ... other middleware ...
    '{app_name}.middleware.logging_middleware.RequestLoggingMiddleware',
]
```

## Informative Logging Checklist

Every log message should include:

- ✅ **Location**: `[module.function]` prefix
- ✅ **Action**: What operation is being performed
- ✅ **Context**: Key identifiers (user_id, entity_id, etc.)
- ✅ **Result**: Success/failure indication
- ✅ **Error details**: Exception type and message (if applicable)

**Good Example**:
```python
logger.info(
    f"[playbook_service.create_playbook] Playbook created successfully | "
    f"user_id={user.id} | playbook_id={playbook.id} | name={playbook.name}"
)
```

**Bad Example**:
```python
logger.info("Playbook created")  # Missing context, location, identifiers
```

## Testing Logging

Verify logging is working:

```python
# tests/test_logging.py
import logging
from pathlib import Path
from django.test import TestCase

class LoggingTestCase(TestCase):
    """Test logging configuration."""
    
    def test_app_log_exists(self):
        """Verify app.log is created."""
        log_file = Path('logs/app.log')
        
        # Trigger a log entry
        logger = logging.getLogger('test')
        logger.info("Test log entry")
        
        # Verify file exists
        self.assertTrue(log_file.exists())
    
    def test_log_rotation(self):
        """Verify log rotation is configured."""
        logger = logging.getLogger('test')
        handler = logger.handlers[0]
        
        self.assertEqual(handler.maxBytes, 10 * 1024 * 1024)
        self.assertEqual(handler.backupCount, 5)
```

## Common Patterns

### Pattern: Logging with Timing

```python
import time

start_time = time.time()
# ... operation ...
duration_ms = (time.time() - start_time) * 1000

logger.info(
    f"[{__name__}.operation] Completed | "
    f"duration_ms={duration_ms:.2f}"
)
```

### Pattern: Logging with Exception Context

```python
try:
    # ... operation ...
except SpecificException as e:
    logger.error(
        f"[{__name__}.operation] Operation failed | "
        f"context_id={id} | error={str(e)}",
        exc_info=True  # Include full traceback
    )
    raise
```

### Pattern: Conditional Debug Logging

```python
if logger.isEnabledFor(logging.DEBUG):
    logger.debug(
        f"[{__name__}.operation] Debug info | "
        f"variable_state={expensive_to_compute()}"
    )
```

## Integration with EST Workflow

The `consumption.log` uses JSON format for EST-08 parsing:

```python
import json
import logging

consumption_logger = logging.getLogger('consumption')

def log_token_consumption(scenario_id, user_id, tokens_used, model, sprint=1):
    """Log token consumption for EST workflow."""
    entry = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'scenario_id': scenario_id,
        'user_id': user_id,
        'sprint': sprint,
        'tokens_used': tokens_used,
        'model': model,
        'operation': 'implement',
        'status': 'completed'
    }
    consumption_logger.info(json.dumps(entry))
```

## References

- For sprint close and token consumption tracking, see Activity EST-08 (Sprint Close and Rebaseline)
- Django Logging Documentation: https://docs.djangoproject.com/en/stable/topics/logging/

---

### Goal 2: Frontend Interaction Logging

**What**: All HTMX interactions and user actions log to `logs/gui.log`

**Why**: Track user behavior, debug frontend issues, and understand interaction patterns

**Success Criteria**:
- [ ] JavaScript Logger class created in `static/js/logger.js`
- [ ] HTMX event listeners configured (beforeRequest, afterRequest, responseError)
- [ ] Django backend endpoint created (`/api/log/gui/`)
- [ ] Frontend logs sent to backend for persistence
- [ ] Console integration for development debugging

**Implementation**: See **Skill** `skills/htmx_frontend_logging.md`

---

### Goal 3: Token Consumption Tracking

**What**: AI token usage logged to `logs/consumption.log` in JSON format

**Why**: Enable EST workflow sprint-by-sprint calibration via velocity factor calculation and K-token baseline updates

**Success Criteria**:
- [ ] TokenTracker utility class created
- [ ] Scenario-level token tracking implemented
- [ ] JSON log format compatible with EST-08 Sprint Close & Rebaseline
- [ ] Consumption logger configured with JSON formatter
- [ ] Sprint report generation utility available

**Implementation**: See **Skill** `skills/claude_token_tracking.md`

---

## Implementation Steps

### Step 1: Create Logs Directory Structure

```bash
mkdir -p logs
touch logs/.gitkeep

# Add logs to .gitignore (keep structure, ignore content)
cat >> .gitignore << 'EOF'

# Logs
logs/*.log
!logs/.gitkeep
EOF
```

**Deliverable**: `logs/` directory with `.gitkeep`, `.gitignore` updated

---

### Step 2: Configure Backend Logging

**Objective**: Add Django LOGGING configuration for three log files

**Tasks**:
1. Add LOGGING dictionary to `{project_name}/settings.py`
2. Configure formatters (verbose, simple, json)
3. Configure handlers (app_file, gui_file, consumption_file, console)
4. Configure loggers (django, {project_name}, gui, consumption)
5. Add informative logging to service methods

**Reference**: See **Skill** `skills/django_logging_setup.md` for:
- Complete LOGGING configuration
- RotatingFileHandler setup
- Logger usage patterns in services, views, models
- Informative logging message format
- Testing logging configuration

**Deliverable**: Django LOGGING configured, backend operations logging to `app.log`

---

### Step 3: Configure Frontend Logging

**Objective**: Create JavaScript logger and backend endpoint for GUI events

**Tasks**:
1. Create `static/js/logger.js` with Logger class
2. Add HTMX event listeners (beforeRequest, afterRequest, responseError, etc.)
3. Create Django view `{app_name}/views/logging_views.py::log_gui_event`
4. Add URL route `/api/log/gui/`
5. Include logger in `templates/base.html`
6. Test frontend logging in browser console

**Reference**: See **Skill** `skills/htmx_frontend_logging.md` for:
- JavaScript Logger class implementation
- HTMX event logging patterns
- Django backend endpoint
- User action logging
- JavaScript error catching
- Performance considerations (throttling, batching)

**Deliverable**: Frontend interactions logging to `gui.log`

---

### Step 4: Configure Token Consumption Tracking

**Objective**: Create TokenTracker utility for EST workflow integration

**Tasks**:
1. Create `{app_name}/utils/token_tracker.py` with TokenTracker class
2. Add consumption logger to Django settings (JSON formatter)
3. Create utility functions for parsing consumption.log
4. Create Django management command for sprint reports
5. Document integration with BPE workflow

**Reference**: See **Skill** `skills/claude_token_tracking.md` for:
- TokenTracker class implementation
- JSON log format for EST-08
- Parsing and aggregation utilities
- Sprint report generation
- Integration with Claude API
- Velocity factor calculation

**Deliverable**: Token consumption logging to `consumption.log` in EST-compatible format

---

### Step 5: Verify All Logs Are Working

**Verification Checklist**:

1. **Backend Logging**:
   ```bash
   # Start Django server
   python manage.py runserver
   
   # Trigger some operations (create, read, update)
   # Check logs/app.log for entries
   tail -f logs/app.log
   ```

2. **Frontend Logging**:
   ```bash
   # Open browser to http://localhost:8000
   # Open browser console (F12)
   # Click buttons, submit forms
   # Verify console shows log messages
   # Check logs/gui.log for persisted entries
   tail -f logs/gui.log
   ```

3. **Token Consumption**:
   ```python
   # In Django shell
   from {app_name}.utils.token_tracker import log_token_consumption
   
   log_token_consumption(
       scenario_id="TEST-01",
       user_id=1,
       tokens_used=1000,
       model="claude-3-5-sonnet-20241022",
       sprint=1
   )
   ```
   ```bash
   # Check logs/consumption.log
   cat logs/consumption.log
   # Should show JSON entry
   ```

4. **Log Rotation**:
   ```bash
   # Verify file size limits
   ls -lh logs/
   # Should show maxBytes=10MB configured
   ```

**Deliverable**: All three logs verified and working

---

### Step 6: Commit Logging Infrastructure

```bash
git add logs/.gitkeep .gitignore
git add {project_name}/settings.py
git add static/js/logger.js
git add {app_name}/views/logging_views.py
git add {app_name}/utils/token_tracker.py
git add {app_name}/urls.py
git add templates/base.html

git commit -m "feat(observability): configure three-tier logging infrastructure

Add comprehensive logging for backend operations, frontend interactions,
and AI token consumption:

Backend (logs/app.log):
- Django LOGGING configuration with RotatingFileHandler
- Informative logging pattern (module:function:line + context)
- Logs for services, views, models, and signals

Frontend (logs/gui.log):
- JavaScript Logger class with console and backend integration
- HTMX event listeners for all interactions
- Django endpoint for GUI log collection
- User action and error logging

Token Consumption (logs/consumption.log):
- TokenTracker utility for scenario-level tracking
- JSON format compatible with EST-08 Sprint Close workflow
- Parsing and aggregation utilities
- Sprint report generation command

Enables:
- Troubleshooting without reproduction
- User behavior analysis
- EST workflow token calibration

Refs: .windsurf/rules/informative-logging.md
Refs: .windsurf/workflows/EST/EST-08-Sprint_Close_and_Rebaseline.md"
```

**Deliverable**: Logging infrastructure committed to repository

---

## Success Criteria

- [x] **Logs directory** created with `.gitkeep`
- [x] **`.gitignore`** updated to exclude `logs/*.log`
- [x] **Backend logging** configured in Django settings
- [x] **app.log** receiving backend operation logs
- [x] **gui.log** receiving frontend interaction logs
- [x] **consumption.log** receiving token consumption in JSON format
- [x] **Log rotation** configured (10MB, 5 backups)
- [x] **Informative logging** pattern followed (module:function:line + context)
- [x] **JavaScript Logger** created and included in base template
- [x] **HTMX events** automatically logged
- [x] **TokenTracker** utility created
- [x] **All logs verified** and working
- [x] **Infrastructure committed** to repository

---

## Artifacts Produced

- `logs/` directory structure
- `logs/.gitkeep`
- `.gitignore` (updated)
- Django LOGGING configuration in `{project_name}/settings.py`
- `static/js/logger.js` (JavaScript Logger class)
- `{app_name}/views/logging_views.py` (GUI log endpoint)
- `{app_name}/utils/token_tracker.py` (TokenTracker utility)
- `{app_name}/management/commands/sprint_token_report.py` (optional)
- URL route for `/api/log/gui/`
- Updated `templates/base.html` (includes logger.js)

---

## Artifacts Consumed

- `.windsurf/rules/informative-logging.md` — Logging format requirements
- `.windsurf/workflows/EST/EST-08-Sprint_Close_and_Rebaseline.md` — consumption.log format spec
- `.windsurf/workflows/BSP/skills/django_logging_setup.md` — Backend logging implementation
- `.windsurf/workflows/BSP/skills/htmx_frontend_logging.md` — Frontend logging implementation
- `.windsurf/workflows/BSP/skills/claude_token_tracking.md` — Token tracking implementation

---

## Notes

### EST Workflow Integration

The `consumption.log` format is designed for EST-08 Sprint Close & Rebaseline:

1. **Sprint Close** reads `consumption.log` to collect actuals
2. **Velocity Factor** computed: `VF = Actual Tokens / Estimated Tokens`
3. **K-token baselines** updated in Reference Table
4. **Monte Carlo** re-run with calibrated data
5. **Forecasts refined** (P50/P80/P95)

This creates a continuous improvement loop where estimates get more accurate with each sprint.

### Informative Logging Pattern

Every log message should answer:
- **Where**: `[module.function:line]`
- **What**: Operation being performed
- **Who**: `user_id=X`
- **Context**: Entity IDs, parameters
- **Result**: Success/failure, error details

**Example**:
```python
logger.info(
    f"[playbook_service.create_playbook:45] Playbook created | "
    f"user_id={user.id} | playbook_id={playbook.id} | name={playbook.name}"
)
```

### Performance Considerations

- **Backend logs**: RotatingFileHandler prevents disk space issues
- **Frontend logs**: Sent async, non-blocking
- **Token logs**: JSON format for fast parsing
- **Optional**: Implement log batching for high-traffic applications (see htmx_frontend_logging.md)

### Technology Alternatives

This activity is platform-agnostic. If not using Django+HTMX+Claude:
- **Backend**: Adapt patterns to Flask, FastAPI, Express, etc.
- **Frontend**: Adapt to React, Vue, Angular, etc.
- **AI**: Adapt to OpenAI, Gemini, etc.

The Skills provide Django+HTMX+Claude implementations, but the goals and success criteria remain the same.
