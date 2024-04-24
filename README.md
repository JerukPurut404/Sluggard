# Sluggard
Unofficial Python API wrapper for Simulise. Currently in the works

## What is Simulise?
Simulise is a tool that helps students develop their skills and track their progress using an online portfolio. It allows students and teachers to easily create assignments and showcase their work. Instead of grades, students earn badges for completing tasks. Schools can also use Simulise to identify important skills and track student progress in a clear way.


This API wrapper provides methods to interact with the Simulise GraphQL API. It allows you to perform operations such as searching for a school name, discovering user information, getting portfolio items, retrieving user information, and listening for unread notifications.

## Usage

To use Sluggard, you need to provide a CSRF token and cookies for authentication. Once initialized, you can call the following methods:

### `school_name_search(name)`

Search for a school name and return the results. Note that this can without the token and cookies

### `discover_user(user)`

Discover user information including user ID, username, primary role, active groups, and dashboard tiles.

### `get_portfolio_items(user)`

Retrieve portfolio items for a specific user including item ID, icon, title, link, creation date, and authors.

### `user_info(user_id)`

Get user information for a specific user ID including ID, name, about, avatar, username, primary role, rendered label, and impersonation capability.

### `unread_notification()`

Listen for unread notification changes and return the notification count.

## Example

Here is an example of how to use Sluggard:

```python
from Sluggard import Sluggard

# Initialize the API with CSRF token and cookies
api = Sluggard(csrf_token, cookies)
``` 

## How to get the CSRF and Cookie Token? 

1. Open the developer tools in your web browser by right-clicking on the webpage and selecting "Inspect" or pressing F12 once you are logged into your Simulise account.

2. Go to the "Network" tab in the developer tools to see all the network requests being made by the webpage.

3. Find the request from https://api.simulise.com/graphql and click on it to view the details.

4. Look for the "Headers" section in the request details. Here, you can find the values for the CSRF token and the cookie.

5. The CSRF token is usually found in a header called "X-CSRF-Token" or something similar. Copy the value of this token.

6. The cookie value is located in the "Cookie" header. Copy the value of the cookie. Get the "simulise_legacy_session_production" , "simulise_session_production" and "XSRF-TOKEN" values

