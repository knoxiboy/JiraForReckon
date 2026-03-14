# Examples for Jira Ticket Evaluator

## Example 1: Feature Request (PROJ-101)
**Summary**: Implement User Profile Page
**Description**: 
As a user, I want to see a profile page with my avatar, display name, and bio.
**Acceptance Criteria**:
1. A new route `/profile` should be created.
2. The page must display the User's Avatar image.
3. The page must display the User's Bio text.
4. If no bio is set, display a placeholder "No bio provided".

**PR Diff Snippet**:
```diff
+ route('/profile', ProfilePage)
+ class ProfilePage extends Component {
+   render() {
+     return <div>{this.user.avatar} {this.user.name}</div>
+   }
+ }
```
**Expected Evaluation**: Partial (Missing Bio and Placeholder logic).

---

## Example 2: Bug Report (PROJ-202)
**Summary**: Fix logout button not clearing session cookie
**Description**: 
Currently, clicking logout clears local storage but the session cookie `auth_token` remains.
**Acceptance Criteria**:
1. Clicking logout must clear `localStorage`.
2. Clicking logout must explicitly expire the `auth_token` cookie.

**PR Diff Snippet**:
```diff
  function logout() {
    localStorage.clear();
+   document.cookie = "auth_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
  }
```
**Expected Evaluation**: Pass.

---

## Example 3: Refactor / Cleanup (PROJ-303)
**Summary**: Refactor authentication middleware to use strategy pattern
**Description**: 
The current authentication middleware uses a long `if/else` chain to handle different auth methods (JWT, API Key, OAuth). Refactor this into a Strategy Pattern for maintainability.
**Acceptance Criteria**:
1. Create an `AuthStrategy` interface/base class with a `verify(request)` method.
2. Create concrete strategy classes: `JwtStrategy`, `ApiKeyStrategy`, `OAuthStrategy`.
3. The middleware must delegate to the appropriate strategy based on the request header.
4. Existing unit tests must continue to pass (no behavioral change).
5. Remove the legacy `if/else` chain from `auth_middleware.py`.

**PR Diff Snippet**:
```diff
+ class AuthStrategy(ABC):
+     @abstractmethod
+     def verify(self, request): ...
+
+ class JwtStrategy(AuthStrategy):
+     def verify(self, request):
+         token = request.headers.get('Authorization')
+         return jwt.decode(token, SECRET_KEY)
+
+ class ApiKeyStrategy(AuthStrategy):
+     def verify(self, request):
+         key = request.headers.get('X-API-Key')
+         return db.api_keys.validate(key)
+
- def auth_middleware(request):
-     if request.headers.get('Authorization'):
-         # JWT logic...
-     elif request.headers.get('X-API-Key'):
-         # API Key logic...
+ STRATEGIES = {
+     'Authorization': JwtStrategy(),
+     'X-API-Key': ApiKeyStrategy(),
+ }
+
+ def auth_middleware(request):
+     for header, strategy in STRATEGIES.items():
+         if request.headers.get(header):
+             return strategy.verify(request)
```
**Expected Evaluation**: Partial (Missing `OAuthStrategy` implementation and no evidence of test suite passing).
