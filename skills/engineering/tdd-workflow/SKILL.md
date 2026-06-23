---
name: tdd-workflow
description: Use this skill when writing new features, fixing bugs, or refactoring code. Enforces test-driven development with 80%+ coverage including unit, integration, and E2E tests.
---

# Test-Driven Development Workflow

This skill ensures all code development follows TDD principles with comprehensive test coverage.

## When to Activate

- Writing new features or functionality
- Fixing bugs or issues
- Refactoring existing code
- Adding API endpoints
- Creating new components

## Core Principles

### 1. Tests BEFORE Code
ALWAYS write tests first, then implement code to make tests pass.

### 2. Coverage Requirements
- Minimum 80% coverage (unit + integration + E2E)
- All edge cases covered
- Error scenarios tested
- Boundary conditions verified

### 3. Test Types

#### 建議的整體測試分佈

- Unit + Property-Based → 邏輯正確性與邊界完整性
- Mutation Testing → 驗證測試品質
- Integration → 系統連接與契約
- E2E → 關鍵業務流程全覆蓋
- Visual Regression → UI 穩定性
- Chaos → 生產級可靠度

#### Unit Tests

- Individual functions and utilities
- Component logic (without side effects)
- Pure functions
- Helpers and utilities
- Fast feedback, run on every commit


#### Property-Based Tests

✅ 驗證「行為的不變量（invariants）」，而不是單一範例


- Generate many randomized inputs to validate general properties
- Assert logical invariants instead of fixed expected values
- Especially suitable for:

##### Parsers / serializers

- Form validators
- Date, number, state transformations
- Domain rules (e.g. pricing, permissions)

##### Characteristics

- Tests describe what must always be true
- Finds edge cases humans rarely think of
- Complements example‑based unit tests

##### Examples

- serialize(deserialize(x)) === x
- Sorting output is always ordered
- Total price is never negative

Typical tools

- golang: gopter / rapid
- JS/TS: fast-check
- Python: Hypothesis
- Haskell: QuickCheck
- .NET(C#): FsCheck

#### Mutation Tests

✅ 驗證「測試是不是在騙自己」

- Intentionally introduce small bugs (mutations) into production code
- Verify that tests fail when behavior is broken
- Measures test effectiveness, not coverage

##### What it catches

- Assertions that never fail
- Dead or meaningless tests
- Logic branches not truly validated

##### Common mutation types

- > → >=
- true → false
- Removing conditionals
- Replacing return values

##### Guidelines

- Run periodically (CI nightly / pre‑release)
- Focus on critical domain logic
- Do NOT require 100% mutation score

##### Typical tools

- JS/TS: Stryker
- JVM: PIT


#### Integration Tests

- API endpoints
- Database operations
- Service-to-service interactions
- External API calls (mocked or sandboxed)
- Verifies contracts between components

##### Scope

- More realistic than unit tests
- Slower but higher confidence
- Still deterministic

#### Chaos Tests

✅ 驗證「系統在錯誤發生時是否仍然可控」


- Introduce controlled failures into running systems
- Validate system resilience rather than correctness
- Focuses on behavior under stress

##### Failure scenarios

- Network latency / packet loss
- Service crash or restart
- Dependency timeout
- Partial data corruption

##### Assertions

- System does not cascade failure
- Retries / fallbacks work
- Errors are observable and logged
- User impact is limited

##### Where to run

- Staging (preferred)
- Production (with strict safety rails)

##### Typical tools

- Chaos Mesh / Litmus
- AWS Fault Injection Simulator
- Custom fault toggles


#### E2E Tests (Playwright)

- Critical user flows
- Complete workflows
- Browser automation
- UI interactions
- Business‑critical scenarios only

##### Guidelines

- Minimal count, maximal value
- Always assume flakiness risk
- No exhaustive UI coverage here


#### Visual Regression Tests

✅ 驗證「UI 是否被無意間改壞」


- Capture UI screenshots and compare pixel differences
- Detect accidental visual changes
- Independent of DOM structure or CSS logic

##### What it protects

- Layout breaks
- Color / spacing regressions
- Typography and branding issues

##### Best use cases

- Design systems
- Marketing pages
- Complex responsive layouts

##### Practices

- Controlled viewport sizes
- Stable test data
- Explicit review/approval of diffs

##### Typical tools

- Playwright screenshot assertions
- Percy / Chromatic
- Loki / BackstopJS



## TDD Workflow Steps

### Step 1: Write User Journeys
(for SDD codig, in `requirements.md`, or for vibe coding, in `plan.md` or some specific document.)
```
As a [role], I want to [action], so that [benefit]

Example:
As a user, I want to search for markets semantically,
so that I can find relevant markets even without exact keywords.
```

### Step 1.5: Create Test Decision Table Row (Draft)

Before writing the first failing test, create or update the related `TESTS.md` row:

- `Test ID` aligned with the intended test function/class naming
- `Type Tag`
- `Scenario`
- `Req Trace`
- `Owner`
- `Canonical Command`
- initial `Status` / `Risk` / `Result`

This keeps TDD connected to formal QA/QC governance instead of leaving test traceability as an afterthought.

### Step 2: Generate Test Cases
For each user journey, create comprehensive test cases:

```typescript
describe('Semantic Search', () => {
  it('returns relevant markets for query', async () => {
    // Test implementation
  })

  it('handles empty query gracefully', async () => {
    // Test edge case
  })

  it('falls back to substring search when Redis unavailable', async () => {
    // Test fallback behavior
  })

  it('sorts results by similarity score', async () => {
    // Test sorting logic
  })
})
```

### Step 3: Run Tests (They Should Fail)
```bash
npm test
# Tests should fail - we haven't implemented yet
```

### Step 4: Implement Code
Write minimal code to make tests pass:

```typescript
// Implementation guided by tests
export async function searchMarkets(query: string) {
  // Implementation here
}
```

### Step 5: Run Tests Again
```bash
npm test
# Tests should now pass
```

### Step 6: Refactor
Improve code quality while keeping tests green:
- Remove duplication
- Improve naming
- Optimize performance
- Enhance readability

#### Planning requirement for Refactor

When the surrounding workflow uses a planning artifact such as `tasks.md`, the REFRACTOR phase must not remain implicit.

- If work is broken into task items, either:
  - create explicit `RED` / `GREEN` / `REFACTOR` sub-steps for critical slices, or
  - explicitly state in the task acceptance/eval wording what refactor is expected after GREEN and how it will be verified.
- “Tests passed” is not enough to claim TDD is complete if the refactor step was never planned or never evidenced.

### Step 7: Verify Coverage
```bash
npm run test:coverage
# Verify 80%+ coverage achieved
```

## Testing Patterns

### Unit Test Pattern (Jest/Vitest)
```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from './Button'

describe('Button Component', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click</Button>)

    fireEvent.click(screen.getByRole('button'))

    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })
})
```

### API Integration Test Pattern
```typescript
import { NextRequest } from 'next/server'
import { GET } from './route'

describe('GET /api/markets', () => {
  it('returns markets successfully', async () => {
    const request = new NextRequest('http://localhost/api/markets')
    const response = await GET(request)
    const data = await response.json()

    expect(response.status).toBe(200)
    expect(data.success).toBe(true)
    expect(Array.isArray(data.data)).toBe(true)
  })

  it('validates query parameters', async () => {
    const request = new NextRequest('http://localhost/api/markets?limit=invalid')
    const response = await GET(request)

    expect(response.status).toBe(400)
  })

  it('handles database errors gracefully', async () => {
    // Mock database failure
    const request = new NextRequest('http://localhost/api/markets')
    // Test error handling
  })
})
```

### E2E Test Pattern (Playwright)
```typescript
import { test, expect } from '@playwright/test'

test('user can search and filter markets', async ({ page }) => {
  // Navigate to markets page
  await page.goto('/')
  await page.click('a[href="/markets"]')

  // Verify page loaded
  await expect(page.locator('h1')).toContainText('Markets')

  // Search for markets
  await page.fill('input[placeholder="Search markets"]', 'election')

  // Wait for debounce and results
  await page.waitForTimeout(600)

  // Verify search results displayed
  const results = page.locator('[data-testid="market-card"]')
  await expect(results).toHaveCount(5, { timeout: 5000 })

  // Verify results contain search term
  const firstResult = results.first()
  await expect(firstResult).toContainText('election', { ignoreCase: true })

  // Filter by status
  await page.click('button:has-text("Active")')

  // Verify filtered results
  await expect(results).toHaveCount(3)
})

test('user can create a new market', async ({ page }) => {
  // Login first
  await page.goto('/creator-dashboard')

  // Fill market creation form
  await page.fill('input[name="name"]', 'Test Market')
  await page.fill('textarea[name="description"]', 'Test description')
  await page.fill('input[name="endDate"]', '2025-12-31')

  // Submit form
  await page.click('button[type="submit"]')

  // Verify success message
  await expect(page.locator('text=Market created successfully')).toBeVisible()

  // Verify redirect to market page
  await expect(page).toHaveURL(/\/markets\/test-market/)
})
```

## Test File Organization

Take typescript for example:

```
src/
├── components/
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx          # Unit tests
│   │   └── Button.stories.tsx       # Storybook
│   └── MarketCard/
│       ├── MarketCard.tsx
│       └── MarketCard.test.tsx
├── app/
│   └── api/
│       └── markets/
│           ├── route.ts
│           └── route.test.ts         # Integration tests
└── e2e/
    ├── markets.spec.ts               # E2E tests
    ├── trading.spec.ts
    └── auth.spec.ts
```

## Mocking External Services

For development phase, mock external services. But for project finalization phase, write another tests for integration/e2e/chaos.

### Supabase Mock
```typescript
jest.mock('@/lib/supabase', () => ({
  supabase: {
    from: jest.fn(() => ({
      select: jest.fn(() => ({
        eq: jest.fn(() => Promise.resolve({
          data: [{ id: 1, name: 'Test Market' }],
          error: null
        }))
      }))
    }))
  }
}))
```

### Redis Mock
```typescript
jest.mock('@/lib/redis', () => ({
  searchMarketsByVector: jest.fn(() => Promise.resolve([
    { slug: 'test-market', similarity_score: 0.95 }
  ])),
  checkRedisHealth: jest.fn(() => Promise.resolve({ connected: true }))
}))
```

### OpenAI Mock
```typescript
jest.mock('@/lib/openai', () => ({
  generateEmbedding: jest.fn(() => Promise.resolve(
    new Array(1536).fill(0.1) // Mock 1536-dim embedding
  ))
}))
```

## Test Coverage Verification

### Run Coverage Report
```bash
npm run test:coverage
```

### Coverage Thresholds
```json
{
  "jest": {
    "coverageThresholds": {
      "global": {
        "branches": 80,
        "functions": 80,
        "lines": 80,
        "statements": 80
      }
    }
  }
}
```

## Common Testing Mistakes to Avoid

### ❌ WRONG: Testing Implementation Details
```typescript
// Don't test internal state
expect(component.state.count).toBe(5)
```

### ✅ CORRECT: Test User-Visible Behavior
```typescript
// Test what users see
expect(screen.getByText('Count: 5')).toBeInTheDocument()
```

### ❌ WRONG: Brittle Selectors
```typescript
// Breaks easily
await page.click('.css-class-xyz')
```

### ✅ CORRECT: Semantic Selectors
```typescript
// Resilient to changes
await page.click('button:has-text("Submit")')
await page.click('[data-testid="submit-button"]')
```

### ❌ WRONG: No Test Isolation
```typescript
// Tests depend on each other
test('creates user', () => { /* ... */ })
test('updates same user', () => { /* depends on previous test */ })
```

### ✅ CORRECT: Independent Tests
```typescript
// Each test sets up its own data
test('creates user', () => {
  const user = createTestUser()
  // Test logic
})

test('updates user', () => {
  const user = createTestUser()
  // Update logic
})
```

## Continuous Testing

### Watch Mode During Development
```bash
npm test -- --watch
# Tests run automatically on file changes
```

### Pre-Commit Hook
```bash
# Runs before every commit
npm test && npm run lint
```

### CI/CD Integration
```yaml
# GitHub Actions
- name: Run Tests
  run: npm test -- --coverage
- name: Upload Coverage
  uses: codecov/codecov-action@v3
```

## Best Practices

1. **Write Tests First** - Always TDD
2. **One Assert Per Test** - Focus on single behavior
3. **Descriptive Test Names** - Explain what's tested
4. **Arrange-Act-Assert** - Clear test structure
5. **Mock External Dependencies** - Isolate unit tests
6. **Test Edge Cases** - Null, undefined, empty, large
7. **Test Error Paths** - Not just happy paths
8. **Keep Tests Fast** - Unit tests < 50ms each
9. **Clean Up After Tests** - No side effects
10. **Review Coverage Reports** - Identify gaps

## Success Metrics

- 80%+ code coverage achieved
- All tests passing (green)
- No skipped or disabled tests
- Fast test execution (< 30s for unit tests)
- E2E tests cover critical user flows
- Tests catch bugs before production

---

**Remember**: Tests are not optional. They are the safety net that enables confident refactoring, rapid development, and production reliability.
