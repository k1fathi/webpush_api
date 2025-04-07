# A/B Test Management Wireframes

## 1. A/B Test Listing Page

## 2. A/B Test Details Page
// ...wireframe for details page (e.g. test info, variations, results)...

## API Endpoints Usage
- Create Test: POST /api/v1/abtests
- List Tests: GET /api/v1/abtests?skip=0&limit=100
- Get Test Details: GET /api/v1/abtests/{id}
- Update Test: PUT /api/v1/abtests/{id}
- Delete Test: DELETE /api/v1/abtests/{id}

## Visual Form Formats

### Create Test Form
+----------------------------------------------+
|            Create New A/B Test               |
+----------------------------------------------+
| Test Name:      [_______________________]     |
| Description:    [_______________________]     |
| Variation A:    [_______________________]     |
| Variation B:    [_______________________]     |
|                                              |
|        [Cancel]          [Create Test]         |
+----------------------------------------------+

### Edit Test Form
+----------------------------------------------+
|              Edit A/B Test                   |
+----------------------------------------------+
| Test Name:      [ prefilled text ]           |
| Description:    [ prefilled text ]           |
| Variation A:    [ prefilled text ]           |
| Variation B:    [ prefilled text ]           |
|                                              |
|        [Cancel]          [Save Changes]        |
+----------------------------------------------+

### Delete Test Confirmation
+----------------------------------------------+
|         Delete A/B Test Confirmation         |
+----------------------------------------------+
| Are you sure you want to delete this test?   |
| This action cannot be undone.                |
|                                              |
|        [Cancel]          [Delete Test]         |
+----------------------------------------------+

