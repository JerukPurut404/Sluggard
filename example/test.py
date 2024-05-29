from sluggard import Sluggard
csrf = "csrf_token"
cookie = "cookie_token"
client = Sluggard(csrf, cookie, "tenant")
user = client.view_assignment("assignedassignement_id")
for i in user.assignments:
  print(i.statusmessage_text)

# Shows the status message of the assignments

user = client.user_info('@user')
print(user)

# Shows the user info based on the input
# User(user-id, user-name, user-roles, https://avatar.on.simulise.cloud/user-id/avatar.jpg)