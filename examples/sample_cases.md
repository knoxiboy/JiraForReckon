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
