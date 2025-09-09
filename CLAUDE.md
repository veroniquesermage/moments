# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Moments is a gift management application with an Angular frontend and FastAPI backend. The application helps groups of people manage gift lists, reservations, and sharing among members.

## Developer Context & Preferences

**Developer Profile**: Java senior learning Python/FastAPI
**Communication Style**: Direct, step-by-step explanations, optimal solutions first
**Special Considerations**: TSA - prefer structured responses, avoid cognitive overload

## Common Development Commands

### Backend (FastAPI + SQLAlchemy + PostgreSQL)
```bash
# Development environment
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run backend development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Database migrations
alembic upgrade head
alembic revision --autogenerate -m "description"

# Run tests
pytest
pytest backend/tests/test_specific_file.py
pytest -v  # verbose output

# Docker development
docker-compose up -d  # Start all services
docker-compose -f docker-compose.prod.yml up -d  # Production
docker exec -it moments-backend bash  # Backend container shell
docker exec -it moments-postgres psql -U Mom3ntsAdm1n moments  # Database shell
```

### Frontend (Angular 19)
```bash
# Development environment
cd frontend
npm install

# Development server with proxy
npm run start:proxy  # Recommended for development (uses proxy.conf.json)
npm start  # Direct start without proxy

# Build
npm run build
ng build --configuration production

# Run tests
npm test
ng test --watch=false --browsers=ChromeHeadless  # Single run
```

### Database Operations
```bash
# Enter PostgreSQL container
docker exec -it moments-postgres psql -U Mom3ntsAdm1n moments

# Common PostgreSQL commands
\dt  # List tables
\d table_name  # Describe table
\q  # Quit
```

## Architecture Overview

### Backend Architecture (FastAPI)

**Core Structure:**
- **`app/main.py`**: Application entry point with FastAPI app, middleware, CORS, OpenTelemetry instrumentation
- **`app/database.py`**: Database connection, session management, SQLAlchemy async engine
- **`app/router.py`**: Main router including all sub-routers

**Layer Organization:**
- **`app/models/`**: SQLAlchemy ORM models (Gift, User, Group, UserGroup, etc.)
- **`app/services/`**: Business logic layer (GiftService, GroupService, UserGroupService)
- **`app/routes/`**: FastAPI route definitions (gift_route, group_route, auth_route, etc.)
- **`app/schemas/`**: Pydantic models for request/response validation
- **`app/core/`**: Core utilities (config, logger, JWT, enums)
- **`app/dependencies/`**: FastAPI dependency providers (current_user, group_id)
- **`app/middleware/`**: Custom middleware (database session handling)

**Key Patterns:**
- **Service Layer Pattern**: Business logic is encapsulated in service classes with static methods
- **Repository Pattern**: Database operations are handled through SQLAlchemy ORM with eager loading
- **Dependency Injection**: FastAPI's dependency system for database sessions and user authentication
- **Schema Validation**: Pydantic models for all API inputs/outputs

### Frontend Architecture (Angular)

**Core Structure:**
- **`src/app/app.routes.ts`**: Main routing configuration with lazy-loaded modules
- **`src/core/services/`**: Angular services for API communication and state management
- **`src/pages/`**: Feature modules (auth, dashboard, groupe, profile, compte-tiers)
- **`src/shared/`**: Shared components and utilities

**Key Features:**
- **Lazy Loading**: Route-based code splitting for performance
- **Service-Based Architecture**: Services handle API calls and business logic
- **Component-Based**: Modular component structure
- **SCSS Styling**: Custom styling with retro-terminal theme

### Database Design

**Key Entities:**
- **`utilisateur`** (User): Core user entity with Google OAuth integration
- **`groupe`** (Group): Gift groups with invitation codes
- **`user_group`**: Many-to-many relationship between users and groups with roles
- **`cadeaux`** (Gift): Gift items with status tracking and priority
- **`gift_delivery`**: Delivery information for gifts
- **`gift_shared`**: Gift sharing between users
- **`idees_cadeaux`**: Gift ideas that can become actual gifts

**Important Relationships:**
- Users belong to multiple groups with different roles (ADMIN/MEMBRE)
- Gifts can be reserved, taken, or shared between group members
- Complex gift lifecycle with status transitions and expiration dates

## Configuration & Environment

### Environment Files
- **Development**: `.env` (backend), `environment.ts` (frontend)
- **Production**: `.env.prod` (backend), `environment.prod.ts` (frontend)

### Key Configuration Areas
- **Database**: PostgreSQL with PgBouncer connection pooling
- **Authentication**: Google OAuth2 with JWT tokens
- **Monitoring**: OpenTelemetry + Prometheus metrics
- **Email**: Mailjet integration for invitations and notifications

### Docker Architecture
- **postgres**: PostgreSQL 16 database
- **pgbouncer**: Connection pooling for database
- **backend**: FastAPI application
- **frontend**: Angular application served by nginx

## Development Patterns

### Backend Patterns
- **Static Service Methods**: All business logic methods are static class methods
- **Async/Await**: Full async support with SQLAlchemy async sessions
- **Eager Loading**: Use `selectinload()` to avoid N+1 queries
- **Transaction Management**: Automatic rollback on SQLAlchemy exceptions
- **Trace Logging**: OpenTelemetry integration with structured logging

### Frontend Patterns
- **Reactive Programming**: RxJS observables for data handling
- **Component Communication**: Services for cross-component communication
- **Route Guards**: Authentication and authorization guards
- **Interceptors**: HTTP interceptors for token management and error handling

### Database Patterns
- **Migration-First**: All schema changes through Alembic migrations
- **Index Strategy**: Composite indexes for query optimization
- **Soft Deletes**: Some entities use status flags instead of hard deletes
- **Timezone Handling**: Paris timezone used for date operations (`now_paris()`)

## Testing Strategy

### Testing Directives for Claude

**MANDATORY TESTING WORKFLOW:**

1. **Before any code modification**: Always run existing tests to ensure current codebase is stable
   ```bash
   # Backend
   pytest

   # Frontend
   ng test --watch=false --browsers=ChromeHeadless
   ```

2. **After any code implementation**:
   - Write comprehensive tests covering the new/modified functionality
   - Ensure all tests pass before considering the task complete
   - Test coverage should include happy path, edge cases, and error scenarios

3. **Test-First Approach for new features**:
   - Write failing tests first (when possible)
   - Implement code to make tests pass
   - Refactor while keeping tests green

**Code Quality Gates:**
- **No code without tests**: Every new function, method, or feature must have corresponding tests
- **No broken tests**: All existing tests must continue to pass
- **Business logic coverage**: Focus on service layer testing for backend, component logic for frontend
- **Error handling**: Test error scenarios and edge cases explicitly

**Testing Standards:**
- **Backend**: Minimum 80% test coverage on service layer
- **Frontend**: Component logic and service methods must be tested
- **Integration**: Critical user workflows must have integration tests
- **Performance**: Include performance regression tests for optimizations

**Test Categories to Always Include:**
```python
# Backend example structure for any new service method
async def test_[method_name]_success():
    """Test successful execution"""
    pass

async def test_[method_name]_validation_error():
    """Test input validation failures"""
    pass

async def test_[method_name]_permission_denied():
    """Test unauthorized access"""
    pass

async def test_[method_name]_not_found():
    """Test resource not found scenarios"""
    pass
```

**Before submitting any code change:**
1. Run full test suite: `pytest` and `ng test`
2. Check test coverage: `pytest --cov=app --cov-report=term-missing`
3. Verify no regressions in existing functionality
4. Confirm new functionality is properly tested

### Backend Testing Framework & Structure

**Testing Stack:**
- **Framework**: pytest with async support
- **Database**: Dedicated test database (separate from dev/prod)
- **Fixtures**: pytest fixtures for database sessions, test users, and test data
- **Mocking**: unittest.mock for external dependencies (Google OAuth, Mailjet)

**Test Organization:**
```
backend/tests/
├── conftest.py                 # Shared fixtures and test configuration
├── test_models/               # Model validation tests
│   ├── test_user.py
│   ├── test_gift.py
│   └── test_group.py
├── test_services/             # Business logic tests
│   ├── test_gift_service.py
│   ├── test_group_service.py
│   └── test_auth_service.py
├── test_routes/              # API endpoint tests
│   ├── test_gift_route.py
│   ├── test_group_route.py
│   └── test_auth_route.py
└── test_integration/         # End-to-end integration tests
    ├── test_gift_lifecycle.py
    └── test_group_management.py
```

**Testing Patterns for Services:**
- **Arrange-Act-Assert**: Clear test structure
- **Database Isolation**: Each test runs in its own transaction that rolls back
- **Test Database**: Use a dedicated test database (e.g., `moments_test`)
- **Mock External APIs**: Mock Google OAuth, Mailjet, and other external dependencies
- **Test Data Factories**: Create consistent test data using factories or fixtures
- **Edge Case Testing**: Test business logic edge cases (expired reservations, permission checks)

**Example Test Structure:**
```python
# test_services/test_gift_service.py
import pytest
from app.services.gift_service import GiftService
from app.core.enum import GiftStatusEnum

@pytest.mark.asyncio
async def test_create_gift_success(db_session, test_user, test_gift_data):
    """Test successful gift creation"""
    # Arrange
    gift_create = GiftCreate(**test_gift_data)

    # Act
    result = await GiftService.create_gift(db_session, test_user, gift_create)

    # Assert
    assert result.nom == test_gift_data["nom"]
    assert result.destinataire_id == test_user.id
    assert result.statut == GiftStatusEnum.DISPONIBLE

@pytest.mark.asyncio
async def test_create_gift_unauthorized(db_session, test_user, test_gift_data):
    """Test gift creation for another user (should fail)"""
    # Arrange
    gift_create = GiftCreate(**{**test_gift_data, "destinataire_id": 999})

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await GiftService.create_gift(db_session, test_user, gift_create)

    assert exc_info.value.status_code == 403
```

**Critical Test Scenarios for Backend:**
- **Gift Lifecycle**: Creation → Reservation → Status changes → Sharing → Delivery
- **Permission Testing**: User can only modify their own gifts/groups
- **Expiration Logic**: Reservation expiration and cleanup
- **Group Management**: Join/leave groups, role changes, invitation codes
- **Authentication Flow**: JWT token validation, Google OAuth integration
- **Database Constraints**: Foreign key violations, unique constraints
- **Business Rules**: Gift priority updates, sharing calculations, delivery tracking

### Frontend Testing Framework & Structure

**Testing Stack:**
- **Framework**: Jasmine + Karma for unit tests, Cypress for E2E
- **Utilities**: Angular Testing Library, rxjs-marbles for observable testing
- **Mocking**: jasmine.createSpy(), HttpClientTestingModule for HTTP mocking

**Test Organization:**
```
frontend/src/
├── app/component.spec.ts      # Component unit tests
├── core/services/             # Service tests alongside services
│   ├── gift.service.spec.ts
│   ├── group.service.spec.ts
│   └── auth.service.spec.ts
└── e2e/                      # End-to-end tests (Cypress)
    ├── gift-management.cy.ts
    ├── group-creation.cy.ts
    └── user-authentication.cy.ts
```

**Testing Patterns for Frontend:**
- **Component Testing**: Test component logic, inputs/outputs, DOM interactions
- **Service Testing**: Mock HTTP calls, test observable streams
- **Integration Testing**: Test component-service interactions
- **E2E Testing**: Full user workflows across multiple pages

**Example Test Structure:**
```typescript
// core/services/gift.service.spec.ts
describe('GiftService', () => {
  let service: GiftService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [GiftService]
    });
    service = TestBed.inject(GiftService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  it('should create gift successfully', () => {
    // Arrange
    const giftData = { nom: 'Test Gift', description: 'Test' };
    const expectedResponse = { id: 1, ...giftData };

    // Act
    service.createGift(giftData).subscribe(result => {
      // Assert
      expect(result).toEqual(expectedResponse);
    });

    // Assert HTTP call
    const req = httpMock.expectOne('/api/cadeaux');
    expect(req.request.method).toBe('POST');
    req.flush(expectedResponse);
  });
});
```

**Critical Test Scenarios for Frontend:**
- **Authentication Flow**: Login/logout, token refresh, protected routes
- **Gift Management**: CRUD operations, status updates, sharing functionality
- **Group Management**: Creating/joining groups, member management
- **Form Validation**: Input validation, error display, submission handling
- **Responsive Design**: Mobile/desktop layout testing
- **Error Handling**: Network errors, validation errors, user feedback

### Integration Testing Strategy

**Database Integration Tests:**
- **Dedicated Test Database**: Use `moments_test` database, never dev/prod
- **Migration Testing**: Run migrations on test database before tests
- **Constraint Testing**: Test foreign key constraints and cascading deletes
- **Transaction Rollback**: Each test rolls back to maintain clean state

**API Integration Tests:**
- **End-to-End Workflows**: Complete user scenarios across multiple endpoints
- **Authentication Integration**: Test JWT flow with real token validation
- **Error Scenarios**: Network failures, timeout handling, retry logic

**Test Data Management:**
- **Fixtures**: Reusable test data sets for different scenarios
- **Factories**: Dynamic test data generation for varied scenarios
- **Cleanup**: Proper test data cleanup and isolation

### Test Commands & Configuration

**Backend Testing Commands:**
```bash
# Run all tests
pytest

# Run specific test file
pytest backend/tests/test_services/test_gift_service.py

# Run tests with coverage
pytest --cov=app --cov-report=html

# Run tests in parallel
pytest -n auto

# Run only fast tests (exclude integration)
pytest -m "not integration"
```

**Frontend Testing Commands:**
```bash
# Unit tests
ng test
ng test --watch=false --browsers=ChromeHeadless

# E2E tests
npx cypress run
npx cypress open

# Test coverage
ng test --code-coverage
```

### Testing Best Practices for This Codebase

1. **Mock External Dependencies**: Always mock Google OAuth, Mailjet, and other external APIs
2. **Test Business Logic First**: Focus on service layer testing before route testing
3. **Use Dedicated Test Database**: Always use `moments_test` database, never dev/prod
4. **Test Permission Systems**: Verify role-based access control thoroughly
5. **Test Edge Cases**: Expiration logic, concurrent operations, edge date/time scenarios
6. **Maintain Test Data**: Use factories for consistent, maintainable test data
7. **Test Error Scenarios**: Network failures, validation errors, business rule violations

## Production Deployment

The README.md contains detailed production deployment instructions including:
- Environment file modifications for production
- Docker image building and deployment
- Database migration execution
- Monitoring setup

Key production considerations:
- Environment-specific configuration files
- PgBouncer configuration for production database connections
- Cron jobs for database cleanup
- Log file management and backup procedures

## Security Considerations

- **Authentication**: Google OAuth2 integration with JWT tokens
- **Authorization**: Role-based access control (ADMIN/MEMBRE)
- **Database Security**: Connection pooling, parameterized queries
- **CORS Configuration**: Specific origins allowed in production
- **Input Validation**: Pydantic schemas for all API endpoints
- **Secret Management**: Environment variables for sensitive configuration
