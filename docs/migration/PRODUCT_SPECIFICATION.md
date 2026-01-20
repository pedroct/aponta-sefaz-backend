# 📋 PRODUCT SPECIFICATION: Apontamentos (Time Tracking)

## Executive Summary

**Apontamentos** is a web-based time tracking and work management system that integrates seamlessly with Azure DevOps. It enables teams to log work hours, track task progress, and maintain synchronized data between local records and Azure DevOps work items. The system provides a hierarchical view of epics, features, user stories, and tasks, with real-time hour aggregation and automatic synchronization.

---

## 1. Product Purpose & Vision

### Primary Goals

1. **Centralized Time Tracking**: Provide a single interface for developers to log hours spent on specific tasks
2. **Real-time Synchronization**: Keep local time tracking data synchronized with Azure DevOps work items
3. **Hierarchical Work Visibility**: Display work items in a tree structure (Epic → Feature → Story → Task) with aggregate metrics
4. **Progress Monitoring**: Automatically calculate completed work and remaining effort based on logged hours
5. **Team Accountability**: Track who worked on what, when, and for how long

### Key Problems Solved

- ❌ **Manual Updates**: Developers no longer need to manually update Azure DevOps work items
- ❌ **Data Silos**: All time tracking data stays synchronized across systems
- ❌ **Time Loss**: Eliminate time spent navigating between multiple tools
- ❌ **Visibility Gaps**: Real-time aggregate hours per person, task, epic, and day

---

## 2. Core Features

### 2.1 Timesheet Grid Interface

A hierarchical, spreadsheet-like view displaying:

**Left Columns (Metadata)**:
- **ID**: Unique Azure DevOps work item identifier
- **Title**: Work item name with icon indicating type (Epic 🟣, Feature 🟢, Story 🔵, Task 🟡, Bug 🔴)
- **Estimate (E)**: Original estimated hours (from Azure DevOps `OriginalEstimate`)
- **Total**: Aggregate completed hours across all logged time

**Time Columns**:
- Weekly grid showing Monday through Sunday
- Each cell displays hours logged on that specific day
- Cell values come from logged "Apontamentos" entries

**Footer Row**:
- Daily totals: Sum of all hours logged per day
- Weekly total: Sum of all hours logged in the week
- Automatic calculation with color coding for overload

### 2.2 Modal: Add Time Entry (Apontamento)

A dialog form for logging work hours with the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| **Usuário** | Display + Avatar | Auto | Current logged-in user |
| **Tarefa** | Autocomplete Combobox | Yes | Select/search work item by ID or title |
| **Data** | Date Picker | Yes | When the work was performed |
| **Duração** | Time Input + Shortcuts | Yes | Hours worked (HH:mm format or quick buttons) |
| **Tipo Atividade** | Dropdown | Yes | Category: Desenvolvimento, Documentação, Reunião, Review, Outro |
| **Comentário** | Text Area | No | Description of work performed |

**Quick Duration Buttons**: 
- `+0.5h` | `+1h` | `+2h` | `+4h` for faster entry

**On Submit**:
1. Save to local `Apontamentos` table
2. Automatically update Azure DevOps work item:
   - Increment `CompletedWork`
   - Decrement `RemainingWork` (minimum 0)
3. Refresh timesheet grid with new data
4. Show confirmation toast notification

### 2.3 Work Item Hierarchy Display

**Structure**: Epic > Feature > User Story > Task/Bug

**Features**:
- Expandable/collapsible tree view
- Nested indent visualization
- Parent aggregation: Parent's total = sum of all children
- Recursive calculation for multi-level nesting

**Display Logic**:
- Tasks/Bugs: Show only direct logged hours
- Stories/Features/Epics: Show aggregated hours from all descendants

### 2.4 Search & Autocomplete

**Task Search** (in Modal):
- Real-time search by work item ID or title
- Minimum 2 characters to trigger search
- Results filtered by project and work item type
- Debounced to reduce API calls
- Cached results with React Query
- Shows ID, Title, Type, and current hours

---

## 3. Architecture & Technical Design

### 3.1 Data Model

#### WorkItems Table
```
id (PK) → Azure DevOps ID
title → Work item title
type → Epic | Feature | User Story | Task | Bug
originalEstimate → Original estimated hours
remainingWork → Hours left to complete
completedWork → Hours already logged
projectId → Reference to project
```

#### WorkItemHierarchy Table
```
parentId → Parent work item ID
childId → Child work item ID
relationship → Type of relationship
```

#### Apontamentos Table
```
id (PK) → Auto-increment
workItemId (FK) → WorkItems.id
userId → Azure DevOps user ID
date → When work was performed
hours → Decimal hours logged
activityType → Desenvolvimento | Documentação | etc.
comment → User notes
createdAt → Timestamp
syncedToAzure → Boolean flag
```

### 3.2 Synchronization Rules

**On Save Apontamento**:
1. Write to local `Apontamentos` table
2. Calculate new totals:
   ```
   NewCompletedWork = CurrentCompletedWork + LoggedHours
   NewRemainingWork = Max(0, CurrentRemainingWork - LoggedHours)
   ```
3. Send PATCH request to Azure DevOps API:
   ```
   PATCH /api/wit/workitems/{id}?api-version=7.2-preview.3
   [
     { op: "add", path: "/fields/Microsoft.VSTS.Scheduling.CompletedWork", value: NewCompletedWork },
     { op: "add", path: "/fields/Microsoft.VSTS.Scheduling.RemainingWork", value: NewRemainingWork }
   ]
   ```
4. Mark `syncedToAzure = true` in local record
5. Refresh parent aggregations recursively

**Conflict Resolution**:
- If Azure update fails, log error but keep local record
- Retry mechanism with exponential backoff
- Manual sync button available for users

### 3.3 Backend Architecture

**Technology Stack**:
- **Server**: Express.js with TypeScript
- **Database**: SQLite/Drizzle ORM
- **External API**: Azure DevOps REST API (v7.2-preview.3)
- **Authentication**: Azure DevOps personal access token (PAT)

**Key Endpoints**:

```
GET  /api/work-items              → List all cached work items
GET  /api/work-items/search       → Search by title (WIQL)
POST /api/apontamentos            → Create new time entry
GET  /api/apontamentos            → List time entries (filtered)
PATCH /api/work-items/{id}/sync   → Sync specific item to Azure
GET  /api/projects                → List available projects
```

**Synchronization Service** (`sync-service.ts`):
- Periodic sync of local changes to Azure
- Intelligent conflict detection
- Rollback capability for failed updates
- Audit trail for all sync operations

### 3.4 Frontend Architecture

**Technology Stack**:
- **Framework**: React 18 with TypeScript
- **UI Components**: shadcn/ui (Radix UI primitives)
- **State Management**: TanStack Query (React Query)
- **Forms**: React Hook Form + Zod validation
- **Styling**: Tailwind CSS

**Key Components**:

```
├── PaginaPrincipal
│   ├── TimesheetGrid
│   │   ├── HierarchyRow (expandable)
│   │   ├── TimeCell (daily hours)
│   │   └── FooterRow (totals)
│   └── ModalAdicionarTempo
│       ├── UserDisplay
│       ├── TaskAutocomplete
│       ├── DatePicker
│       ├── DurationInput
│       ├── ActivityTypeSelect
│       └── CommentField
```

**Custom Hooks**:
- `useAtividades()` → Fetch and manage time entries
- `useSearchWorkItems()` → Search tasks with debouncing
- `useCurrentUser()` → Get authenticated user info
- `useApi()` → Generic API call wrapper

---

## 4. User Workflows

### Workflow 1: Log Daily Hours

1. User opens Apontamentos app
2. Clicks "Adicionar Apontamento" button
3. Modal opens with pre-selected user
4. Searches for task in "Tarefa" field (e.g., "Implementar login")
5. Task appears in dropdown → User clicks to select
6. Selects date (defaults to today)
7. Enters duration via input or quick button (+2h)
8. Selects activity type (Desenvolvimento)
9. Adds optional comment ("Implemented user authentication")
10. Clicks "Salvar"
11. System:
    - Saves to `Apontamentos` table
    - Updates Azure DevOps work item
    - Refreshes timesheet grid
    - Shows success toast

### Workflow 2: Review Weekly Hours

1. User opens timesheet view
2. Sees hierarchical structure of all assigned work
3. Views hours logged per day in grid
4. Reviews daily totals in footer
5. Notices overload (e.g., 10+ hours in one day)
6. Can expand parent items to see child task breakdown
7. Uses visual indicators to identify problem areas

### Workflow 3: Sync Issues Recovery

1. Time entry saved locally but Azure update failed
2. Retry notification appears
3. User clicks "Retry Sync"
4. System attempts PATCH again with backoff
5. On success: Toast confirmation, status updates
6. On failure: Error details shown, manual escalation option

---

## 5. User Interface Design

### Color Scheme & Visual Language

- **Type Icons**:
  - Epic: 🟣 Purple
  - Feature: 🟢 Green
  - User Story: 🔵 Blue
  - Task: 🟡 Yellow
  - Bug: 🔴 Red

- **Cell Colors**:
  - < 4 hours: 🟢 Green (normal)
  - 4-8 hours: 🟡 Yellow (acceptable)
  - 8-10 hours: 🟠 Orange (warning)
  - > 10 hours: 🔴 Red (overload)

### Responsiveness

- **Desktop (1920px+)**: Full timesheet with all columns visible
- **Tablet (1024px)**: Horizontal scroll, core columns fixed
- **Mobile**: Simplified card view, modal-first interaction

---

## 6. Integration Points

### Azure DevOps Integration

**Query: Fetch Work Item Hierarchy**
```
SELECT [System.Id]
FROM WorkItemLinks
WHERE [Source].[System.TeamProject] = @project
  AND [Source].[System.WorkItemType] = 'Epic'
  AND [System.Links.LinkType] = 'System.LinkTypes.Hierarchy-Forward'
  AND [Target].[System.WorkItemType] IN ('Feature', 'User Story', 'Task', 'Bug')
MODE (Recursive)
```

**Update: Sync Completed Work**
```
PATCH /_apis/wit/workitems/{id}?api-version=7.2-preview.3
Content-Type: application/json-patch+json

[
  {
    "op": "add",
    "path": "/fields/Microsoft.VSTS.Scheduling.CompletedWork",
    "value": 8.5
  },
  {
    "op": "add",
    "path": "/fields/Microsoft.VSTS.Scheduling.RemainingWork",
    "value": 1.5
  }
]
```

### Authentication

- PAT (Personal Access Token) stored securely in backend
- User identity from Azure DevOps user context
- Session management via HTTP-only cookies

---

## 7. Validation & Business Rules

### Input Validation

| Field | Rules |
|-------|-------|
| **Duração** | 0.25 - 12 hours per entry, decimal precision |
| **Data** | Cannot be in future, max 30 days in past |
| **Tarefa** | Must exist in current project |
| **Comentário** | Max 500 characters |

### Business Rules

1. **Hours Constraints**:
   - Cannot log negative hours
   - Total daily hours capped at 24
   - Warning if > 10 hours in a day

2. **Sync Constraints**:
   - CompletedWork cannot exceed OriginalEstimate (with warning)
   - RemainingWork never negative (automatic floor at 0)
   - Only Tasks/Bugs directly updated in Azure; parent totals calculated locally

3. **Access Control**:
   - Users can only log hours for themselves (configurable)
   - Managers can optionally review/approve entries
   - Admins can manually adjust entries

---

## 8. Error Handling & Edge Cases

### Azure DevOps Connection Issues

- **Scenario**: Azure API unreachable
- **Behavior**: Save locally, queue for retry, show warning
- **Recovery**: Automatic retry on next sync cycle

### Duplicate Entries

- **Scenario**: User clicks "Save" twice
- **Behavior**: Detect duplicate (same user, task, date within 1 minute)
- **Action**: Show confirmation dialog before allowing duplicate

### Timezone Handling

- Store all dates in UTC
- Display in user's local timezone
- Handle DST transitions gracefully

### Data Consistency

- Database transactions for atomic operations
- Rollback on failed sync
- Audit log for all modifications

---

## 9. Performance Considerations

### Caching Strategy

- **React Query**: Cache work items for 5 minutes
- **Search Results**: Cache for 2 minutes
- **User's Time Entries**: Cache for 1 minute
- **Manual Refresh**: Always available via button

### Pagination

- Timesheet: Load one week at a time
- History: Load 50 entries per page with infinite scroll
- Search: Show top 20 results

### Database Indexing

```sql
CREATE INDEX idx_apontamentos_user_date ON Apontamentos(userId, date);
CREATE INDEX idx_apontamentos_workitem ON Apontamentos(workItemId);
CREATE INDEX idx_hierarchy_parent ON WorkItemHierarchy(parentId);
CREATE INDEX idx_hierarchy_child ON WorkItemHierarchy(childId);
```

---

## 10. Success Metrics & KPIs

### User Adoption

- **Target**: 90% of team members logging entries within 2 weeks
- **Measure**: Active users per week

### Data Quality

- **Target**: 95% of time entries synced successfully on first attempt
- **Measure**: Failed sync ratio

### Time Savings

- **Target**: Average 5 minutes saved per user per day vs. manual updates
- **Measure**: User feedback surveys

### System Reliability

- **Target**: 99.5% uptime
- **Measure**: API availability monitoring

---

## 11. Roadmap & Future Features

### Phase 1 (Current - MVP)
✅ Basic time entry logging
✅ Work item hierarchy display
✅ Azure DevOps synchronization
✅ Search/autocomplete

### Phase 2 (Q1 2026)
- 🔄 Timesheet templates and recurring entries
- 🔄 Manager approval workflow
- 🔄 Bulk edit capabilities
- 🔄 Export to Excel/PDF

### Phase 3 (Q2 2026)
- 📊 Analytics dashboard (hours by person, project, week)
- 📧 Email notifications for approvals
- 🔔 Slack integration for reminders
- 📱 Mobile app (React Native)

### Phase 4 (Q3+ 2026)
- 🤖 AI-powered time estimation
- 📅 Calendar view
- 💰 Billing integration
- 📈 Burndown chart integration

---

## 12. Deployment & Maintenance

### Environments

- **Development**: Local setup with test Azure project
- **Staging**: Pre-production mirror environment
- **Production**: Live system with real Azure DevOps projects

### Deployment Process

```bash
npm install           # Install dependencies
npm run build        # Build TypeScript
npm run test         # Run test suite
npm run start        # Launch server
```

### Monitoring & Logging

- Application logs: Stored in `.logs/` directory
- API response times: Tracked per endpoint
- Sync failures: Alerted to admin dashboard
- User activity: Audit trail in database

### Database Migrations

```bash
npm run db:push      # Apply Drizzle migrations
```

---

## 13. Security & Compliance

### Data Protection

- ✅ HTTPS-only communication
- ✅ SQL injection prevention (parameterized queries)
- ✅ XSS protection via React's built-in sanitization
- ✅ CSRF tokens on state-changing operations
- ✅ Rate limiting on API endpoints

### Authentication & Authorization

- ✅ Azure DevOps OAuth (recommended future)
- ✅ Current: PAT-based authentication
- ✅ Role-based access control (RBAC)
- ✅ Session timeout: 30 minutes idle

### Compliance

- 📋 GDPR: User data deletion on request
- 📋 SOC 2: Audit logging and retention
- 📋 Data backup: Daily to cloud storage

---

## 14. Documentation & Support

### User Documentation

- In-app tooltips on all major fields
- Video tutorials for common workflows
- Knowledge base with FAQ
- Email support channel

### Developer Documentation

- API documentation (OpenAPI/Swagger)
- Architecture decision records (ADRs)
- Database schema documentation
- Setup guide for new developers

---

## 15. Glossary

| Term | Definition |
|------|-----------|
| **Apontamento** | A single time entry logging hours for a specific task |
| **Timesheet** | The main grid view showing all hours across a week |
| **Work Item** | Any task, story, feature, or epic in Azure DevOps |
| **Hierarchy** | Parent-child relationship (Epic → Feature → Story → Task) |
| **Sync** | Two-way synchronization between local DB and Azure DevOps |
| **WIQL** | Work Item Query Language (Azure DevOps query syntax) |
| **PAT** | Personal Access Token (authentication credential) |

---

## 16. Appendix: Example User Journey

**Maria - Software Developer**

**Monday 9:00 AM**
- Opens Apontamentos
- Clicks "Adicionar Apontamento"
- Searches for "Implement login form"
- Selects it, confirms date (today)
- Clicks "+2h" button
- Selects "Desenvolvimento"
- Adds comment: "Built HTML form and basic validation"
- Saves

**System Action**:
1. Writes to Apontamentos table
2. Azure DevOps work item #1234:
   - CompletedWork: 6 → 8
   - RemainingWork: 4 → 2
3. Timesheet grid updates showing "2.0" in Monday column
4. Parent epic recalculates aggregate hours

**Maria's Benefit**: ✅ 30 seconds to log hours | ✅ Automatic Azure sync | ✅ Aggregate visibility

---

**Document Version**: 1.0
**Last Updated**: January 18, 2026
**Status**: Final ✅
